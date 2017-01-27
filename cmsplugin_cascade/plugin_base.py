# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict
from distutils.version import LooseVersion

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.forms import MediaDefiningClass
from django.utils import six
from django.utils.functional import lazy
from django.utils.module_loading import import_string
from django.utils.translation import string_concat
from django.utils.safestring import SafeText, mark_safe

from cms import __version__ as cms_version
from cms.plugin_base import CMSPluginBaseMetaclass, CMSPluginBase
from cms.utils.compat.dj import is_installed

from . import settings
from .fields import GlossaryField
from .models_base import CascadeModelBase
from .models import CascadeElement, SharableCascadeElement
from .generic.mixins import SectionMixin, SectionModelMixin
from .sharable.forms import SharableGlossaryMixin
from .extra_fields.mixins import ExtraFieldsMixin
from .widgets import JSONMultiWidget
from .hide_plugins import HidePluginMixin
from .render_template import RenderTemplateMixin
from .utils import remove_duplicates

mark_safe_lazy = lazy(mark_safe, six.text_type)

fake_proxy_models = {}


def create_proxy_model(name, model_mixins, base_model, attrs=None, module=None):
    """
    Create a Django Proxy Model on the fly, to be used by any Cascade Plugin.
    """
    class Meta:
        proxy = True
        app_label = 'cmsplugin_cascade'

    name = str(name + 'Model')
    bases = model_mixins + (base_model,)
    attrs = dict(attrs or {}, Meta=Meta, __module__=module)
    Model = type(name, bases, attrs)
    fake_proxy_models[name] = bases
    return Model


class CascadePluginMixinMetaclass(MediaDefiningClass):
    ring_plugin_bases = {}

    def __new__(cls, name, bases, attrs):
        cls.build_glossary_fields(bases, attrs)
        ring_plugin = attrs.get('ring_plugin')
        if ring_plugin:
            ring_plugin_bases = [b.ring_plugin for b in bases
                                 if hasattr(b, 'ring_plugin') and b.ring_plugin != ring_plugin]

            # remember the dependencies
            cls.ring_plugin_bases.setdefault(ring_plugin, [])
            cls.ring_plugin_bases[ring_plugin].extend(ring_plugin_bases)
            cls.ring_plugin_bases[ring_plugin] = remove_duplicates(cls.ring_plugin_bases[ring_plugin])

        new_class = super(CascadePluginMixinMetaclass, cls).__new__(cls, name, bases, attrs)
        return new_class

    @classmethod
    def build_glossary_fields(cls, bases, attrs):
        # collect glossary fields from all base classes
        base_glossary_fields = []
        for base_class in bases:
            base_glossary_fields.extend(getattr(base_class, 'glossary_fields', []))

        # collect declared glossary fields from current class
        declared_glossary_fields = []
        for field_name in list(attrs.keys()):
            if isinstance(attrs[field_name], GlossaryField):
                field = attrs.pop(field_name)
                field.name = field_name
                declared_glossary_fields.append(field)

        if 'glossary_fields' in attrs:
            if declared_glossary_fields:
                msg = "Can not mix 'glossary_fields' with declared atributes of type 'GlossaryField'"
                raise ImproperlyConfigured(msg)
            declared_glossary_fields = list(attrs['glossary_fields'])

        if 'glossary_field_order' in attrs:
            # if reordering is desired, reorder the glossary fields
            unordered_fields = dict((gf.name, gf) for gf in base_glossary_fields)
            for gf in declared_glossary_fields:
                unordered_fields.update({gf.name: gf})
            unordered_fields.update(dict((gf.name, gf) for gf in declared_glossary_fields))
            glossary_fields = OrderedDict((k, unordered_fields[k])
                                          for k in attrs['glossary_field_order'] if k in unordered_fields)
        else:
            # merge glossary fields from base classes with the declared ones, overwriting the former ones
            glossary_fields = OrderedDict((gf.name, gf) for gf in base_glossary_fields)
            for gf in declared_glossary_fields:
                glossary_fields.update({gf.name: gf})

        if glossary_fields:
            attrs['glossary_fields'] = glossary_fields.values()


class CascadePluginMixinBase(six.with_metaclass(CascadePluginMixinMetaclass)):
    """
    Use this as a base for mixin classes used by other CascadePlugins
    """


class CascadePluginBaseMetaclass(CascadePluginMixinMetaclass, CMSPluginBaseMetaclass):
    """
    All plugins from djangocms-cascade can be instantiated in different ways. In order to allow this
    by a user defined configuration, this meta-class conditionally inherits from additional mixin
    classes.
    """
    plugins_with_extra_fields = dict(settings.CMSPLUGIN_CASCADE['plugins_with_extra_fields'])
    plugins_with_bookmark = list(settings.CMSPLUGIN_CASCADE['plugins_with_bookmark'])
    plugins_with_sharables = dict(settings.CMSPLUGIN_CASCADE['plugins_with_sharables'])
    plugins_with_extra_render_templates = settings.CMSPLUGIN_CASCADE['plugins_with_extra_render_templates'].keys()
    allow_plugin_hiding = settings.CMSPLUGIN_CASCADE['allow_plugin_hiding']
    exclude_hiding_plugin = list(settings.CMSPLUGIN_CASCADE['exclude_hiding_plugin'])

    def __new__(cls, name, bases, attrs):
        model_mixins = attrs.pop('model_mixins', ())
        if (cls.allow_plugin_hiding and name not in cls.exclude_hiding_plugin and 'name' in attrs and
            not attrs.get('text_enabled')):
            bases = (HidePluginMixin,) + bases
        if name in cls.plugins_with_extra_fields:
            bases = (ExtraFieldsMixin,) + bases
        if name in cls.plugins_with_bookmark:
            bases = (SectionMixin,) + bases
            model_mixins = (SectionModelMixin,) + model_mixins
        if name in cls.plugins_with_sharables:
            bases = (SharableGlossaryMixin,) + bases
            attrs['fields'] = list(attrs.get('fields', ['glossary']))
            attrs['fields'].extend([('save_shared_glossary', 'save_as_identifier'), 'shared_glossary'])
            attrs['sharable_fields'] = cls.plugins_with_sharables[name]
            base_model = SharableCascadeElement
        else:
            attrs['exclude'] = list(attrs.get('exclude', []))
            attrs['exclude'].append('shared_glossary')
            base_model = CascadeElement
        if name in cls.plugins_with_extra_render_templates:
            bases = (RenderTemplateMixin,) + bases
        if name == 'SegmentPlugin':
            # SegmentPlugin shall additionally inherit from configured mixin classes
            model_mixins += tuple(import_string(mc[0]) for mc in settings.CMSPLUGIN_CASCADE['segmentation_mixins'])
        module = attrs.get('__module__')
        attrs['model'] = create_proxy_model(name, model_mixins, base_model, module=module)
        if is_installed('reversion'):
            import reversion.revisions
            if not reversion.revisions.is_registered(base_model):
                reversion.revisions.register(base_model)
        # handle ambiguous plugin names by appending a symbol
        if 'name' in attrs and settings.CMSPLUGIN_CASCADE['plugin_prefix']:
            attrs['name'] = mark_safe_lazy(string_concat(
                settings.CMSPLUGIN_CASCADE['plugin_prefix'], "&nbsp;", attrs['name']))

        return super(CascadePluginBaseMetaclass, cls).__new__(cls, name, bases, attrs)


class TransparentWrapper(object):
    """
    Add this mixin class to other Cascade plugins, wishing to be added transparently between other
    plugins restricting parent-children relationships.
    For instance: A BootstrapColumnPlugin can only be added as a child to a RowPlugin. This means
    that no other wrapper can be added between those two plugins. By adding this mixin class we can
    allow any plugin to behave transparently, just as if it would not have be inserted into the DOM
    tree. When moving plugins in- and out of transparent wrapper plugins, always reload the page, so
    that the parent-children relationships can be updated.
    """
    child_plugins_cache = False
    parent_plugins_cache = False

    @classmethod
    def get_child_classes(cls, slot, page, instance=None):
        if hasattr(cls, 'direct_child_classes'):
            return cls.direct_child_classes
        while True:
            instance = instance.get_parent_instance()
            if instance is None:
                return super(TransparentWrapper, cls).get_child_classes(slot, page, instance)
            if not issubclass(instance.plugin_class, TransparentWrapper):
                return instance.plugin_class.get_child_classes(slot, page, instance)

    @classmethod
    def get_parent_classes(cls, slot, page, instance=None):
        if hasattr(cls, 'direct_parent_classes'):
            return cls.direct_parent_classes
        parent_classes = set(super(TransparentWrapper, cls).get_parent_classes(slot, page, instance) or [])
        if isinstance(instance, CascadeElement):
            instance = instance.get_parent_instance()
            if instance is not None:
                parent_classes.add(instance.plugin_type)
        return list(parent_classes)


class TransparentContainer(TransparentWrapper):
    """
    This mixin class marks each plugin inheriting from it, as a transparent container.
    Such a plugin is added to the global list of entitled parent plugins, which is required if we
    want to place and move all other Cascade plugins below this container.

    Often, transparent wrapping classes come in pairs. For instance the `AccordionPlugin` containing
    one or more `PanelPlugin`. Here the `AccordionPlugin` must inherit from `TransparentWrapper`,
    whereas the `AccordionPlugin` must inherit from the `TransparentContainer`.
    """
    @staticmethod
    def get_plugins():
        from cms.plugin_pool import plugin_pool
        global _leaf_transparent_plugins

        try:
            return _leaf_transparent_plugins
        except NameError:
            _leaf_transparent_plugins = [
                plugin.__name__ for plugin in plugin_pool.get_all_plugins()
                    if issubclass(plugin, TransparentContainer)
            ]
            return _leaf_transparent_plugins


class CascadePluginBase(six.with_metaclass(CascadePluginBaseMetaclass, CMSPluginBase)):
    change_form_template = 'cascade/admin/change_form.html'
    glossary_variables = []  # entries in glossary not handled by a form editor
    model_mixins = ()  # model mixins added to the final Django model
    parent_classes = None
    alien_child_classes = False

    class Media:
        css = {'all': ['cascade/css/admin/partialfields.css', 'cascade/css/admin/editplugin.css']}
        js = ['cascade/js/underscore.js', 'cascade/js/ring.js']

    def __init__(self, model=None, admin_site=None, glossary_fields=None):
        super(CascadePluginBase, self).__init__(model, admin_site)
        if isinstance(glossary_fields, (list, tuple)):
            self.glossary_fields = list(glossary_fields)
        elif not hasattr(self, 'glossary_fields'):
            self.glossary_fields = []

    @classmethod
    def _get_parent_classes_transparent(cls, slot, page, instance=None):
        """
        Return all parent classes including those marked as "transparent".
        """
        parent_classes = super(CascadePluginBase, cls).get_parent_classes(slot, page, instance)
        if parent_classes is None:
            if cls.get_require_parent(slot, page) is False:
                return
            parent_classes = []

        # add all plugins marked as 'transparent', since they all are potential parents
        parent_classes = set(parent_classes)
        parent_classes.update(TransparentContainer.get_plugins())
        return list(parent_classes)

    @classmethod
    def get_child_classes(cls, slot, page, instance=None):
        plugin_type = cls.__name__
        child_classes = set()
        for child_class in cls.get_child_plugin_candidates(slot, page):
            if issubclass(child_class, CascadePluginBase):
                own_child_classes = getattr(cls, 'child_classes', None) or []
                child_parent_classes = child_class._get_parent_classes_transparent(slot, page, instance)
                if isinstance(child_parent_classes, (list, tuple)) and plugin_type in child_parent_classes:
                    child_classes.add(child_class)
                elif plugin_type in own_child_classes:
                    child_classes.add(child_class)
                elif child_parent_classes is None:
                    child_classes.add(child_class)
            else:
                if cls.alien_child_classes and child_class.__name__ in settings.CMSPLUGIN_CASCADE['alien_plugins']:
                    child_classes.add(child_class)

        return list(cc.__name__ for cc in child_classes)

    @classmethod
    def get_parent_classes(cls, slot, page, instance=None):
        return cls._get_parent_classes_transparent(slot, page, instance)

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

    @classmethod
    def get_data_representation(cls, instance):
        """
        Return a representation of the given instance suitable for a serialized representation.
        """
        return {'glossary': instance.glossary}

    @classmethod
    def add_inline_elements(cls, instance, inlines):
        """
        Hook to create (sortable) inline elements for the given instance.
        """

    @classmethod
    def add_shared_reference(cls, instance, shared_glossary):
        """
        Hook to add a reference pointing onto an existing SharedGlossary instance.
        """

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
        if request.method == 'POST':
            is_shared = bool(request.POST.get('shared_glossary'))
            for field in glossary_fields:
                if not (is_shared and field.name in self.sharable_fields):
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

    def get_parent_instance(self, request=None, obj=None):
        """
        Get the parent model instance corresponding to this plugin. When adding a new plugin, the
        parent might not be available. Therefore as fallback, pass in the request object.
        """
        try:
            parent_id = obj.parent_id
        except AttributeError:
            try:
                # TODO: self.parent presumably is not used anymore in CMS-3.4, because it doesn't
                # make sense anyway, since the plugin instances shall know their parents, not the
                # plugins.
                parent_id = self.parent.id
            except AttributeError:
                if request:
                    parent_id = request.GET.get('plugin_parent', None)
                    if parent_id is None:
                        from cms.models import CMSPlugin
                        try:
                            parent_id = CMSPlugin.objects.filter(id=request.resolver_match.args[0]
                                                                 ).only("parent_id").order_by('?').first().parent_id
                        except (AttributeError, IndexError):
                            parent_id = None
                else:
                    parent_id = None
        for model in CascadeModelBase._get_cascade_elements():
            try:
                return model.objects.get(id=parent_id)
            except model.DoesNotExist:
                continue

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
        ring_plugin_bases = dict((ring_plugin, ['django.cascade.{}'.format(b) for b in bases])
                                 for ring_plugin, bases in CascadePluginMixinMetaclass.ring_plugin_bases.items())
        context.update(
            ring_plugin_bases=ring_plugin_bases,
            plugin_title=string_concat(self.module, " ", self.name, " Plugin"),
            plugin_intro=mark_safe(getattr(self, 'intro_html', '')),
            plugin_footnote=mark_safe(getattr(self, 'footnote_html', '')),
        )
        if hasattr(self, 'ring_plugin'):
            context.update(
                ring_plugin=self.ring_plugin,
            )

        # remove glossary field from rendered form
        form = context['adminform'].form
        try:
            fields = list(form.fields)
            fields.remove('glossary')
            context['empty_form'] = len(fields) + len(form.glossary_fields) == 0
        except KeyError:
            pass
        return super(CascadePluginBase, self).render_change_form(request, context, add, change, form_url, obj)

    def in_edit_mode(self, request, placeholder):
        """
        Returns True, if the plugin is in "edit mode".
        """
        toolbar = getattr(request, 'toolbar', None)
        edit_mode = getattr(toolbar, 'edit_mode', False) and getattr(placeholder, 'is_editable', True)
        if edit_mode:
            if LooseVersion(cms_version) < LooseVersion('3.4.0'):
                edit_mode = placeholder.has_change_permission(request)
            else:
                edit_mode = placeholder.has_change_permission(request.user)
        return edit_mode
