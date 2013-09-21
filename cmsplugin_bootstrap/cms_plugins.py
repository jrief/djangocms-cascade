from django import forms
from django.forms import widgets
from django.forms.models import modelform_factory
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from cmsplugin_bootstrap.models import BootstrapElement


class BootstrapPluginBase(CMSPluginBase):
    module = 'Bootstrap'
    model = BootstrapElement
    render_template = "cms/plugins/bootstrap/generic.html"
    allow_children = True
    fieldsets = (
        (None, {
            'fields': ('class_name',)
        }),
        (_('Advanced Settings'), {
            'classes': ('collapse',),
            'fields': ('extra_classes', 'extra_styles',),
        }),
    )

    def __init__(self, *args, **kwargs):
        if hasattr(self, 'class_name_choices'):
            class_name_widget = widgets.Select(choices=self.class_name_choices)
            self.form = modelform_factory(BootstrapElement, widgets={'class_name': class_name_widget})
        else:
            self.form = modelform_factory(BootstrapElement, exclude=['class_name'])
            self.fieldsets[0][1]['fields'] = ()
        super(BootstrapPluginBase, self).__init__(*args, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.tag_type = self.tag_type
        if hasattr(self, 'css_class'):
            obj.class_name = self.css_class
        return super(BootstrapPluginBase, self).save_model(request, obj, form, change)


class ButtonWrapperPlugin(BootstrapPluginBase):
    name = _("Button wrapper")
    render_template = "cms/plugins/bootstrap/naked.html"
    child_classes = ['LinkPlugin']
    tag_type = 'naked'
    css_class = 'btn'

plugin_pool.register_plugin(ButtonWrapperPlugin)


class BootstrapRowPlugin(BootstrapPluginBase):
    name = _("Row container")
    child_classes = ['BootstrapColumnPlugin']
    tag_type = 'div'
    css_class = 'row'

plugin_pool.register_plugin(BootstrapRowPlugin)


class BootstrapColumnPlugin(BootstrapPluginBase):
    name = _("Column container")
    parent_classes = ['BootstrapRowPlugin']
    require_parent = True
    tag_type = 'div'
    class_name_choices = [2 * ('span%s' % i,) for i in range(1, 13)]

    def __init__(self, *args, **kwargs):
        super(BootstrapColumnPlugin, self).__init__(*args, **kwargs)

plugin_pool.register_plugin(BootstrapColumnPlugin)
