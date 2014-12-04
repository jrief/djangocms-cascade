# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.exceptions import ObjectDoesNotExist
from django.utils import six
from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from .models_base import CascadeModelBase
from .widgets import JSONMultiWidget


class CascadePluginBase(CMSPluginBase):
    tag_type = 'div'
    render_template = 'cms/plugins/generic.html'
    glossary_variables = []  # entries in glossary not handled by a form editor

    class Media:
        css = {'all': ('cascade/css/admin/partialfields.css', 'cascade/css/admin/editplugin.css',)}

    def _child_classes(self):
        """All registered plugins shall be allowed as children for this plugin"""
        if getattr(self, '_cached_child_classes', None) is not None:
            return self._cached_child_classes
        self._cached_child_classes = list(getattr(self, 'generic_child_classes', [])) or []
        for p in plugin_pool.get_all_plugins():
            if (isinstance(p.parent_classes, (list, tuple))
              and self.__class__.__name__ in p.parent_classes
              and p.__name__ not in self._cached_child_classes):
                self._cached_child_classes.append(p.__name__)
        return self._cached_child_classes
    child_classes = property(_child_classes)

    def __init__(self, model=None, admin_site=None, glossary_fields=None):
        super(CascadePluginBase, self).__init__(model, admin_site)
        if isinstance(glossary_fields, (list, tuple)):
            self.glossary_fields = glossary_fields
        elif not hasattr(self, 'glossary_fields'):
            self.glossary_fields = []

    @classmethod
    def get_identifier(cls, model):
        """
        Returns the descriptive name for the current model
        """
        return ''

    @classmethod
    def get_css_classes(cls, obj):
        """
        Returns a list of CSS classes to be added as class="..." to the current HTML tag.
        """
        css_classes = []
        if hasattr(cls, 'default_css_class'):
            css_classes.append(cls.default_css_class)
        for attr in getattr(cls, 'default_css_attributes', []):
            css_class = obj.glossary.get(attr)
            if isinstance(css_class, six.string_types):
                css_classes.append(css_class)
            elif isinstance(css_class, list):
                css_classes.extend(css_class)
        return css_classes

    @classmethod
    def get_inline_styles(cls, obj):
        """
        Returns a dictionary of CSS attributes to be added as style="..." to the current HTML tag.
        """
        inline_styles = getattr(cls, 'default_inline_styles', {})
        css_style = obj.glossary.get('inline_styles')
        if css_style:
            inline_styles.update(css_style)
        return inline_styles

    @classmethod
    def get_html_tag_attributes(cls, obj):
        """
        Returns a dictionary of attributes, which shall be added to the current HTML tag.
        This method normally is called by the models's property method ``html_tag_ attributes``,
        which enriches the HTML tag with those attributes converted to a list as
        ``attr1="val1" attr2="val2" ...``.
        """
        attributes = getattr(cls, 'html_tag_attributes', {})
        return dict((attr, obj.glossary.get(key, '')) for key, attr in attributes.items())

    @classmethod
    def sanitize_model(cls, obj):
        """
        This method is called, before the model is written to the database. It can be overloaded
        to sanitize the current models, in case a parent model changed in a way, which might
        affect this plugin.
        This method shall return ``True``, in case a model change was necessary, otherwise it shall
        return ``False`` to prevent a useless database update.
        """
        return False

    def extend_children(self, parent, wanted_children, child_class, child_glossary=None):
        """
        Extend the number of children so that the parent object contains wanted children.
        No child will be removed if wanted_children is smaller than the current number of children.
        """
        from cms.api import add_plugin
        current_children = parent.get_children().count()
        for _ in range(current_children, wanted_children):
            child = add_plugin(parent.placeholder, child_class, parent.language, target=parent)
            if isinstance(child_glossary, dict):
                child.glossary.update(child_glossary)
            child.save()

    def get_form(self, request, obj=None, **kwargs):
        """
        Build the form used for changing the model.
        """
        glossary_fields = kwargs.pop('glossary_fields', self.glossary_fields)
        kwargs.update(widgets={'glossary': JSONMultiWidget(glossary_fields)}, labels={'glossary': ''})
        form = super(CascadePluginBase, self).get_form(request, obj, **kwargs)
        # help_text can not be cleared using an empty string in modelform_factory
        form.base_fields['glossary'].help_text = ''
        for field in glossary_fields:
            form.base_fields['glossary'].validators.append(field.run_validators)
        setattr(form, 'glossary_fields', glossary_fields)
        return form

    def save_model(self, request, new_obj, form, change):
        if change and self.glossary_variables:
            old_obj = super(CascadePluginBase, self).get_object(request, form.instance.id)
            for key in self.glossary_variables:
                if key not in new_obj.glossary and key in old_obj.glossary:
                    # transfer listed glossary variable from the old to new object
                    new_obj.glossary[key] = old_obj.glossary[key]
        super(CascadePluginBase, self).save_model(request, new_obj, form, change)

    def get_parent_instance(self):
        """
        Get the parent model instance corresponding to this plugin. Returns None if the current
        plugin instance is the root model.
        """
        for model in CascadeModelBase._get_cascade_elements():
            try:
                return model.objects.get(id=self.parent.id)
            except ObjectDoesNotExist:
                pass
