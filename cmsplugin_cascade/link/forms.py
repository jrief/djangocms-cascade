# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.sites.models import Site
from django.db.models import get_model
from django.forms import fields
from django.forms.widgets import TextInput
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from cms.models import Page
try:
    from .fields import LinkSearchField as LinkSelectFormField

    class PageSelectFormField(LinkSelectFormField):
        search_fields = ['title_set__title__icontains', 'title_set__menu_title__icontains', 'title_set__slug__icontains']
except ImportError:
    from cms.forms.fields import PageSelectFormField


class LinkForm(ModelForm):
    """
    Form class to add fake fields for rendering the ModelAdmin's form, which later are used to
    populate the glossary of the model.
    """
    LINK_TYPE_CHOICES = (('cmspage', _("CMS Page")), ('exturl', _("External URL")), ('email', _("Mail To")),)
    link_type = fields.ChoiceField()
    cms_page = PageSelectFormField(required=False, label='',
        help_text=_("An internal link onto CMS pages of this site"))
    ext_url = fields.URLField(required=False, label='', help_text=_("Link onto external page"))
    mail_to = fields.EmailField(required=False, label='', help_text=_("Open Email program with this address"))

    class Meta:
        fields = ('glossary',)

    def __init__(self, raw_data=None, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = instance and dict(instance.glossary) or {'link': {'type': 'cmspage'}}
        initial.update(kwargs.pop('initial', {}))
        link_type = initial['link']['type']
        self.base_fields['link_type'].choices = self.LINK_TYPE_CHOICES
        self.base_fields['link_type'].initial = link_type
        if raw_data and raw_data.get('shared_glossary'):
            # convert this into an optional field since it is disabled with ``shared_glossary`` set
            self.base_fields['link_type'].required = False
        try:
            site = instance.page.site
        except AttributeError:
            site = Site.objects.get_current()
        self.base_fields['cms_page'].queryset = Page.objects.drafts().on_site(site)
        set_initial_linktype = getattr(self, 'set_initial_{0}'.format(link_type), None)
        if callable(set_initial_linktype):
            set_initial_linktype(initial)
        kwargs.update(initial=initial)
        super(LinkForm, self).__init__(raw_data, *args, **kwargs)

    def clean_glossary(self):
        """
        This method rectifies the behavior of JSONFormFieldBase.clean which
        converts the value of empty fields to None, while it shall be an empty dict.
        """
        glossary = self.cleaned_data['glossary']
        if glossary is None:
            glossary = {}
        return glossary

    def clean(self):
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

    def clean_cms_page(self):
        if self.cleaned_data.get('link_type') == 'cmspage':
            self.cleaned_data['link_data'] = {
                'type': 'cmspage',
                'model': 'cms.Page',
                'pk': self.cleaned_data['cms_page'] and self.cleaned_data['cms_page'].pk or None
            }

    def clean_ext_url(self):
        if self.cleaned_data.get('link_type') == 'exturl':
            self.cleaned_data['link_data'] = {'type': 'exturl', 'url': self.cleaned_data['ext_url']}

    def clean_mail_to(self):
        if self.cleaned_data.get('link_type') == 'email':
            self.cleaned_data['link_data'] = {'type': 'email', 'email': self.cleaned_data['mail_to']}

    def set_initial_none(self, initial):
        pass

    def set_initial_cmspage(self, initial):
        try:
            Model = get_model(*initial['link']['model'].split('.'))
            initial['cms_page'] = Model.objects.get(pk=initial['link']['pk'])
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
    def unset_required_for(cls, sharable_fields):
        """
        Fields borrowed by `SharedGlossaryAdmin` to build its temporary change form, only are
        required if they are declared in `sharable_fields`. Otherwise just deactivate them.
        """
        if 'link' not in sharable_fields:
            cls.base_fields['link_type'].required = False


class TextLinkForm(LinkForm):
    """
    Form class with the additional fake field ``link_content`` used to store the content of pure
    text links.
    """
    link_content = fields.CharField(required=False, label=_("Link Content"),
        # replace auto-generated id so that CKEditor automatically transfers the text into this input field
        widget=TextInput(attrs={'id': 'id_name'}), help_text=_("Content of Link"))

    def clean(self):
        """
        link_content intentionally was rendered outside the glossary field, now move this content
        back to the ``glossary``.
        """
        cleaned_data = super(TextLinkForm, self).clean()
        if self.is_valid():
            cleaned_data['glossary'].update(link_content=cleaned_data['link_content'])
        return cleaned_data
