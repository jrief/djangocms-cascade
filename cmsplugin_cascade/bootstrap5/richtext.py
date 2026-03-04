from django.forms.fields import CharField, ChoiceField, EmailField, IntegerField, URLField
from django.forms.widgets import EmailInput, NumberInput, RadioSelect, TextInput, URLInput
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.models import CascadeElement

from finder.forms.fields import FinderFileField
from finder.forms.widgets import FinderFileSelect

from formset.forms import ModelForm
from formset.formfields.richtext import RichTextField
from formset.richtext import controls, dialogs
from formset.widgets import PhoneNumberInput, Selectize
from formset.widgets.richtext import RichTextarea

from cmsplugin_cascade.bootstrap5.hyperlink import AnchorChoiceField, AnchorFieldFilterSet, LinkTypeChoiceField, PageChoiceField


class HyperlinkDialogForm(dialogs.RichtextDialogForm):
    title = _("Edit Link")
    extension = 'hyperlink'
    extension_script = 'cascade/admin/tiptap-extensions/hyperlink.js'
    plugin_type = 'mark'

    link_content = CharField(
        label=_("Link Content"),
        widget=TextInput(attrs={
            'richtext-selection': True,
            'size': 50,
        })
    )
    link_type = LinkTypeChoiceField(
        widget=RadioSelect(attrs={'richtext-map-from': 'change_link_type()'}),
    )
    cms_page = PageChoiceField(
        label=_("CMS Page"),
        required=False,
        widget=Selectize(attrs={
            'richtext-map-to': '{cms_page: elements.link_type.value == "cmspage" ? elements.cms_page.value : ""}',
            'richtext-map-from': 'cms_page',
            'df-show': ".link_type == 'cmspage'",
            'df-require': ".link_type == 'cmspage'",
        }),
    )
    anchor = AnchorChoiceField(
        label='',
        required=False,
        empty_label=_("Page Root"),
        help_text=_("Page bookmark"),
        widget=Selectize(
            use_filter_set=AnchorFieldFilterSet,
            attrs={
                'richtext-map-to': '{anchor: elements.link_type.value == "cmspage" ? elements.anchor.value : ""}',
                'richtext-map-from': '{value: parseInt(attributes.anchor)}',  # a numeric value forces Selectize to refetch its options
                'df-show': ".link_type === 'cmspage'",
            },
        ),
    )
    ext_url = URLField(
        label=_("External URL"),
        required=False,
        widget=URLInput(attrs={
            'size': 35,
            'richtext-map-to': '{href: elements.link_type.value == "exturl" ? elements.ext_url.value : ""}',
            'richtext-map-from': 'href',
            'df-show': ".link_type == 'exturl'",
            'df-require': ".link_type == 'exturl'",
        }),
    )
    download_file = FinderFileField(
        label=_("Downloadable File"),
        required=False,
        help_text=_("A link to a downloadable file"),
        widget=FinderFileSelect(attrs={
            'richtext-map-to': '{download_file: elements.link_type.value == "download" ? elements.download_file.value : ""}',
            'richtext-map-from': 'download_file',
            'df-show': ".link_type === 'download'",
            'df-require': ".link_type == 'download'",
        }),
    )
    mail_to = EmailField(
        label=_("Email Address"),
        required=False,
        help_text=_("A link to an email address"),
        widget=EmailInput(attrs={
            'size': 35,
            'placeholder': "john@example.org",
            'richtext-map-to': '{mail_to: elements.link_type.value == "email" ? elements.mail_to.value : ""}',
            'richtext-map-from': 'mail_to',
            'df-show': ".link_type === 'email'",
            'df-require': ".link_type === 'email'",
        }),
    )
    phone_number = CharField(
        label=_("Phone Number"),
        required=False,
        help_text=_("A phone number link"),
        widget=PhoneNumberInput(attrs={
            'richtext-map-to': '{phone_number: elements.link_type.value == "phone" ? elements.phone_number.value : ""}',
            'richtext-map-from': 'phone_number',
            'df-show': ".link_type === 'phone'",
            'df-require': ".link_type === 'phone'",
        }),
    )


class InlineImageDialogForm(dialogs.RichtextDialogForm):
    title = _("Edit Image")
    extension = 'inline_image'
    extension_script = 'cascade/admin/tiptap-extensions/inlineimage.js'
    plugin_type = 'node'
    icon = 'formset/icons/image.svg'

    image_file = FinderFileField(
        label=_("Image"),
        required=False,
        widget = FinderFileSelect(attrs={
            'richtext-map-to': 'insert_cropped_image()',
            'richtext-map-from': 'dataset.file_id',
        }),
    )
    width = IntegerField(
        label=_("Width"),
        required=False,
        help_text=_("Leave empty to adapt to aspect ratio."),
        widget=NumberInput(attrs={'richtext-bidirectional': True}),
    )
    height = IntegerField(
        label=_("Height"),
        required=False,
        help_text=_("Leave empty to adapt to aspect ratio."),
        widget=NumberInput(attrs={'richtext-bidirectional': True}),
    )
    alignment = ChoiceField(
        label=_("Image alignment"),
        choices=[
            ('image-align-left', _("Freestanding left")),
            ('image-align-center', _("Freestanding centered")),
            ('image-align-right', _("Freestanding right")),
            ('image-float-left', _("Float left")),
            ('image-float-right', _("Float right")),
        ],
        required=False,
        initial='image-align-center',
        widget=RadioSelect(attrs={'richtext-map-from': 'align_image()'}),
    )

    def clean_content(self, richtext_field, attributes):
        super().clean_content(richtext_field, attributes)
        width, height = attributes.get('width'), attributes.get('height')
        width = int(width) if str(width).isdigit() else None
        height = int(height) if str(height).isdigit() else None
        dataset = attributes.get('dataset', {})
        orig_width, orig_height = dataset.get('orig_width', 1), dataset.get('orig_height', 1)
        if width is None and height is None:
            width, height = self.initial.get('width'), self.initial.get('height')
        elif width is None:
            width = round(height * orig_width / orig_height)
        elif height is None:
            height = round(width / orig_width * orig_height)
        attributes['width'] = width
        attributes['height'] = height


class RichtextForm(ModelForm):
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
                    InlineImageDialogForm(initial={'width': 300, 'height': 200}),
                    icon='formset/icons/image.svg',
                ),
                controls.HorizontalRule(),
                controls.Separator(),
                controls.ClearFormat(),
                controls.Undo(),
                controls.Redo(),
            ]
        ),
    )

    class Meta:
        model = CascadeElement
        exclude = ['shared_glossary']
        fields_map = {
            'glossary': ['body'],
        }


class RichtextPlugin(BootstrapPluginBase):
    name = _("Richtext")
    parent_classes = None
    allow_children = False
    form = RichtextForm
    change_form_template = 'admin/cmsplugin_cascade/formset/richtext_change_form.html'
    render_template = 'cascade/bootstrap5/richtext.html'

    class Media:
        css = {
            'all': [
                'cascade/admin/bootstrap5/css/richtextplugin.css',
                'cascade/css/richtext.css',
                'finder/css/finder-select.css',
                'formset/css/bootstrap5-extra.css',
            ]
        }
        js = [format_html(
            '<script type="module" src="{}"></script>',
            static('finder/js/finder-select.js')
        )]

    @classmethod
    def get_identifier(cls, instance):
        return format_html('Some content')

    @classmethod
    def translate(cls, translator, instance, target_language, **extra_kwargs):
        if body := instance.glossary.get('body'):
            result = translator.translate_text(
                body,
                target_lang=target_language,
                **extra_kwargs,
            )
            instance.glossary['body'] = result.text
            instance.save(update_fields=['body'])

    def render(self, context, instance, placeholder):
        context = self.super(RichtextPlugin, self).render(context, instance, placeholder)
        context.update({'body': instance.glossary.get('body', '')})
        return context

    def get_field(self, field_path):
        if field_path == 'hyperlink_dialog.anchor':
            return AnchorChoiceField()
        return super().get_field(field_path)

plugin_pool.register_plugin(RichtextPlugin)
