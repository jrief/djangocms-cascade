from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.admin.sites import site as admin_site
from django.db.models.fields.related import ManyToOneRel
from django.forms import fields, Media, ModelChoiceField
from django.forms.models import ModelForm
from django.forms.widgets import Select as SelectWidget, RadioSelect
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _, get_language
from django_select2.forms import HeavySelect2Widget
from cms.models import Page
from cmsplugin_cascade.utils import validate_link
from entangled.forms import EntangledModelFormMixin, get_related_object
from filer.models.filemodels import File as FilerFileModel
from filer.fields.file import AdminFileWidget, FilerFileField
import requests
from cms.utils import get_current_site


def format_page_link(*args, **kwargs):
    return format_html("{} ({})", *args, **kwargs)


class HeavySelectWidget(HeavySelect2Widget):
    @property
    def media(self):
        parent_media = super(HeavySelectWidget, self).media
        # prepend JS snippet to re-add 'jQuery' to the global namespace
        js = ['cascade/js/admin/jquery.restore.js', *parent_media._js]
        return Media(css=parent_media._css, js=js)

    def Xrender(self, name, value, attrs=None, renderer=None):
        try:
            page = Page.objects.get(pk=value)
        except (Page.DoesNotExist, ValueError):
            pass
        else:
            language = get_language()
            text = format_page_link(page.get_title(language), page.get_absolute_url(language))
            self.choices.append((value, text))
        html = super(HeavySelectWidget, self).render(name, value, attrs, renderer)
        return html


class LinkSearchField(ModelChoiceField):
    widget = HeavySelectWidget(data_view='admin:get_published_pagelist')

    def __init__(self, *args, **kwargs):
        queryset = Page.objects.public().on_site(get_current_site())
        kwargs.setdefault('queryset', queryset)
        super(LinkSearchField, self).__init__(*args, **kwargs)

    def Xclean(self, value):
        value = super().clean(value)
        return value
        try:
            return int(value)
        except (TypeError, ValueError):
            pass


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

    link_type = fields.ChoiceField(
        label=_("Link"),
        choices=LINK_TYPE_CHOICES,
        initial=LINK_TYPE_CHOICES[0][0],
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

    def X__init__(self, data=None, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = dict(instance.glossary) if instance else {}
        # default_link_type = {'link_type': self.LINK_TYPE_CHOICES[0][0]}
        # initial = dict(instance.glossary) if instance else default_link_type
        # initial.update(kwargs.pop('initial', {}))
        # initial.setdefault('link', {'type': default_link_type})
        # link_type = initial['link']['type']
        # self.base_fields['link_type'].choices = self.LINK_TYPE_CHOICES
        # self.base_fields['link_type'].initial = link_type
        if data and data.get('shared_glossary'):
            # convert this into an optional field since it is disabled with ``shared_glossary`` set
            self.base_fields['link_type'].required = False
        try:
            set_initial_linktype = getattr(self, 'set_initial_{link_type}'.format(**initial))
        except KeyError:
            set_initial_linktype = None
        if 'django_select2' not in settings.INSTALLED_APPS:
            # populate classic Select field for choosing a CMS page
            site = get_current_site()
            choices = [(p.pk, format_page_link(p.get_page_title(), p.get_absolute_url()))
                       for p in Page.objects.drafts().on_site(site)]
            self.base_fields['cms_page'].choices = choices

        if callable(set_initial_linktype):
            set_initial_linktype(initial)
        #self._preset_section(data, initial)
        # self.base_fields['download_file'].widget = AdminFileWidget(ManyToOneRel(FilerFileField, FilerFileModel, 'id'), admin_site)
        super().__init__(data, initial=initial, *args, **kwargs)

    def __init__(self, *args, **kwargs):
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

    def clean(self):
        cleaned_data = super().clean()
        link_type = cleaned_data.get('link_type')
        error = None
        if link_type == 'cmspage':
            if cleaned_data['cms_page'] is None:
                error = ValidationError(_("CMS page to link to is missing."))
                self.add_error('cms_page', error)
        elif link_type == 'download':
            if cleaned_data['download_file'] is None:
                error = ValidationError(_("File for download is missing."))
                self.add_error('download_file', error)
        elif link_type == 'exturl':
            ext_url = cleaned_data['ext_url']
            if ext_url:
                try:
                    response = requests.head(ext_url, allow_redirects=True)
                    if response.status_code != 200:
                        error = ValidationError(_("No external page found on {url}.").format(url=ext_url))
                except Exception as exc:
                    error = ValidationError(_("Failed to connect to {url}.").format(url=ext_url))
            else:
                error = ValidationError(_("No external URL provided."))
            if error:
                self.add_error('ext_url', error)
        if error:
            raise error
        return cleaned_data

    def Xclean_glossary(self):
        """
        This method rectifies the behavior of JSONFormFieldBase.clean which converts
        the value of empty fields to None, although it shall be an empty dict.
        """
        glossary = self.cleaned_data['glossary']
        if glossary is None:
            glossary = {}
        return glossary

    def Xclean(self):
        cleaned_data = super(LinkForm, self).clean()
        if self.is_valid():
            if 'link_data' in cleaned_data:
                cleaned_data['glossary'].update(link=cleaned_data['link_data'])
                del self.cleaned_data['link_data']
            elif 'link_type' in cleaned_data:
                cleaned_data['glossary'].update(link={'type': cleaned_data['link_type']})
            else:
                cleaned_data['glossary'].update(link={'type': 'none'})
        return cleaned_data

    def Xclean_cms_page(self):
        if self.cleaned_data.get('link_type') == 'cmspage':
            validate_link(self.cleaned_data['cms_page'])
        return self.cleaned_data['cms_page']

    def Xclean_section(self):
        # if self.cleaned_data.get('link_type') == 'cmspage':
        #     self.cleaned_data['cms_page']['section'] = self.cleaned_data['section']
        return self.cleaned_data['section']

    def Xclean_download_file(self):
        if (self.cleaned_data.get('link_type') == 'download'
            and isinstance(self.cleaned_data['download_file'], FilerFileModel)):
            self.cleaned_data['link_data'] = {
                'model': 'filer.File',
                'pk': self.cleaned_data['download_file'].id,
            }
            return self.cleaned_data['download_file']

    def clean_ext_url(self):
        if self.cleaned_data.get('link_type') == 'exturl':
            self.cleaned_data['link_data'] = {'type': 'exturl', 'url': self.cleaned_data['ext_url']}
        return self.cleaned_data['ext_url']

    def clean_mail_to(self):
        if self.cleaned_data.get('link_type') == 'email':
            self.cleaned_data['link_data'] = {'type': 'email', 'email': self.cleaned_data['mail_to']}
        return self.cleaned_data['mail_to']

    def set_initial_none(self, initial):
        pass

    def set_initial_cmspage(self, initial):
        try:
            # check if that page still exists, otherwise return nothing
            Model = apps.get_model(initial['cms_page']['model'])
            initial['cms_page'] = Model.objects.get(pk=initial['cms_page']['pk']).pk
        except (KeyError, ObjectDoesNotExist):
            pass

    def set_initial_download(self, initial):
        try:
            # check if that page still exists, otherwise return nothing
            Model = apps.get_model(*initial['link']['model'].split('.'))
            initial['download_file'] = Model.objects.get(pk=initial['link']['pk']).pk
        except (KeyError, ObjectDoesNotExist):
            pass

    def set_initial_exturl(self, initial):
        try:
            initial['ext_url'] = initial['link']['url']
        except KeyError:
            pass

    def set_initial_email(self, initial):
        try:
            initial['mail_to'] = initial['link']['email']
        except KeyError:
            pass

    @classmethod
    def get_form_class(cls):
        """
        Hook to return a form class for editing a CMSPlugin inheriting from ``LinkPluginBase``.
        """
        return cls

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


class X_TextLinkFormMixin(object):
    """
    To be used in combination with `LinkForm` for easily accessing the field `link_content`.
    """
    def clean(self):
        cleaned_data = super().clean()
        if self.is_valid():
            cleaned_data['glossary'].update(link_content=cleaned_data['link_content'])
        return cleaned_data
