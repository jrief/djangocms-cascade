from django.forms.fields import CharField, ChoiceField, URLField
from django.forms.widgets import Select, TextInput, URLInput
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.models import CascadeElement, CascadePageContent, PageContentAnchor

from finder.forms.fields import FinderFileField
from finder.forms.widgets import FinderFileSelect

from formset.forms import ModelForm
from formset.formfields.richtext import RichTextField
from formset.richtext import controls, dialogs
from formset.widgets import Selectize
from formset.widgets.richtext import RichTextarea

from cmsplugin_cascade.bootstrap5.link import PageChoiceField


class CustomHyperlinkDialogForm(dialogs.RichtextDialogForm):
    title = _("Edit Link")
    extension = 'custom_hyperlink'
    extension_script = 'cascade/admin/tiptap-extensions/custom_hyperlink.js'
    plugin_type = 'mark'
    prefix = 'custom_hyperlink_dialog'

    text = CharField(
        label=_("Link Text"),
        widget=TextInput(attrs={
            'richtext-selection': True,
            'size': 50,
        })
    )
    link_type = ChoiceField(
        label=_("Link Type"),
        choices=[
            ('external', _("External URL")),
            ('internal', _("Internal Page")),
            ('download', _("Downloadable File")),
        ],
        initial='internal',
        widget=Select(attrs={
            'richtext-map-from': '{value: attributes.href ? "external" : (attributes.cms_page ? "internal" : "download")}',
        }),
    )
    url = URLField(
        label="External URL",
        widget=URLInput(attrs={
            'size': 50,
            'richtext-map-to': '{href: elements.link_type.value == "external" ? elements.url.value : ""}',
            'richtext-map-from': 'href',
            'df-show': ".link_type == 'external'",
            'df-require': ".link_type == 'external'",
        }),
    )
    cms_page = PageChoiceField(
        label="Internal Page",
        widget=Selectize(attrs={
            'richtext-map-to': '{cms_page_id: elements.link_type.value == "internal" ? elements.cms_page.value : ""}',
            'richtext-map-from': 'cms_page_id',
            'df-show': ".link_type == 'internal'",
            'df-require': ".link_type == 'internal'",
        }),
    )
    download_file = FinderFileField(
        required=False,
        label='',
        help_text=_("A link to a downloadable file"),
        widget=FinderFileSelect(attrs={
            # 'richtext-map-to': '{selected_file: elements.link_type.value == "download" ? elements.download_file.value : ""}',
            'richtext-map-from': '{dataset: {file_id: attributes.download_file}}',
            'df-show': ".link_type === 'download'",
        }),
    )


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
                    CustomHyperlinkDialogForm(),
                    icon='formset/icons/link.svg',
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
        css = {'all': ['cascade/admin/bootstrap5/css/richtextplugin.css', 'finder/css/finder-select.css']}
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

plugin_pool.register_plugin(RichtextPlugin)
