from django.core.exceptions import ImproperlyConfigured
from django.forms.fields import BooleanField
from django.utils.translation import gettext_lazy as _
from django.template import engines

from entangled.forms import EntangledModelFormMixin


class HidePluginFormMixin(EntangledModelFormMixin):
    hide_plugin = BooleanField(
        label=_("Hide plugin"),
        required=False,
        help_text=_("Hide this plugin and all of it's children.")
    )

    class Meta:
        entangled_fields = {'glossary': ['hide_plugin']}


class HidePluginMixin:
    """
    This mixin class adds a checkbox to each named plugin, which if checked hides that
    plugin during the rendering phase.
    """
    suppress_template = engines['django'].from_string('')
    hiding_template_string = '''
{{% load cms_tags %}}
<div style="display: none;">
{{% for plugin in instance.child_plugin_instances %}}{{% render_plugin plugin %}}{{% endfor %}}
</div>
<style>
div.cms .cms-structure .cms-draggable-{plugin_id} .cms-dragitem {{
color: gray;
background-color: lightgray;
background-image: repeating-linear-gradient(-45deg, transparent, transparent 4px, rgba(255,255,255,.5) 4px, rgba(255,255,255,.5) 8px);
background-size: contain;
}}
</style>
'''

    def get_form(self, request, obj=None, **kwargs):
        form = kwargs.get('form', self.form)
        assert issubclass(form, EntangledModelFormMixin), "Form must inherit from EntangledModelFormMixin"
        kwargs['form'] = type(form.__name__, (HidePluginFormMixin, form), {})
        return super().get_form(request, obj, **kwargs)

    def get_render_template(self, context, instance, placeholder):
        if instance.glossary.get('hide_plugin'):
            if self.in_edit_mode(context['request'], placeholder):
                # in edit mode we actually must render the children, otherwise they won't show
                # up in Structure Mode
                template_string = self.hiding_template_string.format(plugin_id=instance.pk)
                return engines['django'].from_string(template_string)
            else:
                return self.suppress_template

        super_self = super(HidePluginMixin, self)
        if hasattr(super_self, 'get_render_template'):
            template = super_self.get_render_template(context, instance, placeholder)
        elif getattr(self, 'render_template', False):
            template = getattr(self, 'render_template', False)
        else:
            template = None
        if not template:
            raise ImproperlyConfigured("Plugin {} has no render_template.".format(self.__class__))
        return template
