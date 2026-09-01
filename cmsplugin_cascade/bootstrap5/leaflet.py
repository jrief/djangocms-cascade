from django.forms.fields import CharField
from django.utils.translation import gettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.models import CascadeElement

from formset.forms import ModelForm
from formset.formfields.geomap import GeoMapField
from formset.formfields.richtext import RichTextField
from formset.geomap import controls, dialogs
from formset.widgets.geomap import GeoMapWidget


class MarkerDialogForm(dialogs.GeoMapDialogForm):
    title = _("Edit Marker Details")
    extension = 'marker_details'
    properties_map = {'name': 'name', 'body': 'body'}

    name = CharField(
        required=False,
        label=_("Name"),
    )
    body = RichTextField(
        label=_("Description"),
        required=False,
    )


class LeafletMarkerForm(ModelForm):
    map = GeoMapField(
        label='',
        widget=GeoMapWidget(
            controls_topleft=[
                controls.PointEditor(dialog_forms=[MarkerDialogForm()]),
            ],
            attrs={'style': 'height:450px;max-height:900px;'},
        ),
    )

    class Meta:
        model = CascadeElement
        exclude = ['shared_glossary']
        fields_map = {
            'glossary': ['map'],
        }


class LeafletPlugin(BootstrapPluginBase):
    name = _("Leaflet")
    parent_classes = ['BootstrapColumnPlugin']
    form = LeafletMarkerForm
    render_template = 'cascade/bootstrap5/leaflet.html'

    class Media:
        css = {'all': [
            'cascade/css/leaflet.css',
            'formset/css/bootstrap5-extra.css',
        ]}

    @classmethod
    def get_identifier(cls, instance):
        return "Content"

    def render(self, context, instance, placeholder):
        context = self.super(LeafletPlugin, self).render(context, instance, placeholder)
        context.update({'coordinate': instance.glossary.get('coordinate', '')})
        return context


plugin_pool.register_plugin(LeafletPlugin)
