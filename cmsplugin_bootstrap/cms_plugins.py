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

    def __init__(self, *args, **kwargs):
        super(BootstrapPluginBase, self).__init__(*args, **kwargs)
        choice_widgets = {}
        if hasattr(self, 'css_classes') and len(self.css_classes) > 1:
            choice_widgets['class_name'] = widgets.Select(choices=self.css_classes)
        if hasattr(self, 'extra_classes'):
            choice_widgets['extra_classes'] = widgets.CheckboxSelectMultiple(choices=self.extra_classes)
        self.form = modelform_factory(BootstrapElement, fields=choice_widgets.keys(), widgets=choice_widgets)

    def save_model(self, request, obj, form, change):
        obj.tag_type = self.tag_type
        if hasattr(self, 'css_classes') and len(self.css_classes) == 1:
            obj.class_name = self.css_classes[0][0]
        return super(BootstrapPluginBase, self).save_model(request, obj, form, change)


class ButtonWrapperPlugin(BootstrapPluginBase):
    name = _("Button wrapper")
    render_template = "cms/plugins/bootstrap/naked.html"
    child_classes = ['LinkPlugin']
    tag_type = 'naked'
    css_classes = (('btn', 'btn'),)
    extra_classes = tuple((chr(b[0] + 64), 'btn-%s' % b[1])
        for b in enumerate(('primary', 'info', 'success', 'warning', 'danger', 'inverse', 'link')))

plugin_pool.register_plugin(ButtonWrapperPlugin)


class BootstrapRowPlugin(BootstrapPluginBase):
    name = _("Row container")
    child_classes = ['BootstrapColumnPlugin']
    tag_type = 'div'
    css_classes = (('row', 'row'),)

plugin_pool.register_plugin(BootstrapRowPlugin)


class BootstrapColumnPlugin(BootstrapPluginBase):
    name = _("Column container")
    parent_classes = ['BootstrapRowPlugin']
    require_parent = True
    tag_type = 'div'
    css_classes = tuple(2 * ('span%s' % i,) for i in range(1, 13))
    extra_classes = tuple((chr(o + 64), 'offset%s' % o,) for o in range(1, 12))

plugin_pool.register_plugin(BootstrapColumnPlugin)
