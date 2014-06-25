# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import mark_safe, format_html_join
from jsonfield.fields import JSONField
from cms.models import CMSPlugin
from cms.plugin_pool import plugin_pool


class CascadeModelBase(CMSPlugin):
    """
    The container to hold additional bootstrap elements.
    """
    class Meta:
        abstract = True

    cmsplugin_ptr = models.OneToOneField(CMSPlugin, related_name='+', parent_link=True)
    glossary = JSONField(null=True, blank=True, default={})

    def __unicode__(self):
        return self.plugin_class.get_identifier(self)

    @property
    def plugin_class(self):
        if not hasattr(self, '_plugin_class'):
            self._plugin_class = self.get_plugin_class()
        return self._plugin_class

    @property
    def tag_type(self):
        return self.plugin_class.tag_type

    @property
    def css_classes(self):
        css_classes = self.plugin_class.get_css_classes(self)
        return mark_safe(' '.join(css_classes))

    @property
    def inline_styles(self):
        inline_styles = self.plugin_class.get_inline_styles(self)
        return format_html_join(' ', '{0}: {1};', (s for s in inline_styles.items() if s[1]))

    @property
    def html_attributes(self):
        html_attributes = self.plugin_class.get_html_attributes(self)
        return format_html_join(' ', '{0}="{1}"',
                                ((attr, val) for attr, val in html_attributes.items() if val))

    def get_parent(self):
        """
        Get the parent model. Returns None if current element is the root element.
        """
        if self.parent_id:
            for model in CascadeModelBase._get_cascade_elements():
                try:
                    return model.objects.get(id=self.parent_id)
                except ObjectDoesNotExist:
                    pass

    def get_complete_glossary(self):
        """
        Return the parent glossary for this model object merged with the current object.
        This is done by starting from the root element down to the current element and enriching
        the glossary with each models's own glossary.
        """
        parent = self.get_parent()
        if parent:
            complete_glossary = parent.get_complete_glossary()
        else:
            complete_glossary = {}
        complete_glossary.update(self.glossary or {})
        return complete_glossary

    def sanitize_children(self):
        """
        Recursively walk down the plugin tree and invoke method ``save(sanitize_only=True)`` for
        each child.
        """
        for model in CascadeModelBase._get_cascade_elements():
            for child in model.objects.filter(parent_id=self.id):
                child.save(sanitize_only=True)
                child.sanitize_children()

    def save(self, sanitize_only=False, *args, **kwargs):
        """
        A hook which let the plugin instance sanitize to current object model while saving it.
        With ``sanitize_only=True``, the current model object only is saved when the method
        ``sanitize_model()`` from the corresponding plugin actually changed the glossary.
        """
        sanitized = self.plugin_class.sanitize_model(self)
        if sanitize_only:
            if sanitized:
                super(CascadeModelBase, self).save(no_signals=True)
        else:
            super(CascadeModelBase, self).save(*args, **kwargs)

    @classmethod
    def _get_cascade_elements(cls):
        """
        Returns a set of models which are derived from CascadeModelBase. This set shall be used
        for traversing the plugin tree, since children can be interconnected using different
        plugins.
        """
        if not hasattr(cls, '_cached_cascade_elements'):
            cce = set([p.model for p in plugin_pool.get_all_plugins() if issubclass(p.model, cls)])
            setattr(cls, '_cached_cascade_elements', cce)
        return cls._cached_cascade_elements
