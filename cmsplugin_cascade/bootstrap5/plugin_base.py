import os

from django.template.loader import get_template, TemplateDoesNotExist
from django.utils.safestring import SafeText

from cms.models import Placeholder
from cms.plugin_base import CMSPluginBaseMetaclass, CMSPluginBase
from cms.utils.conf import get_cms_setting

from cmsplugin_cascade import app_settings
from cmsplugin_cascade.form_renderer import CascadeFormRenderer
from cmsplugin_cascade.models import CascadeElement
from cmsplugin_cascade.plugin_base import CascadePluginMixin, create_proxy_model

from formset.admin import ModelAdminMixin


class CascadePluginMetaclass(CMSPluginBaseMetaclass):

    def __new__(cls, name, bases, attrs):
        model_mixins = attrs.pop('model_mixins', ())
        attrs['model'] = create_proxy_model(name, model_mixins, CascadeElement, module=attrs.get('__module__'))
        return super().__new__(cls, name, bases, attrs)


class BootstrapPluginBase(CascadePluginMixin, ModelAdminMixin, CMSPluginBase, metaclass=CascadePluginMetaclass):
    change_form_template = 'admin/cmsplugin_cascade/formset/change_form.html'
    module = 'Bootstrap'
    require_parent = True
    allow_children = True
    render_template = 'cascade/generic/wrapper.html'
    form_renderer_class = CascadeFormRenderer

    class Media:
        css = {'all': ['formset/css/adminform.css', 'cascade/css/admin/adminform.css']}
        js = ['cascade/admin/bootstrap5/js/cascadeplugin.js']

    def get_render_template(self, context, instance, placeholder):
        render_template = getattr(self, 'render_template', None)
        if render_template and '{}' in render_template:
            try:
                # check if overridden template exists
                template = render_template.format(app_settings.CMSPLUGIN_CASCADE['bootstrap5']['template_basedir'])
                template = os.path.normpath(template)
                get_template(template)
                return template
            except (KeyError, TemplateDoesNotExist):
                template = render_template.format('')
                return os.path.normpath(template)
        return render_template

    @classmethod
    def get_breakpoints(cls, instance):
        """
        Return the list of applied breakpoints defined in the parent container.
        """
        if container := instance.get_ancestors_qs().filter(plugin_type='BootstrapContainerPlugin').last():
            instance, _ = container.get_plugin_instance()
            if isinstance(instance, CascadeElement):
                return instance.glossary.get('breakpoints', [])
        return []

    @classmethod
    def super(cls, klass, instance):
        """
        Plugins inheriting from CascadePluginBaseMetaclass can have two different base classes,
        :class:`cmsplugin_cascade.plugin_base.CMSPluginBase` and :class:`cmsplugin_cascade.strides.StridePluginBase`.
        Therefore, in order to call a method from an inherited class, use this "super" wrapping method.
        >>> cls.super(MyPlugin, self).a_method()
        """
        return super(klass, instance)

    @classmethod
    def get_identifier(cls, instance):
        """
        Hook to return a description for the current model.
        """
        return SafeText()

    @classmethod
    def sanitize_model(cls, instance):
        # TODO: probably not required anymore

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

    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        """
        We just need the popup interface here
        """
        context.update({
            'preview': 'no_preview' not in request.GET,
            'is_popup': True,
            'plugin': obj,
            'CMS_MEDIA_URL': get_cms_setting('MEDIA_URL'),
        })
        return super().render_change_form(request, context, add, change, form_url, obj)

    def render_success_response(self):
        add = 'plugin_type' in self.request.GET
        return self.render_close_frame(self.request, self.object, add)

    def _update_collection_view(self, view_kwargs):
        instance = view_kwargs['instance']
        if instance.pk is None:
            initial = view_kwargs['initial']
            instance.plugin_type = initial['plugin_type']
            instance.language = initial['plugin_language']
            instance.parent_id = initial.get('plugin_parent')
            instance.placeholder = Placeholder.objects.get(id=initial['placeholder_id'])
            instance.position = instance.placeholder.get_next_plugin_position(
                language=initial['plugin_language'],
                parent=instance.parent,
                insert_order='last',
            )
            instance.placeholder.add_plugin(instance)
        return super()._update_collection_view(view_kwargs)
