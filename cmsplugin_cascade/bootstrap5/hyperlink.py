from django.forms.fields import CharField, ChoiceField, EmailField, URLField
from django.forms.models import ModelChoiceField
from django.forms.widgets import EmailInput, RadioSelect, TextInput, URLInput
from django.utils.translation import gettext_lazy as _, get_language, get_language_from_path

from cms.models.contentmodels import PageContent
from cms.models.pagemodel import Page
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.models import CascadeElement, CascadePage, PageContentAnchor

from django_filters import FilterSet, ModelChoiceFilter

from finder.forms.fields import FinderFileField
from finder.forms.widgets import FinderFileSelect
from finder.models.file import FileModel as FinderFileModel

from formset.fieldsmapping import get_related_object
from formset.forms import ModelForm
from formset.widgets import PhoneNumberInput, Selectize


class LinkTypeChoiceField(ChoiceField):
    LINK_TYPE_CHOICES = [
        ('cmspage', _("CMS Page")),
        ('exturl', _("External URL")),
        ('download', _("Download File")),
        ('email', _("Mail To")),
        ('phone', _("Phone Number")),
    ]
    widget = RadioSelect()

    def __init__(self, *args, **kwargs):
        link_type_choices = []
        if kwargs.get('required') is False:
            link_type_choices.append(('', _("No Link")))
        link_type_choices.extend(self.LINK_TYPE_CHOICES)
        kwargs.setdefault('label', _("Link Type"))
        kwargs.setdefault('initial', link_type_choices[0][0])
        super().__init__(choices=link_type_choices, *args, **kwargs)


class PageChoiceField(ModelChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(Page.objects.all(), *args, **kwargs)

    def label_from_instance(self, obj):
        language = get_language()
        return {
            'label': obj.get_title(language),
            'sublabel': f"/{obj.get_path(language)}",
        }


class AnchorFieldFilterSet(FilterSet):
    cms_page = ModelChoiceFilter(
        queryset=CascadePage.objects.all(),
    )

    @property
    def qs(self):
        parent_qs = super().qs
        if cms_page_id := self.request.GET.get('filter-cms_page'):
            cms_page = Page.objects.get(pk=cms_page_id)
            language = get_language_from_path(self.request.GET.get('cms_path'))
            page_content = cms_page.get_content_obj(language=language)
            return parent_qs.filter(content__extended_object=page_content)
        return parent_qs.none()


class AnchorChoiceField(ModelChoiceField):
    widget = Selectize(
        use_filter_set=AnchorFieldFilterSet,
        attrs={
            'df-show': "link_type === 'cmspage'",
            'df-require': "link_type === 'cmspage'",
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(queryset=PageContentAnchor.objects.all(), *args, **kwargs)

    def label_from_instance(self, obj):
        return f"#{obj.identifier}"


class TextLinkForm(ModelForm):
    link_content = CharField(
        label=_("Link Content"),
        widget=TextInput(attrs={'size': 50}),
    )
    link_type = LinkTypeChoiceField()
    cms_page = PageChoiceField(
        label='',
        required=False,
        help_text=_("An internal link onto any CMS page of this site"),
        widget=Selectize(
            search_lookup='page__title__icontains',
            attrs={
                'placeholder': _("CMS-Page"),
                'df-show': "link_type === 'cmspage'",
                'df-require': "link_type === 'cmspage'",
            },
        ),
    )
    anchor = AnchorChoiceField(
        label='',
        required=False,
        empty_label=_("Page Root"),
        help_text=_("Page bookmark"),
    )
    ext_url = URLField(
        label='',
        required=False,
        help_text=_("An external link to any URL outside of this site"),
        widget=URLInput(attrs={
            'size': 50,
            'placeholder': "https://example.com",
            'df-show': "link_type === 'exturl'",
            'df-require': "link_type === 'exturl'"
        }),
    )
    download_file = FinderFileField(
        label='',
        required=False,
        help_text=_("A link to a downloadable file"),
        widget=FinderFileSelect(attrs={
            'df-show': "link_type === 'download'",
            'df-require': "link_type === 'download'",
        }),
    )
    mail_to = EmailField(
        label='',
        required=False,
        help_text=_("A link to an email address"),
        widget=EmailInput(attrs={
            'size': 50,
            'placeholder': "john@example.org",
            'df-show': "link_type === 'email'",
            'df-require': "link_type === 'email'",
        }),
    )
    phone_number = CharField(
        label='',
        required=False,
        help_text=_("A phone number link"),
        widget=PhoneNumberInput(attrs={
            'df-show': "link_type === 'phone'",
            'df-require': "link_type === 'phone'",
        }),
    )

    class Meta:
        model = CascadeElement
        exclude = ['shared_glossary']
        fields_map = {
            'glossary': [
                'link_content', 'link_type',
                'cms_page', 'anchor', 'ext_url', 'download_file', 'mail_to', 'phone_number',
            ],
        }

    def __init__(self, *args, **kwargs):
        link_type_choices = []
        if not getattr(self, 'require_link', True):
            link_type_choices.append(('', _("No Link")))
            self.declared_fields['link_type'].required = False
        # link_type_choices.extend(self.LINK_TYPE_CHOICES)
        # self.declared_fields['link_type'].choices = link_type_choices
        # self.declared_fields['link_type'].initial = link_type_choices[0][0]
        instance = kwargs.get('instance')
        # if instance and instance.glossary.get('link_type') == 'cmspage':
        #     self._preset_section(instance)
        super().__init__(*args, **kwargs)


class TextLinkPlugin(BootstrapPluginBase):
    name = _("Link")
    require_parent = True
    parent_classes = ['BootstrapColumnPlugin']
    allow_children = False
    render_template = 'cascade/bootstrap5/hyperlink.html'
    form = TextLinkForm
    model_mixins = (LinkElementMixin,)

    class Media:
        css = {'all': ['cascade/admin/bootstrap5/css/linkplugin.css']}

    @classmethod
    def get_identifier(cls, instance):
        try:
            return instance.content
        except AttributeError:
            return ''

    @classmethod
    def get_link(cls, obj):
        linktype = obj.glossary.get('link_type')
        if linktype == 'exturl':
            return '{ext_url}'.format(**obj.glossary)
        if linktype == 'email':
            return 'mailto:{mail_to}'.format(**obj.glossary)
        if linktype == 'phone':
            return 'tel:{phone_number}'.format(**obj.glossary)

        # otherwise resolve by model
        href = 'javascript:void(0)'
        if linktype == 'cmspage':
            if cms_page := get_related_object(obj.glossary, 'cms_page'):
                page_content = cms_page.get_content_obj(obj.language)
                if isinstance(page_content, PageContent):
                    href = page_content.get_absolute_url()
                    if anchor := get_related_object(obj.glossary, 'anchor'):
                        href = f'{href}#{anchor.identifier}'
        elif linktype == 'download':
            if file_uuid := obj.glossary.get('download_file'):
                download_file = FinderFileModel.objects.get_inode(id=file_uuid, is_folder=False)
                href = download_file.get_download_url()
        return href


plugin_pool.register_plugin(TextLinkPlugin)
