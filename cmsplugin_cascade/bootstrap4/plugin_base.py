import os
from django.template.loader import get_template, TemplateDoesNotExist
from cmsplugin_cascade import app_settings
from cmsplugin_cascade.plugin_base import CascadePluginBase


class BootstrapPluginBase(CascadePluginBase):
    module = 'Bootstrap'
    require_parent = True
    allow_children = True
    render_template = 'cascade/generic/wrapper.html'

    def get_render_template(self, context, instance, placeholder):
        render_template = getattr(self, 'render_template', None)
        if render_template and '{}' in render_template:
            try:
                # check if overridden template exists
                template = render_template.format(app_settings.CMSPLUGIN_CASCADE['bootstrap4']['template_basedir'])
                template = os.path.normpath(template)
                get_template(template)
                return template
            except (KeyError, TemplateDoesNotExist):
                template = render_template.format('')
                return os.path.normpath(template)
        return render_template
