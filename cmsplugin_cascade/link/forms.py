from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.admin.sites import site as admin_site
from django.db.models.fields.related import ManyToOneRel
from django.forms import fields, Media
from django.forms.models import ModelChoiceField
from django.forms.widgets import RadioSelect
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_select2.forms import HeavySelect2Widget

from cms.utils import get_current_site
from cms.models import Page
from entangled.forms import EntangledModelFormMixin
from entangled.utils import get_related_object
from filer.models.filemodels import File as FilerFileModel
from filer.fields.file import AdminFileWidget, FilerFileField

try:
    from phonenumber_field.formfields import PhoneNumberField
except ImportError:
    PhoneNumberField = None


def format_page_link(title, path):
    html = format_html("{} ({})", mark_safe(title), path)
    return html


class PageSelect2Widget(HeavySelect2Widget):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('data_view', 'admin:get_published_pagelist')
        super().__init__(*args, **kwargs)

    @property
    def media(self):
        parent_media = super().media
        # append jquery.init.js to enforce select2.js into the global 'jQuery' namespace
        js = list(parent_media._js) + ['admin/js/jquery.init.js']
        return Media(css=parent_media._css, js=js)

    def render(self, *args, **kwargs):
        # replace self.choices by an empty list to prevent building an optgroup for all pages
        try:
            page = Page.objects.get(pk=kwargs['value'])
        except (Page.DoesNotExist, ValueError, KeyError):
            self.choices = []
        else:
            self.choices = [(kwargs['value'], str(page))]
        return super().render(*args, **kwargs)


class LinkSearchField(ModelChoiceField):
    widget = PageSelect2Widget()

    def __init__(self, *args, **kwargs):
        queryset = Page.objects.public()
        try:
            queryset = queryset.published().on_site(get_current_site()).distinct()
        except:
            pass
        kwargs.setdefault('queryset', queryset)
        super().__init__(*args, **kwargs)

    def clean(self, value):
        self.queryset = Page.objects.public().published().on_site(get_current_site())
        return super().clean(value)


class SectionChoiceField(fields.ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('choices', [('', _("Page Root"))])
        super().__init__(*args, **kwargs)

    def valid_value(self, value):
        """
        The optgroup is adjusted dynamically accroding to the selected cms_page, so always returns True
        and let `LinkForm` validate this value.
        """
        return True


class LinkForm(EntangledModelFormMixin):
    LINK_TYPE_CHOICES = [
        ('cmspage', _("CMS Page")),
        ('download', _("Download File")),
        ('exturl', _("External URL")),
        ('email', _("Mail To")),
    ]
    if PhoneNumberField:
        LINK_TYPE_CHOICES.append(('phonenumber', _("Phone number")))

    link_type = fields.ChoiceField(
        label=_("Link"),
        help_text=_("Type of link"),
    )

    cms_page = LinkSearchField(
        required=False,
        label='',
        help_text=_("An internal link onto any CMS page of this site"),
    )

    section = SectionChoiceField(
        required=False,
        label='',
        help_text=_("Page bookmark"),
    )

    download_file = ModelChoiceField(
        label='',
        queryset=FilerFileModel.objects.all(),
        widget=AdminFileWidget(ManyToOneRel(FilerFileField, FilerFileModel, 'id'), admin_site),
        required=False,
        help_text=_("An internal link onto a file from filer"),
    )

    ext_url = fields.URLField(
        required=False,
        label=_("URL"),
        help_text=_("Link onto external page"),
    )

    mail_to = fields.EmailField(
        required=False,
        label=_("Email"),
        help_text=_("Open Email program with this address"),
    )

    if PhoneNumberField:
        phone_number = PhoneNumberField(
            required=False,
            label=_("Phone Number"),
            help_text=_("International phone number, ex. +1 212 555 2368."),
        )

    link_target = fields.ChoiceField(
        choices=[
            ('', _("Same Window")),
            ('_blank', _("New Window")),
            ('_parent', _("Parent Window")),
            ('_top', _("Topmost Frame")),
        ],
        label=_("Link Target"),
        widget=RadioSelect,
        required=False,
        help_text=_("Open Link in other target."),
    )

    link_title = fields.CharField(
        label=_("Title"),
        required=False,
        help_text=_("Link's Title"),
    )

    class Meta:
        entangled_fields = {'glossary': ['link_type', 'cms_page', 'section', 'download_file', 'ext_url', 'mail_to',
                                         'link_target', 'link_title']}
        if PhoneNumberField:
            entangled_fields['glossary'].append('phone_number')

    def __init__(self, *args, **kwargs):
        link_type_choices = []
        if not getattr(self, 'require_link', True):
            link_type_choices.append(('', _("No Link")))
            self.declared_fields['link_type'].required = False
        link_type_choices.extend(self.LINK_TYPE_CHOICES)
        self.declared_fields['link_type'].choices = link_type_choices
        self.declared_fields['link_type'].initial = link_type_choices[0][0]
        instance = kwargs.get('instance')
        if instance and instance.glossary.get('link_type') == 'cmspage':
            self._preset_section(instance)
        super().__init__(*args, **kwargs)

    def _preset_section(self, instance):
        """
        Field ``cms_page`` may refer onto any CMS page, which itself may contain bookmarks. This method
        creates the list of bookmarks.
        """
        self.base_fields['section'].choices = self.base_fields['section'].choices[:1]
        try:
            cascade_page = get_related_object(instance.glossary, 'cms_page').cascadepage
            for key, val in cascade_page.glossary.get('element_ids', {}).items():
                self.base_fields['section'].choices.append((key, val))
        except (AttributeError, ObjectDoesNotExist):
            pass

    def _post_clean(self):
        super()._post_clean()
        empty_fields = [None, '']
        link_type = self.cleaned_data['glossary'].get('link_type')
        if link_type == 'cmspage':
            if self.cleaned_data['glossary'].get('cms_page', False) in empty_fields:
                error = ValidationError(_("CMS page to link to is missing."), code='required')
                self.add_error('cms_page', error)
        elif link_type == 'download':
            if self.cleaned_data['glossary'].get('download_file', False) in empty_fields:
                error = ValidationError(_("File for download is missing."), code='required')
                self.add_error('download_file', error)
        elif link_type == 'exturl':
            ext_url = self.cleaned_data['glossary'].get('ext_url', False)
            if ext_url in empty_fields:
                error = ValidationError(_("No valid URL provided."), code='required')
                self.add_error('ext_url', error)
        elif link_type == 'email':
            if self.cleaned_data['glossary'].get('mail_to', False) in empty_fields:
                error = ValidationError(_("No email address provided."), code='required')
                self.add_error('mail_to', error)
        elif link_type == 'phonenumber':
            if self.cleaned_data['glossary'].get('phone_number', False) in empty_fields:
                error = ValidationError(_("No phone number provided."), code='required')
                self.add_error('phone_number', error)

    def clean_phone_number(self):
        return str(self.cleaned_data['phone_number'])

    @classmethod
    def unset_required_for(cls, sharable_fields):
        """
        Fields borrowed by `SharedGlossaryAdmin` to build its temporary change form, only are
        required if they are declared in `sharable_fields`. Otherwise just deactivate them.
        """
        if 'link_content' in cls.base_fields and 'link_content' not in sharable_fields:
            cls.base_fields['link_content'].required = False
        if 'link_type' in cls.base_fields and 'link' not in sharable_fields:
            cls.base_fields['link_type'].required = False


class TextLinkFormMixin(EntangledModelFormMixin):
    link_content = fields.CharField(
        label=_("Link Content"),
        widget=fields.TextInput(attrs={'id': 'id_name'}),  # replace auto-generated id so that CKEditor automatically transfers the text into this input field
        help_text=_("Content of Link"),
    )

    class Meta:
        entangled_fields = {'glossary': ['link_content']}
