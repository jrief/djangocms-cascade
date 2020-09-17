from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from cms.plugin_pool import plugin_pool

from cmsplugin_cascade import app_settings
from cmsplugin_cascade.plugin_base import CascadePluginBase, TransparentContainer


class CustomSnippetPlugin(TransparentContainer, CascadePluginBase):
    """
    Allows to add a customized template anywhere. This plugins will be registered only if the
    project added a template using the configuration setting 'plugins_with_extra_render_templates'.
    """
    name = _("Custom Snippet")
    require_parent = False
    allow_children = True
    alien_child_classes = True
    render_template_choices = dict(app_settings.CMSPLUGIN_CASCADE['plugins_with_extra_render_templates'].get('CustomSnippetPlugin', ()))
    render_template = 'cascade/generic/does_not_exist.html'  # default in case the template could not be found

    @classmethod
    def get_identifier(cls, instance):
        render_template = instance.glossary.get('render_template')
        if render_template:
            return format_html('{}', cls.render_template_choices.get(render_template))


if CustomSnippetPlugin.render_template_choices:
    # register only, if at least one template has been defined
    plugin_pool.register_plugin(CustomSnippetPlugin)
