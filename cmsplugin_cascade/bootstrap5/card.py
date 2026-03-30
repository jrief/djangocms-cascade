from django.forms.fields import CharField
from django.forms.forms import Form
from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap5.breakpoint import Breakpoint
from cmsplugin_cascade.bootstrap5.fields import AspectRatioChoiceField
from cmsplugin_cascade.bootstrap5.hyperlink import HyperlinkForm, HyperlinkPluginMixin, LinkTypeChoiceField
from cmsplugin_cascade.bootstrap5.icon import extract_stylesheet_urls
from cmsplugin_cascade.bootstrap5.picture import AspectRatioChoicesMixin, ImageElementMixin, LazySizesPictureMixin
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.bootstrap5.richtext import GlyphDialogForm, HyperlinkDialogForm
from cmsplugin_cascade.link.plugin_base import LinkElementMixin

from finder.forms.fields import FinderFileField

from formset.collection import AddSiblingActivator, FormCollection
from formset.formfields.collection import CollectionField
from formset.formfields.richtext import RichTextField
from formset.renderers.bootstrap import richtext_attributes
from formset.richtext import controls
from formset.widgets.richtext import RichTextarea


class ListItemForm(Form):
    content = CharField(
        label=_("Item Content"),
        widget=TextInput(attrs={'style': 'width: 100%;'}),
    )


class ListGroupCollection(FormCollection):
    legend = _("List Group")
    min_siblings = 0
    max_siblings = 10
    is_sortable = True
    list_item_form = ListItemForm()
    induce_add_sibling = '.add_list_item:active'
    ignore_marked_for_removal = True
    add_list_item = AddSiblingActivator(_("Add List Item"))


class CardForm(HyperlinkForm):
    image = FinderFileField(
        label=_("Image"),
        required=False,
        accept_mime_types=['image/*'],
        help_text=_("Optional image for this card."),
    )
    aspect_ratio = AspectRatioChoiceField(Breakpoint.xs, add_original=True)
    title = CharField(
        label=_("Title"),
        required=False,
        help_text=_("Optional title for this card."),
        widget=TextInput(attrs={'style': 'width: 100%;'}),
    )
    subtitle = CharField(
        label=_("Subtitle"),
        required=False,
        help_text=_("Optional subtitle for this card."),
        widget=TextInput(attrs={'style': 'width: 100%;'}),
    )
    body = RichTextField(
        label='',
        widget=RichTextarea(
            control_elements=[
                controls.Heading(),
                controls.Bold(),
                controls.Italic(),
                controls.BulletList(),
                controls.DialogControl(
                    HyperlinkDialogForm(),
                    icon='formset/icons/link.svg',
                ),
                controls.DialogControl(
                    GlyphDialogForm(),
                    icon='formset/icons/omega.svg',
                ),
                controls.HorizontalRule(),
                controls.Separator(),
                controls.ClearFormat(),
                controls.Undo(),
                controls.Redo(),
            ]
        ),
    )
    list_group = CollectionField(ListGroupCollection)
    link_type = LinkTypeChoiceField(required=False)
    link_content = CharField(
        label=_("Link Content"),
        required=False,
        widget=TextInput(attrs={
            'df-show': ".link_type !== ''",
            'style': 'width: 100%;',
        }),
    )

    class Meta(HyperlinkForm.Meta):
        fields_map = {
            'glossary': [
                'image', 'aspect_ratio', 'title', 'subtitle', 'body', 'list_group',
                *HyperlinkForm.Meta.fields_map['glossary'], 'link_content'
            ],
        }


class BootstrapCardPlugin(HyperlinkPluginMixin, AspectRatioChoicesMixin, LazySizesPictureMixin, BootstrapPluginBase):
    """
    Use this plugin to display a card with optional card-header and card-footer.
    """

    name = _("Card")
    default_css_class = 'card'
    require_parent = True
    parent_classes = ['BootstrapColumnPlugin']
    allow_children = False
    child_classes = []
    model_mixins = (LinkElementMixin, ImageElementMixin)
    change_form_template = 'admin/cmsplugin_cascade/formset/richtext_change_form.html'
    render_template = 'cascade/bootstrap5/card.html'
    form = CardForm

    class Media:
        css = {
            'all': [
                'cascade/css/richtext.css',
                'formset/css/bootstrap5-extra.css',
            ]
        }

    @classmethod
    def get_identifier(cls, instance):
        return instance.glossary.get('title', '')

    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        try:
            context.update(stylesheet_urls=extract_stylesheet_urls(obj.glossary['body']['content']))
        except KeyError:
            pass
        return super().render_change_form(request, context, add, change, form_url, obj)

    def render(self, context, instance, placeholder):
        if not (sources := instance.glossary.get('cached_sources')):
            sources = self.get_picture_sources(instance)
            instance.glossary['cached_sources'] = sources
            instance.save(update_fields=['glossary'])

        context = self.super(BootstrapCardPlugin, self).render(context, instance, placeholder)
        body = instance.glossary.get('body', {'type': 'doc', 'content': []})
        context.update({
            'picture': {'sources': sources, 'fallback_image': self.fallback_image},
            'title': instance.glossary.get('title'),
            'subtitle': instance.glossary.get('subtitle'),
            'stylesheet_urls': extract_stylesheet_urls(body['content']),
            'body': body,
            'list_group': instance.glossary.get('list_group'),
        })
        return context

plugin_pool.register_plugin(BootstrapCardPlugin)


def custom_richtext_attributes(node):
    if node['type'] == 'paragraph':
        return mark_safe(' class="card-text"')
    return richtext_attributes(node)
