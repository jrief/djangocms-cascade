import json

from django.forms import widgets
from django.forms.fields import CharField, BooleanField
from django.db.models.fields.related import ManyToOneRel
from django.contrib.admin import StackedInline
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags, strip_spaces_between_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ngettext_lazy, gettext_lazy as _
from filer.fields.image import FilerImageField, AdminImageFormField
from filer.settings import settings as filer_settings
from filer.utils.loader import load_model
from cms.plugin_pool import plugin_pool
from djangocms_text_ckeditor.fields import HTMLFormField

from cmsplugin_cascade import app_settings
from cmsplugin_cascade.fields import HiddenDictField, SizeField, MultiSizeField
from cmsplugin_cascade.forms import CascadeModelForm, CascadeModelFormMixin
from cmsplugin_cascade.image import ImagePropertyMixin
from cmsplugin_cascade.mixins import WithInlineElementsMixin
from cmsplugin_cascade.models import InlineCascadeElement
from cmsplugin_cascade.plugin_base import CascadePluginBase, create_proxy_model
from cmsplugin_cascade.utils import compute_aspect_ratio, get_image_size, parse_responsive_length

Image = load_model(filer_settings.FILER_IMAGE_MODEL)


class MarkerModelMixin:
    @property
    def data(self):
        return mark_safe(json.dumps(self.glossary))


class MarkerForm(CascadeModelForm):
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

    marker_image = AdminImageFormField(
        ManyToOneRel(FilerImageField, Image, 'file_ptr'),
        Image.objects.all(),
        label=_("Marker Image"),
        required=False,
        to_field_name='image_file',
    )

    marker_width = SizeField(
        label=_("Marker Width"),
        allowed_units=['px'],
        required=False,
        help_text=_("Width of the marker icon in pixels."),
    )

    marker_anchor = MultiSizeField(
        ['left', 'top'],
        label=_("Marker Anchor"),
        allowed_units=['px', '%'],
        required=False,
        help_text=_("The coordinates of the icon's anchor (relative to its top left corner)."),
    )

    popup_text = HTMLFormField(
        required=False,
        help_text=_("Optional rich text to display in popup."),
    )

    position = HiddenDictField()

    class Meta:
        entangled_fields = {'glossary': ['title', 'use_icon', 'marker_image', 'marker_width', 'marker_anchor',
                                         'popup_text', 'position']}

    def clean(self):
        cleaned_data = super().clean()
        try:
            position = cleaned_data['position']
            if isinstance(position, str):
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
                cleaned_data['position'] = position

        popup_text = cleaned_data.pop('popup_text', '')
        if strip_tags(popup_text):
            cleaned_data['popup_text'] = strip_spaces_between_tags(popup_text)
        return cleaned_data


class MarkerInline(StackedInline):
    model = InlineCascadeElement
    form = MarkerForm
    raw_id_fields = ['marker_image']
    verbose_name = _("Marker")
    verbose_name_plural = _("Markers")
    extra = 0


class LeafletFormMixin(CascadeModelFormMixin):
    map_width = SizeField(
        label=_("Map Width"),
        allowed_units=['px', '%'],
        initial='100%',
        help_text=_("Set the map width in percent relative to containing element."),
    )

    map_height = SizeField(
        label=_("Adapt Map Height"),
        allowed_units=['px', '%'],
        initial='400px',
        help_text=_("Set a fixed height in pixels, or percent relative to the map width."),
    )

    map_min_height = SizeField(
        label=_("Adapt Map Minimum Height"),
        allowed_units=['px'],
        required=False,
        help_text=_("Optional, set a minimum height in pixels."),
    )

    scroll_wheel_zoom = BooleanField(
        label=_("Zoom by scrolling wheel"),
        initial=True,
        required=False,
        help_text=_("Zoom into map on mouse over by scrolling wheel."),
    )

    map_position = HiddenDictField(
        initial=app_settings.CMSPLUGIN_CASCADE['leaflet']['default_position'],
    )

    class Meta:
        entangled_fields = {'glossary': ['map_width', 'map_height', 'map_position', 'map_min_height',
                                         'scroll_wheel_zoom']}

    def clean(self):
        cleaned_data = super().clean()
        try:
            if isinstance(cleaned_data['map_position'], str):
                cleaned_data['map_position'] = json.loads(cleaned_data['map_position'])
            elif not isinstance(cleaned_data['map_position'], dict):
                raise ValueError
        except (ValueError, KeyError):
            raise ValidationError("Invalid internal position data. Check your Javascript imports.")
        return cleaned_data


class LeafletModelMixin:
    @property
    def map_position(self):
        return mark_safe(json.dumps(self.glossary.get('map_position', {})))


class LeafletPlugin(WithInlineElementsMixin, CascadePluginBase):
    name = _("Map")
    parent_classes = None
    require_parent = False
    allow_children = False
    change_form_template = 'cascade/admin/leaflet_plugin_change_form.html'
    ring_plugin = 'LeafletPlugin'
    form = LeafletFormMixin
    admin_preview = False
    render_template = 'cascade/plugins/leaflet.html'
    inlines = [MarkerInline]
    model_mixins = (LeafletModelMixin,)
    settings = mark_safe(json.dumps(app_settings.CMSPLUGIN_CASCADE['leaflet']))

    class Media:
        css = {'all': [
            'node_modules/leaflet/dist/leaflet.css',
            'node_modules/leaflet-easybutton/src/easy-button.css',
            'cascade/css/admin/leafletplugin.css',
        ]}
        js = [
            'node_modules/leaflet/dist/leaflet.js',
            'node_modules/leaflet-easybutton/src/easy-button.js',
            'admin/js/jquery.init.js',
            'cascade/js/admin/leafletplugin.js',
        ]

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = dict(extra_context or {}, settings=self.settings)
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = dict(extra_context or {}, settings=self.settings)
        return super().change_view(request, object_id, form_url, extra_context)

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
        num_elems = obj.inline_elements.count()
        content = ngettext_lazy("with {0} marker", "with {0} markers", num_elems).format(num_elems)
        return mark_safe(content)

    @classmethod
    def get_data_representation(cls, instance):
        data = super().get_data_representation(instance)
        data.update(inlines=[ie.glossary for ie in instance.inline_elements.all()])
        return data

plugin_pool.register_plugin(LeafletPlugin)
