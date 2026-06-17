from django.forms.fields import CharField, ChoiceField, EmailField, URLField
from django.forms.models import ModelChoiceField
from django.forms.widgets import EmailInput, RadioSelect, TextInput, URLInput
from django.utils.translation import gettext_lazy as _, get_language, get_language_from_path

from cms.models.pagemodel import Page
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.models import CascadeElement, CascadePage, PageAnchor

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
    def __init__(self, queryset=None, widget=None, *args, **kwargs):
        if queryset is None:
            queryset = Page.objects.all()
        if widget is None:
            widget = Selectize(
                search_lookup='page__title__icontains',
                attrs={'placeholder': _("CMS-Page")},
            )
        super().__init__(queryset, widget=widget, *args, **kwargs)

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
            page_url = cms_page.get_url_obj(language=language)
            return parent_qs.filter(page_url=page_url)
        return parent_qs.none()


class AnchorChoiceField(ModelChoiceField):
    widget = Selectize(
        use_filter_set=AnchorFieldFilterSet,
        attrs={'df-show': "link_type === 'cmspage'"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(queryset=PageAnchor.objects.all(), *args, **kwargs)

    def label_from_instance(self, obj):
        return f"#{obj.identifier}"


class HyperlinkForm(ModelForm):
    link_type = LinkTypeChoiceField()
    cms_page = PageChoiceField(
        label=_("CMS Page"),
        required=False,
        help_text=_("An internal link onto any CMS page of this site"),
        widget=Selectize(
            search_lookup='page__title__icontains',
            attrs={
                'placeholder': _("CMS-Page"),
                'df-show': ".link_type === 'cmspage'",
                'df-require': ".link_type === 'cmspage'",
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
        label=_("External URL"),
        required=False,
        help_text=_("An external link to any URL outside of this site"),
        widget=URLInput(attrs={
            'size': 50,
            'placeholder': "https://example.com",
            'df-show': ".link_type === 'exturl'",
            'df-require': ".link_type === 'exturl'"
        }),
    )
    download_file = FinderFileField(
        label=_("Downloadable File"),
        required=False,
        help_text=_("A link to a downloadable file"),
        widget=FinderFileSelect(attrs={
            'df-show': ".link_type === 'download'",
            'df-require': ".link_type === 'download'",
        }),
    )
    mail_to = EmailField(
        label=_("Email Address"),
        required=False,
        help_text=_("A link to an email address"),
        widget=EmailInput(attrs={
            'size': 50,
            'placeholder': "john@example.org",
            'df-show': ".link_type === 'email'",
            'df-require': ".link_type === 'email'",
        }),
    )
    phone_number = CharField(
        label=_("Phone Number"),
        required=False,
        help_text=_("A phone number link"),
        widget=PhoneNumberInput(attrs={
            'df-show': ".link_type === 'phone'",
            'df-require': ".link_type === 'phone'",
        }),
    )

    class Meta:
        model = CascadeElement
        exclude = ['shared_glossary']
        fields_map = {
            'glossary': ['link_type', 'cms_page', 'anchor', 'ext_url', 'download_file', 'mail_to', 'phone_number'],
        }

    def __init__(self, *args, **kwargs):
        link_type_choices = []
        if not getattr(self, 'require_link', True):
            link_type_choices.append(('', _("No Link")))
            self.declared_fields['link_type'].required = False
        super().__init__(*args, **kwargs)


class TextLinkForm(HyperlinkForm):
    link_content = CharField(
        label=_("Link Content"),
        widget=TextInput(attrs={'size': 50}),
    )

    class Meta(HyperlinkForm.Meta):
        fields_map = {
            'glossary': ['link_content'] + HyperlinkForm.Meta.fields_map['glossary']
        }


class HyperlinkPluginMixin:
    class Media:
        css = {'all': ['cascade/admin/bootstrap5/css/hyperlinkplugin.css']}

    @classmethod
    def get_link(cls, obj):
        linktype = obj.glossary.get('link_type')
        if not linktype:
            return ''
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
                if page_url := cms_page.get_url_obj(obj.language):
                    href = page_url.get_absolute_url()
                    try:
                        anchor = page_url.anchors.get(id=obj.glossary['anchor']['pk'])
                        href += f'#{anchor.identifier}'
                    except (PageAnchor.DoesNotExist, TypeError, KeyError):
                        pass
        elif linktype == 'download':
            if file_uuid := obj.glossary.get('download_file'):
                download_file = FinderFileModel.objects.get_inode(id=file_uuid, is_folder=False)
                href = download_file.get_download_url()
        return href


class TextLinkPlugin(HyperlinkPluginMixin, BootstrapPluginBase):
    name = _("Link")
    require_parent = True
    parent_classes = ['BootstrapColumnPlugin']
    render_template = 'cascade/bootstrap5/textlink.html'
    form = TextLinkForm
    model_mixins = (LinkElementMixin,)

    @classmethod
    def get_identifier(cls, instance):
        try:
            return instance.content
        except AttributeError:
            return ''


plugin_pool.register_plugin(TextLinkPlugin)
