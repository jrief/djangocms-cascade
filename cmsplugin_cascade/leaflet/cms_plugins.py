# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.forms.fields import CharField, Field
from django.forms.models import ModelForm, ModelChoiceField
from django.forms import widgets
from django.db.models.fields.related import ManyToOneRel
from django.contrib.admin import StackedInline
from django.contrib.admin.sites import site
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.utils import six

from filer.fields.image import AdminFileWidget, FilerImageField
from filer.models.imagemodels import Image

from cms.plugin_pool import plugin_pool

from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.models import InlineCascadeElement
from cmsplugin_cascade.mixins import ImagePropertyMixin
from cmsplugin_cascade.plugin_base import create_proxy_model, CascadePluginBase
from cmsplugin_cascade.settings import CMSPLUGIN_CASCADE
from cmsplugin_cascade.widgets import CascadingSizeWidget


class MarkerForm(ModelForm):
    marker_title = CharField(
        label=_("Marker Title"),
        widget=widgets.TextInput(attrs={'size': 60}),
    )

    marker_image = ModelChoiceField(
        queryset=Image.objects.all(),
        label=_("Marker Image"),
        required=False,
    )

    leaflet = Field(widget=widgets.HiddenInput)

    glossary_field_order = ['marker_title', 'marker_image']

    class Meta:
        exclude = ['glossary']

    def __init__(self, data=None, *args, **kwargs):
        try:
            initial = dict(kwargs['instance'].glossary)
        except (KeyError, AttributeError):
            initial = {}
        initial.update(kwargs.pop('initial', {}))
        initial['leaflet'] = json.dumps(initial.pop('leaflet', {}))
        for key in self.glossary_field_order:
            self.base_fields[key].initial = initial.get(key)
        try:
            self.base_fields['marker_image'].initial = initial['image']['pk']
        except KeyError:
            self.base_fields['marker_image'].initial = None
        self.base_fields['marker_image'].widget = AdminFileWidget(ManyToOneRel(FilerImageField, Image, 'file_ptr'), site)
        super(MarkerForm, self).__init__(data, initial=initial, *args, **kwargs)

    def clean(self):
        try:
            leaflet = self.cleaned_data['leaflet']
            if isinstance(leaflet, six.string_types):
                self.instance.glossary.update(leaflet=json.loads(leaflet))
            elif isinstance(leaflet, dict):
                self.instance.glossary.update(leaflet=leaflet)
            else:
                raise ValueError
        except (ValueError, KeyError):
            raise ValidationError("Invalid internal leaflet data. Check your Javascript imports.")

        image_file = self.cleaned_data.pop('image_file', None)
        if image_file:
            image_data = {'pk': image_file.pk, 'model': 'filer.Image'}
            self.instance.glossary.update(image=image_data)
        else:
            self.instance.glossary.pop('image', None)
        for key in self.glossary_field_order:
            self.instance.glossary.update({key: self.cleaned_data.get(key)})


class MarkerInline(StackedInline):
    model = InlineCascadeElement
    form = MarkerForm
    raw_id_fields = ['image_file']
    verbose_name = _("Marker")
    verbose_name_plural = _("Markers")
    extra = 0


class LeafletForm(ModelForm):
    DEFAULTS = {
        'lat': 30.0,
        'lng': -40.0,
        'zoom': 3,
    }

    leaflet = Field(widget=widgets.HiddenInput)

    class Meta:
        fields = ['glossary']

    def __init__(self, data=None, *args, **kwargs):
        try:
            initial = dict(kwargs['instance'].glossary)
        except (KeyError, AttributeError):
            initial = {}
        initial.update(kwargs.pop('initial', {}))
        initial['leaflet'] = json.dumps(initial.pop('leaflet', self.DEFAULTS))
        super(LeafletForm, self).__init__(data, initial=initial, *args, **kwargs)

    def clean(self):
        try:
            leaflet = self.cleaned_data['leaflet']
            if isinstance(leaflet, six.string_types):
                self.cleaned_data['glossary'].update(leaflet=json.loads(leaflet))
            elif isinstance(leaflet, dict):
                self.cleaned_data['glossary'].update(leaflet=leaflet)
            else:
                raise ValueError
        except (ValueError, KeyError):
            raise ValidationError("Invalid internal leaflet data. Check your Javascript imports.")


class LeafletPlugin(CascadePluginBase):
    name = _("Map")
    parent_classes = None
    require_parent = False
    allow_children = False
    change_form_template = 'cascade/admin/leaflet_plugin_change_form.html'
    ring_plugin = 'LeafletPlugin'
    admin_preview = False
    render_template = 'cascade/plugins/leaflet.html'
    inlines = (MarkerInline,)
    glossary_field_order = ('map_width', 'map_height')
    form = LeafletForm

    map_width = GlossaryField(
        CascadingSizeWidget(allowed_units=['px', '%'], required=True),
        label=_("Map Width"),
        initial='100%',
        help_text=_("Set the map width in percent relative to containing element."),
    )

    map_height = GlossaryField(
        CascadingSizeWidget(allowed_units=['px', '%'], required=True),
        label=_("Adapt Map Height"),
        initial='400px',
        help_text=_("Set a fixed height in pixels, or percent relative to the map width."),
    )

    class Media:
        css = {'all': [
            'node_modules/leaflet/dist/leaflet.css',
            'node_modules/leaflet-easybutton/src/easy-button.css',
            'cascade/css/admin/leafletplugin.css',
        ]}
        js = [
            'node_modules/leaflet/dist/leaflet.js',
            'node_modules/leaflet-easybutton/src/easy-button.js',
            'cascade/js/admin/leafletplugin.js',
        ]

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = dict(extra_context or {}, settings=CMSPLUGIN_CASCADE['leaflet'])
        return super(LeafletPlugin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = dict(extra_context or {}, settings=CMSPLUGIN_CASCADE['leaflet'])
        return super(LeafletPlugin, self).change_view(request, object_id, form_url, extra_context)

    def render(self, context, instance, placeholder):
        context.update(dict(instance=instance, placeholder=placeholder,
                            settings=CMSPLUGIN_CASCADE['leaflet'],
                            markers=instance.inline_elements.all()))
        return context

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(LeafletPlugin, cls).get_css_classes(obj)
        css_class = obj.glossary.get('css_class')
        if css_class:
            css_classes.append(css_class)
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(LeafletPlugin, cls).get_identifier(obj)
        num_elems = obj.inline_elements.count()
        content = ungettext_lazy("with {0} marker", "with {0} markers", num_elems).format(num_elems)
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(LeafletPlugin)
