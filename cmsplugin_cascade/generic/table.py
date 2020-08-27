import json

from django.core.serializers.json import DjangoJSONEncoder
from django.forms import widgets, CharField, Field
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from entangled.forms import EntangledModelFormMixin

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import CascadePluginBase


class InternalField(Field):
    widget = widgets.HiddenInput

    def prepare_value(self, value):
        if isinstance(value, (dict, list)):
            return json.dumps(value, cls=DjangoJSONEncoder)
        return value

    def to_python(self, value):
        if isinstance(value, str):
            return json.loads(value)
        return value


class TableFormMixin(EntangledModelFormMixin):
    caption = CharField(
        label=_("Table caption"),
        required=False,
        widget=widgets.TextInput(attrs={'style': 'width: 100%; padding-right: 0;'}),
    )

    headers = InternalField(initial=['A', 'B', 'C'])

    data = InternalField(initial=[['', '', '']])

    class Meta:
        entangled_fields = {'glossary': ['caption', 'headers', 'data']}


class TablePlugin(CascadePluginBase):
    name = _("Table")
    ring_plugin = 'TablePlugin'
    render_template = 'cascade/generic/table.html'
    parent_classes = None
    allow_children = False
    form = TableFormMixin
    change_form_template = 'cascade/admin/table_plugin_change_form.html'
    default_css_class = 'table'

    class Media:
        css = {'all': ['node_modules/jexcel/dist/jexcel.css', 'node_modules/jsuites/dist/jsuites.css']}
        js = ['node_modules/jexcel/dist/jexcel.js', 'node_modules/jsuites/dist/jsuites.js', 'admin/js/jquery.init.js',
              'cascade/js/admin/tableplugin.js']

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = dict(extra_context or {}, settings=self.get_settings(request))
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = dict(extra_context or {}, settings=self.get_settings(request))
        return super().change_view(request, object_id, form_url, extra_context)

    def get_settings(self, request):
        return mark_safe(json.dumps({}))

    def render(self, context, instance, placeholder):
        context = self.super(TablePlugin, self).render(context, instance, placeholder)
        return context

plugin_pool.register_plugin(TablePlugin)
