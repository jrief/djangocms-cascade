# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.forms.widgets import media_property
from django.utils import six
from django.utils.functional import lazy
from django.utils.module_loading import import_string
from django.utils.translation import string_concat
from django.utils.safestring import SafeText, mark_safe
from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBaseMetaclass, CMSPluginBase
from cms.utils.placeholder import get_placeholder_conf
from cms.utils.compat.dj import is_installed
from . import settings
from .models_base import CascadeModelBase
from .models import CascadeElement, SharableCascadeElement
from .sharable.forms import SharableGlossaryMixin
from .extra_fields.mixins import ExtraFieldsMixin
from .widgets import JSONMultiWidget
from .render_template import RenderTemplateMixin


def create_proxy_model(name, app_label, model_mixins, base_model, attrs={}, module=None):
    """
    Create a Django Proxy Model on the fly, to be used by any Cascade Plugin.
    """
    _app_label = app_label
    class Meta:
        proxy = True
        app_label = _app_label

    name = str(name + 'Model')
    bases = model_mixins + (base_model,)
    attrs.update({'Meta': Meta, '__module__': module})
    model = type(name, bases, attrs)
    return model

mark_safe_lazy = lazy(mark_safe, six.text_type)


class CascadePluginBaseMetaclass(CMSPluginBaseMetaclass):
    """
    All plugins from djangocms-cascade can be instantiated in different ways. In order to allow this
    by a user defined configuration, this meta-class conditionally inherits from additional mixin
    classes.
    """
    plugins_with_extra_fields = list(settings.CMSPLUGIN_CASCADE['plugins_with_extra_fields'])
    plugins_with_sharables = dict(settings.CMSPLUGIN_CASCADE['plugins_with_sharables'])

    def __new__(cls, name, bases, attrs):
        if name in cls.plugins_with_extra_fields:
            ExtraFieldsMixin.media = media_property(ExtraFieldsMixin)
            bases = (ExtraFieldsMixin,) + bases
        if name in cls.plugins_with_sharables:
            SharableGlossaryMixin.media = media_property(SharableGlossaryMixin)
            bases = (SharableGlossaryMixin,) + bases
            attrs['fields'] += (('save_shared_glossary', 'save_as_identifier'), 'shared_glossary',)
            attrs['sharable_fields'] = cls.plugins_with_sharables[name]
            base_model = SharableCascadeElement
        else:
            base_model = CascadeElement
        if name in settings.CMSPLUGIN_CASCADE['plugins_with_extra_render_templates'].keys():
            RenderTemplateMixin.media = media_property(RenderTemplateMixin)
            bases = (RenderTemplateMixin,) + bases
        model_mixins = attrs.pop('model_mixins', ())
        if name == 'SegmentPlugin':
            # SegmentPlugin shall additionally inherit from configured mixin classes
            model_mixins += tuple(import_string(mc[0]) for mc in settings.CMSPLUGIN_CASCADE['segmentation_mixins'])
        module = attrs.get('__module__')
        app_label = attrs.get('app_label', module.split('.')[0])
        attrs['model'] = create_proxy_model(name, app_label, model_mixins, base_model, module=module)
        if is_installed('reversion'):
            from reversion import VERSION as reversion_VERSION
            if reversion_VERSION < (1, 10):
                import reversion
            else:
                from reversion import revisions as reversion
            if not reversion.is_registered(base_model):
                reversion.register(base_model)
        # handle ambiguous plugin names by appending a symbol
        if 'name' in attrs and settings.CMSPLUGIN_CASCADE['plugin_prefix']:
            attrs['name'] = mark_safe_lazy(string_concat(
                settings.CMSPLUGIN_CASCADE['plugin_prefix'], "&nbsp;", attrs['name']))
        return super(CascadePluginBaseMetaclass, cls).__new__(cls, name, bases, attrs)


class CascadePluginBase(six.with_metaclass(CascadePluginBaseMetaclass, CMSPluginBase)):
    change_form_template = 'cascade/admin/change_form.html'
    glossary_variables = []  # entries in glossary not handled by a form editor
    model_mixins = ()  # model mixins added to the final Django model
    alien_child_classes = False

    class Media:
        css = {'all': ('cascade/css/admin/partialfields.css', 'cascade/css/admin/editplugin.css',)}

    def __init__(self, model=None, admin_site=None, glossary_fields=None):
        super(CascadePluginBase, self).__init__(model, admin_site)
        if isinstance(glossary_fields, (list, tuple)):
            self.glossary_fields = list(glossary_fields)
        elif not hasattr(self, 'glossary_fields'):
            self.glossary_fields = []

    def get_parent_classes(self, slot, page):
        template = page and page.get_template() or None
        ph_conf = get_placeholder_conf('parent_classes', slot, template, default={})
        parent_classes = ph_conf.get(self.__class__.__name__, self.parent_classes)
        if parent_classes is None:
            return
        return tuple(parent_classes)

    def get_child_classes(self, slot, page):
        if isinstance(self.child_classes, (list, tuple)):
            return self.child_classes
        # otherwise determine child_classes by evaluating parent_classes from other plugins
        child_classes = set()
        for p in plugin_pool.get_all_plugins():
            if (isinstance(p.parent_classes, (list, tuple)) and self.__class__.__name__ in p.parent_classes or
              p.parent_classes is None and issubclass(p, CascadePluginBase) or
              isinstance(self.alien_child_classes, (list, tuple)) and p.__name__ in self.alien_child_classes or
              self.alien_child_classes is True and p.__name__ in settings.CMSPLUGIN_CASCADE['alien_plugins']):
                child_classes.add(p.__name__)
        return tuple(child_classes)

    @classmethod
    def get_identifier(cls, instance):
        """
        Hook to return a description for the current model.
        """
        return SafeText()

    @classmethod
    def get_tag_type(self, instance):
        """
        Return the tag_type used to render this plugin.
        """
        return instance.glossary.get('tag_type', getattr(self, 'tag_type', 'div'))

    @classmethod
    def get_css_classes(cls, instance):
        """
        Returns a list of CSS classes to be added as class="..." to the current HTML tag.
        """
        css_classes = []
        if hasattr(cls, 'default_css_class'):
            css_classes.append(cls.default_css_class)
        for attr in getattr(cls, 'default_css_attributes', []):
            css_class = instance.glossary.get(attr)
            if isinstance(css_class, six.string_types):
                css_classes.append(css_class)
            elif isinstance(css_class, list):
                css_classes.extend(css_class)
        return css_classes

    @classmethod
    def get_inline_styles(cls, instance):
        """
        Returns a dictionary of CSS attributes to be added as style="..." to the current HTML tag.
        """
        inline_styles = getattr(cls, 'default_inline_styles', {})
        css_style = instance.glossary.get('inline_styles')
        if css_style:
            inline_styles.update(css_style)
        return inline_styles

    @classmethod
    def get_html_tag_attributes(cls, instance):
        """
        Returns a dictionary of attributes, which shall be added to the current HTML tag.
        This method normally is called by the models's property method ``html_tag_ attributes``,
        which enriches the HTML tag with those attributes converted to a list as
        ``attr1="val1" attr2="val2" ...``.
        """
        attributes = getattr(cls, 'html_tag_attributes', {})
        return dict((attr, instance.glossary.get(key, '')) for key, attr in attributes.items())

    @classmethod
    def sanitize_model(cls, instance):
        """
        This method is called, before the model is written to the database. It can be overloaded
        to sanitize the current models, in case a parent model changed in a way, which might
        affect this plugin.
        This method shall return `True`, in case a model change was necessary, otherwise it shall
        return `False` to prevent a useless database update.
        """
        if instance.glossary is None:
            instance.glossary = {}
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
        widgets = kwargs.pop('widgets', {})
        labels = kwargs.pop('labels', {})
        glossary_fields = kwargs.pop('glossary_fields', self.glossary_fields)
        widgets.update(glossary=JSONMultiWidget(glossary_fields))
        labels.update(glossary='')
        kwargs.update(widgets=widgets, labels=labels)
        form = super(CascadePluginBase, self).get_form(request, obj, **kwargs)
        # help_text can not be cleared using an empty string in modelform_factory
        form.base_fields['glossary'].help_text = ''
        for field in glossary_fields:
            form.base_fields['glossary'].validators.append(field.run_validators)
        form.glossary_fields = glossary_fields
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
            except (AttributeError, ObjectDoesNotExist):
                pass

    def get_previous_instance(self, obj):
        """
        Return the previous instance pair for the current node.
        This differs from get_previous_sibling() which returns an instance of the same kind.
        """
        try:
            if obj and obj.parent and obj.position > 0:
                previnst = obj.parent.get_children().order_by('position')[obj.position - 1]
                return previnst.get_plugin_instance()
        except ObjectDoesNotExist:
            pass
        return None, None

    def get_next_instance(self, obj):
        """
        Return the next instance pair for the current node.
        This differs from get_previous_sibling() which returns an instance of the same kind.
        """
        try:
            if obj and obj.parent:
                nextinst = obj.parent.get_children().order_by('position')[obj.position + 1]
                return nextinst.get_plugin_instance()
        except (IndexError, ObjectDoesNotExist):
            pass
        return None, None

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # determined dependencies for ring.js
        bases = self.get_ring_bases()
        context['base_plugins'] = ['django.cascade.{}'.format(b) for b in bases]

        # remove glossary field from rendered form
        try:
            fields = list(context['adminform'].form.fields)
            fields.remove('glossary')
            context['empty_form'] = len(fields) + len(context['adminform'].form.glossary_fields) == 0
        except KeyError:
            pass
        return super(CascadePluginBase, self).render_change_form(request, context, add, change, form_url, obj)

    def get_ring_bases(self):
        """
        Hook to return a list of base plugins required to build the JavaScript counterpart for the
        current plugin. The named JavaScript plugin must have been created using ``ring.create``.
        """
        return []
