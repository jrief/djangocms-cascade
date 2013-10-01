from django.forms import widgets
from django.forms.models import modelform_factory
from django.utils import simplejson as json
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from cmsplugin_bootstrap.models import BootstrapElement


class BootstrapPluginBase(CMSPluginBase):
    class ExtraStylesWidget(widgets.MultiWidget):
        def __init__(self, **kwargs):
            wdg_attrs = [{ 'placeholder': 'margin-%s' % d, 'class': 'style-field' } for d in BootstrapElement.style_dirs]
            margin_widgets = [widgets.TextInput(m) for m in wdg_attrs]
            super(self.__class__, self).__init__(margin_widgets)

        def decompress(self, value):
            value = value and json.loads(value) or []
            value += [None] * (len(BootstrapElement.style_dirs) - len(value))
            return value

        def value_from_datadict(self, data, files, name):
            result = [data.get('margin-%s' % d) or None for d in BootstrapElement.style_dirs]
            return result

        def render(self, name, value, attrs=None):
            values = self.decompress(value)
            html = '<p>'
            for k, d in enumerate(BootstrapElement.style_dirs):
                html += self.widgets[k].render('margin-%s' % d, values[k], attrs)
            html += '</p>'
            return mark_safe(html)

    module = 'Bootstrap'
    model = BootstrapElement
    change_form_template = "cms/plugins/bootstrap/change_form.html"
    render_template = "cms/plugins/bootstrap/generic.html"
    allow_children = True

    def __init__(self, *args, **kwargs):
        super(BootstrapPluginBase, self).__init__(*args, **kwargs)
        extra_widgets = SortedDict()
        if hasattr(self, 'css_classes') and len(self.css_classes) > 1:
            extra_widgets['class_name'] = widgets.Select(choices=self.css_classes)
        if hasattr(self, 'extra_classes_widget'):
            extra_widgets['extra_classes'] = self.extra_classes_widget
        extra_widgets['extra_styles'] = self.__class__.ExtraStylesWidget()
        self.form = modelform_factory(BootstrapElement, fields=extra_widgets.keys(), widgets=extra_widgets)

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
    extra_classes = tuple(2 * ('btn-%s' % b,)
        for b in ('primary', 'info', 'success', 'warning', 'danger', 'inverse', 'link'))

plugin_pool.register_plugin(ButtonWrapperPlugin)


class BootstrapRowPlugin(BootstrapPluginBase):
    name = _("Row container")
    child_classes = ['BootstrapColumnPlugin']
    tag_type = 'div'
    css_classes = (('row', 'row'),)

plugin_pool.register_plugin(BootstrapRowPlugin)


class BootstrapColumnPlugin(BootstrapPluginBase):
    class ExtraClassesWidget(widgets.MultiWidget):
        def __init__(self, attrs=None):
            choices = ((None, 'no offset'),) + tuple(2 * ('offset%s' % o,) for o in range(1, 12))
            offset_widget = widgets.RadioSelect(choices=choices)
            super(self.__class__, self).__init__([offset_widget], attrs)

        def decompress(self, value):
            value = value and json.loads(value) or []
            value += [None] * (1 - len(value))
            return value

        def value_from_datadict(self, data, files, name):
            return [data.get('offset')]

        def render(self, name, value, attrs=None):
            value = self.decompress(value)
            html = '<div class="clearfix">' + self.widgets[0].render('offset', value[0], attrs) + '</div>'
            return mark_safe(html)

    name = _("Column container")
    parent_classes = ['BootstrapRowPlugin']
    require_parent = True
    tag_type = 'div'
    css_classes = tuple(2 * ('span%s' % i,) for i in range(1, 13))
    extra_classes_widget = ExtraClassesWidget()

plugin_pool.register_plugin(BootstrapColumnPlugin)


class BootstrapThumbnailsPlugin(BootstrapPluginBase):
    name = _("Thumbnails")
    child_classes = ['BootstrapThumbImagePlugin']
    tag_type = 'ul'
    css_classes = (('thumbnails', 'thumbnails'),)

plugin_pool.register_plugin(BootstrapThumbnailsPlugin)


class BootstrapThumbImagePlugin(BootstrapPluginBase):
    name = _("Single thumbnail")
    parent_classes = ['BootstrapThumbnailsPlugin']
    require_parent = True
    tag_type = 'li'
    css_classes = (('thumbnail', 'thumbnail'),)

plugin_pool.register_plugin(BootstrapThumbImagePlugin)
