# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.forms.fields import CharField, BooleanField, Field
from django.forms.models import ModelForm, ModelChoiceField
from django.forms.utils import ErrorList
from django.forms import widgets
from django.db.models.fields.related import ManyToOneRel
from django.contrib.admin import StackedInline
from django.contrib.admin.sites import site
from django.core.exceptions import ValidationError
from django.utils.html import format_html, strip_tags, strip_spaces_between_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.utils import six

from filer.fields.image import AdminFileWidget, FilerImageField
from filer.models.imagemodels import Image

from cms.plugin_pool import plugin_pool
from djangocms_text_ckeditor.fields import HTMLFormField

from cmsplugin_cascade import app_settings
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.models import InlineCascadeElement
from cmsplugin_cascade.plugin_base import CascadePluginBase, create_proxy_model
from cmsplugin_cascade.image import ImagePropertyMixin
from cmsplugin_cascade.utils import compute_aspect_ratio, get_image_size, parse_responsive_length
from cmsplugin_cascade.widgets import CascadingSizeWidget, MultipleCascadingSizeWidget


class GlossaryFormField(Field):
    error_class = ErrorList

    def __init__(self, widget=None, **kwargs):
        if widget:
            kwargs['required'] = widget.required
        super(GlossaryFormField, self).__init__(widget=widget, **kwargs)

    def run_validators(self, value):
        if not callable(getattr(self.widget, 'validate', None)):
            return
        errors = []
        if callable(getattr(self.widget, '__iter__', None)):
            for field_name in self.widget:
                try:
                    self.widget.validate(value, field_name)
                except ValidationError as e:
                    if isinstance(getattr(e, 'params', None), dict):
                        e.params.update(label=self.label)
                    messages = self.error_class([m for m in e.messages])
                    errors.extend(messages)
        else:
            try:
                self.widget.validate(value)
            except ValidationError as e:
                if isinstance(getattr(e, 'params', None), dict):
                    e.params.update(label=self.label)
                errors = self.error_class([m for m in e.messages])
        if errors:
            raise ValidationError(errors)


class MarkerModelMixin(object):
    @property
    def data(self):
        return mark_safe(json.dumps(self.glossary))


class MarkerForm(ModelForm):
    title = CharField(
        label=_("Marker Title"),
        widget=widgets.TextInput(attrs={'size': 60}),
        help_text=_("Please choose a title, then go to the map to set a marker pin")
    )

    use_icon = BooleanField(
        label=_("Use customized marker icon"),
        initial=False,
        required=False,
    )

    marker_image = ModelChoiceField(
        queryset=Image.objects.all(),
        label=_("Marker Image"),
        required=False,
    )

    marker_width = GlossaryFormField(
        widget=CascadingSizeWidget(allowed_units=['px'], required=False),
        label=_("Marker Width"),
        required=False,
        help_text=_("Width of the marker icon in pixels."),
    )

    marker_anchor = GlossaryFormField(
        widget=MultipleCascadingSizeWidget(['left', 'top'], allowed_units=['px', '%'], required=False),
        required=False,
        label=_("Marker Anchor"),
        help_text=_("The coordinates of the icon's anchor (relative to its top left corner)."),
    )

    popup_text = HTMLFormField(
        required=False,
        help_text=_("Optional rich text to display in popup."),
    )

    position = Field(widget=widgets.HiddenInput)

    glossary_field_order = ['title', 'marker_width', 'marker_anchor', 'popup_text']

    class Meta:
        exclude = ['glossary']

    def __init__(self, *args, **kwargs):
        try:
            initial = dict(kwargs['instance'].glossary)
            has_original = True
        except (KeyError, AttributeError):
            initial = {}
            has_original = False
        initial.update(kwargs.pop('initial', {}))
        self.base_fields['position'].initial = json.dumps(initial.pop('position', {}))
        for key in self.glossary_field_order:
            self.base_fields[key].initial = initial.get(key)
        try:
            self.base_fields['marker_image'].initial = initial['image']['pk']
        except KeyError:
            self.base_fields['marker_image'].initial = None
            self.base_fields['use_icon'].initial = False
        else:
            self.base_fields['use_icon'].initial = True
        self.base_fields['marker_image'].widget = AdminFileWidget(ManyToOneRel(FilerImageField, Image, 'file_ptr'), site)
        super(MarkerForm, self).__init__(*args, **kwargs)
        if has_original:
            self.fields['title'].help_text = None

    def clean(self):
        try:
            position = self.cleaned_data['position']
            if isinstance(position, six.string_types):
                position = json.loads(position)
            elif not isinstance(position, dict):
                raise ValueError
        except (ValueError, KeyError):
            raise ValidationError("Invalid internal position data. Check your Javascript imports.")
        else:
            if 'lat' not in position or 'lng' not in position:
                # place the marker in the center of the current map
                position = {k: v for k, v in self.instance.cascade_element.glossary['map_position'].items()
                            if k in ['lat', 'lng']}
            self.instance.glossary.update(position=position)

        marker_image = self.cleaned_data.pop('marker_image', None)
        if marker_image:
            image_data = {'pk': marker_image.pk, 'model': 'filer.Image'}
            self.instance.glossary.update(image=image_data)
        else:
            self.instance.glossary.pop('image', None)

        popup_text = self.cleaned_data.pop('popup_text', None)
        if strip_tags(popup_text):
            popup_text = strip_spaces_between_tags(popup_text)
            self.cleaned_data.update(popup_text=popup_text)

        for key in self.glossary_field_order:
            self.instance.glossary.update({key: self.cleaned_data.get(key)})


class MarkerInline(StackedInline):
    model = InlineCascadeElement
    form = MarkerForm
    raw_id_fields = ['marker_image']
    verbose_name = _("Marker")
    verbose_name_plural = _("Markers")
    extra = 0


class LeafletForm(ModelForm):
    map_position = Field(widget=widgets.HiddenInput)

    class Meta:
        fields = ['glossary']

    def __init__(self, data=None, *args, **kwargs):
        try:
            initial = dict(kwargs['instance'].glossary)
        except (KeyError, AttributeError):
            initial = {}
        initial.update(kwargs.pop('initial', {}))
        map_position = initial.pop('map_position', app_settings.CMSPLUGIN_CASCADE['leaflet']['default_position'])
        initial['map_position'] = json.dumps(map_position)
        super(LeafletForm, self).__init__(data, initial=initial, *args, **kwargs)

    def clean(self):
        try:
            map_position = self.cleaned_data['map_position']
            if isinstance(map_position, six.string_types):
                self.cleaned_data['glossary'].update(map_position=json.loads(map_position))
            elif isinstance(map_position, dict):
                self.cleaned_data['glossary'].update(map_position=map_position)
            else:
                raise ValueError
        except (ValueError, KeyError):
            raise ValidationError("Invalid internal position data. Check your Javascript imports.")


class LeafletModelMixin(object):
    @property
    def map_position(self):
        return mark_safe(json.dumps(self.glossary.get('map_position', {})))


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
    glossary_field_order = ('map_width', 'map_height', 'map_min_height')
    model_mixins = (LeafletModelMixin,)
    form = LeafletForm
    settings = mark_safe(json.dumps(app_settings.CMSPLUGIN_CASCADE['leaflet']))

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

    map_min_height = GlossaryField(
        CascadingSizeWidget(allowed_units=['px'], required=False),
        label=_("Adapt Map Minimum Height"),
        help_text=_("Optional, set a minimum height in pixels."),
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
        extra_context = dict(extra_context or {}, settings=self.settings)
        return super(LeafletPlugin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = dict(extra_context or {}, settings=self.settings)
        return super(LeafletPlugin, self).change_view(request, object_id, form_url, extra_context)

    def render(self, context, instance, placeholder):
        marker_instances = []
        for inline_element in instance.inline_elements.all():
            try:
                ProxyModel = create_proxy_model('LeafletMarker',
                                                (ImagePropertyMixin, MarkerModelMixin),
                                                InlineCascadeElement,
                                                module=__name__)
                marker = ProxyModel(id=inline_element.id, glossary=inline_element.glossary)
                try:
                    aspect_ratio = compute_aspect_ratio(marker.image)
                    width = parse_responsive_length(marker.glossary.get('marker_width') or '25px')
                    marker.size = list(get_image_size(width[0], (None, None), aspect_ratio))
                    marker.size2x = 2 * marker.size[0], 2 * marker.size[1]
                except Exception:
                    # if accessing the image file fails, skip size computations
                    pass
                else:
                    try:
                        marker_anchor = marker.glossary['marker_anchor']
                        top = parse_responsive_length(marker_anchor['top'])
                        left = parse_responsive_length(marker_anchor['left'])
                        if top[0] is None or left[0] is None:
                            left = width[0] * left[1]
                            top = width[0] * aspect_ratio * top[1]
                        else:
                            left, top = left[0], top[0]
                        marker.anchor = [left, top]
                    except Exception:
                        pass
                marker_instances.append(marker)
            except (KeyError, AttributeError):
                pass

        context.update(dict(instance=instance,
                            placeholder=placeholder,
                            settings=self.settings,
                            config=app_settings.CMSPLUGIN_CASCADE['leaflet'],
                            markers=marker_instances))
        return context

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(LeafletPlugin, cls).get_css_classes(obj)
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

    @classmethod
    def get_data_representation(cls, instance):
        data = super(LeafletPlugin, cls).get_data_representation(instance)
        data.update(inlines=[ie.glossary for ie in instance.inline_elements.all()])
        return data

plugin_pool.register_plugin(LeafletPlugin)
