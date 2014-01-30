from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from jsonfield.fields import JSONField
from cms.models import CMSPlugin


class BootstrapElement(CMSPlugin):
    """
    The container to hold additional bootstrap elements.
    """
    cmsplugin_ptr = models.OneToOneField(CMSPlugin, related_name='+', parent_link=True)
    context = JSONField(null=True, blank=True, default={})

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
        return u' '.join(css_classes)

    @property
    def inline_styles(self):
        inline_styles = self.plugin_class.get_inline_styles(self)
        return u' '.join(['{0}: {1};'.format(*s) for s in inline_styles.items() if s[1]])

    @property
    def data_options(self):
        try:
            return u' '.join(['data-{0}={1}'.format(*s) for s in self.options.items() if s[1]])
        except (IndexError, AttributeError):
            pass
        return ''

    def get_full_context(self):
        """
        Return the context recursively, from the root element down to the current element.
        """
        context = {}
        try:
            parent = BootstrapElement.objects.get(id=self.parent_id)
            context = parent.get_full_context()
        except ObjectDoesNotExist:
            pass
        context.update(self.context or {})
        return context
