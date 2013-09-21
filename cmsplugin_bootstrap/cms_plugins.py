from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from django.utils.translation import ugettext_lazy as _
from cmsplugin_bootstrap.models import BootstrapElement


class BootstrapPluginBase(CMSPluginBase):
    module = 'Bootstrap'
    model = BootstrapElement
    allow_children = True

    fieldsets = (
        (None, {
            'fields': ('tag_type', 'class_name')
        }),
        (_('Advanced Settings'), {
            'classes': ('collapse',),
            'fields': ('extra_classes', 'extra_styles',),
        }),
    )

    def save_model(self, request, obj, form, change):
        print 'obj', obj
        obj.tag_type = self.tag_type
        obj.css_class = self.css_class
        return super(ButtonWrapperPlugin, self).save_model(request, obj, form, change)


class ButtonWrapperPlugin(BootstrapPluginBase):
    name = _("Button wrapper")
    render_template = "cms/plugins/bootstrap/naked.html"
    child_classes = ['LinkPlugin']
    tag_type = 'naked'
    css_class = 'btn'

plugin_pool.register_plugin(ButtonWrapperPlugin)
