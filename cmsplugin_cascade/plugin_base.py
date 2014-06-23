# -*- coding: utf-8 -*-
import six
from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from .widgets import JSONMultiWidget


class CascadePluginBase(CMSPluginBase):
    tag_type = 'div'
    render_template = 'cms/plugins/generic.html'
    glossary_variables = []
    _cached_child_classes = None

    class Media:
        css = {'all': ('admin/css/djangocms-cascade.css',)}

    def _child_classes(self):
        """All registered plugins shall be allowed as children for this plugin"""
        if self._cached_child_classes is not None:
            return self._cached_child_classes
        self._cached_child_classes = list(getattr(self, 'generic_child_classes', [])) or []
        for p in plugin_pool.get_all_plugins():
            if isinstance(p.parent_classes, (list, tuple)) and self.__class__.__name__ in p.parent_classes \
                and p.__name__ not in self._cached_child_classes:
                self._cached_child_classes.append(p.__name__)
        return self._cached_child_classes
    child_classes = property(_child_classes)

    def __init__(self, model=None, admin_site=None, glossary_fields=None):
        super(CascadePluginBase, self).__init__(model, admin_site)
        if glossary_fields:
            self.glossary_fields = glossary_fields
        elif not hasattr(self, 'glossary_fields'):
            self.glossary_fields = []

    @classmethod
    def get_identifier(cls, model):
        """
        Returns the descriptive name for the current model
        """
        return six.u('')

    @classmethod
    def get_css_classes(cls, obj):
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
        inline_styles = getattr(cls, 'default_inline_styles', {})
        css_style = obj.glossary.get('inline_styles')
        if css_style:
            inline_styles.update(css_style)
        return inline_styles

    @classmethod
    def get_data_options(cls, obj):
        data_options = getattr(cls, 'default_data_options', {})
        instance_options = obj.glossary.get('data_options')
        if instance_options:
            data_options.update(instance_options)
        return data_options

    def get_object(self, request, object_id):
        """
        Get the object and enrich the glossary with the number of children.
        """
        obj = super(CascadePluginBase, self).get_object(request, object_id)
        try:
            obj.glossary['-num-children-'] = obj.get_children().count()
        except AttributeError:
            pass
        return obj

    @classmethod
    def sanizite_model(cls, obj):
        """
        This method is called, before the model is written to the database. It can be overloaded
        to sanitize your own models. This method shall return True, in case it sanitized the model.
        Otherwise it shall return False to prevent a useless update in the database.
        """
        try:
            del obj.glossary['-num-children-']
            return True
        except (TypeError, KeyError):
            return False

    def extend_children(self, parent, wanted_children, child_class, child_glossary=None):
        """
        Extend the number of children so that the parent object contains wanted children. No child
        will be removed.
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
        kwargs.update(widgets={'glossary': JSONMultiWidget(self.glossary_fields)}, labels={'glossary': ''})
        form = super(CascadePluginBase, self).get_form(request, obj, **kwargs)
        # help_text can not be cleared using an empty string in modelform_factory
        form.base_fields['glossary'].help_text = ''
        for field in self.glossary_fields:
            form.base_fields['glossary'].validators.append(field.run_validators)
        setattr(form, 'glossary_fields', self.glossary_fields)
        return form

    def save_model(self, request, new_obj, form, change):
        if self.glossary_variables:
            old_obj = super(CascadePluginBase, self).get_object(request, form.instance.id)
            for key in self.glossary_variables:
                if key not in new_obj.glossary:
                    # transfer listed glossary variable from the old to new object
                    new_obj.glossary.update(key=old_obj.glossary.get(key))
        super(CascadePluginBase, self).save_model(request, new_obj, form, change)
