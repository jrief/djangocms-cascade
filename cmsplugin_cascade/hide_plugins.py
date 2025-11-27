from django.core.exceptions import ImproperlyConfigured
from django.forms.fields import BooleanField
from django.template.loader import get_template
from django.template.loader_tags import BlockNode
from django.utils.translation import gettext_lazy as _
from django.template import engines

from entangled.forms import EntangledModelFormMixin


class HidePluginFormMixin(EntangledModelFormMixin):
    hide_plugin = BooleanField(
        label=_("Hide element"),
        required=False,
        help_text=_("Hide this element and all of it's descendants from the web-page.")
    )

    class Meta:
        entangled_fields = {'glossary': ['hide_plugin']}


class HidePluginMixin:
    """
    This mixin class adds a checkbox to each named plugin, that if checked, hides that
    plugin during the rendering phase.
    """

    # template string used to render the plugin in published mode
    suppress_template_string = '''{{% extends "{base_template}" %}}
{{% block always-visible %}}{{{{ block.super }}}}{{% endblock %}}
{{% block main-component %}}{{% endblock %}}
'''

    # template string used to render the plugin in edit mode
    hiding_template_string = '''{{% extends "{base_template}" %}}
{{% load cms_tags %}}
{{% block always-visible %}}{{{{ block.super }}}}{{% endblock %}}
{{% block main-component %}}
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
{{% endblock %}}
'''

    def get_form(self, request, obj=None, **kwargs):
        form = kwargs.get('form', self.form)
        assert issubclass(form, EntangledModelFormMixin), "Form must inherit from EntangledModelFormMixin"
        kwargs['form'] = type(form.__name__, (HidePluginFormMixin, form), {})
        return super().get_form(request, obj, **kwargs)

    def get_render_template(self, context, instance, placeholder):
        super_self = super(HidePluginMixin, self)
        if hasattr(super_self, 'get_render_template'):
            template_name = super_self.get_render_template(context, instance, placeholder)
        else:
            template_name = getattr(self, 'render_template', None)
        if not template_name:
            raise ImproperlyConfigured("Plugin {} has no attribute `render_template`.".format(self.__class__))

        if instance.glossary.get('hide_plugin'):
            for node in get_template(template_name).template.nodelist:
                if isinstance(node, BlockNode) and node.name == 'main-component':
                    break
            else:
                template_name = 'cascade/generic/hide_plugin.html'
            if self.in_edit_mode(context['request'], placeholder):
                # in edit mode we actually must render the children, otherwise they won't show
                # up in Structure Mode
                template_string = self.hiding_template_string.format(
                    base_template=template_name,
                    plugin_id=instance.pk,
                )
            else:
                template_string = self.suppress_template_string.format(base_template=template_name)
            return engines['django'].from_string(template_string)

        return template_name
