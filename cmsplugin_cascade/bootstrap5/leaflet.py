from random import randint

from django.forms.fields import CharField
from django.utils.translation import gettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap5.hyperlink import HyperlinkDialogForm
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.models import CascadeElement

from formset.forms import ModelForm
from formset.formfields.geomap import GeoMapField
from formset.formfields.richtext import RichTextField
from formset.geomap import controls, dialogs
from formset.richtext import controls as richtext_controls
from formset.widgets.geomap import GeoMapWidget
from formset.widgets.richtext import RichTextarea


class SpecialMarkerDialogForm(dialogs.GeoMapDialogForm):
    title = _("Edit Marker")
    extension = 'special_marker'
    properties_map = {'name': 'name', 'body': 'body'}

    name = CharField(
        required=False,
        label=_("Name"),
    )
    body = RichTextField(
        label=_("Description"),
        widget=RichTextarea(
            control_elements=[
                richtext_controls.Bold(),
                richtext_controls.Italic(),
                richtext_controls.DialogControl(HyperlinkDialogForm()),
                richtext_controls.Separator(),
                richtext_controls.ClearFormat(),
                richtext_controls.Undo(),
                richtext_controls.Redo(),
            ],
            attrs={'maxlength': 500},
        ),
        required=False,
    )


class LeafletMarkerForm(ModelForm):
    map = GeoMapField(
        label='',
        widget=GeoMapWidget(
            controls_topleft=[
                controls.PointEditor(
                    identifier='special-marker',
                    dialog_forms=[SpecialMarkerDialogForm()],
                ),
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
    parent_classes = ['BootstrapContainerPlugin', 'BootstrapColumnPlugin']
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
        # map_data = self.form().get_field('map').widget.render_map_data(instance.glossary.get('map', {}))
        # context.update({'map_data': map_data})
        context.update({'map_data': instance.glossary.get('map'), 'randint': randint(0, 1000000)})
        return context


plugin_pool.register_plugin(LeafletPlugin)
