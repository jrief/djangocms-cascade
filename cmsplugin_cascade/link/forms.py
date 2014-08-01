# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from django.db.models import get_model
from django.forms import fields
from django.forms.widgets import TextInput
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from cms.models import Page
try:
    from .fields import PageSearchField as PageSelectFormField
except ImportError:
    from cms.forms.fields import PageSelectFormField
from .models import LinkElement


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
        model = LinkElement
        fields = ('glossary',)

    class Media:
        js = ['admin/js/cascade-linkplugin.js']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = instance and dict(instance.glossary) or {'link': {'type': 'cmspage'}}
        initial.update(kwargs.pop('initial', {}))
        link_type = initial['link']['type']
        if instance:
            cms_page_queryset = Page.objects.drafts().on_site(instance.get_site())
        else:
            cms_page_queryset = Page.objects.drafts().on_site(Site.objects.get_current())
        self.base_fields['link_type'].choices = self.LINK_TYPE_CHOICES
        self.base_fields['link_type'].initial = link_type
        self.base_fields['cms_page'].queryset = cms_page_queryset
        getattr(self, 'set_initial_{0}'.format(link_type))(initial)
        kwargs.update(initial=initial)
        super(LinkForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(LinkForm, self).clean()
        if 'link_data' in cleaned_data:
            cleaned_data['glossary'].update(link=cleaned_data['link_data'])
            del self.cleaned_data['link_data']
        else:
            cleaned_data['glossary'].update(link={'type': 'none'})
        return cleaned_data

    def clean_cms_page(self):
        if self.cleaned_data['link_type'] == 'cmspage':
            self.cleaned_data['link_data'] = {
                'type': 'cmspage',
                'model': 'cms.Page',
                'pk': self.cleaned_data['cms_page'] and self.cleaned_data['cms_page'].pk or None
            }

    def clean_ext_url(self):
        if self.cleaned_data['link_type'] == 'exturl':
            self.cleaned_data['link_data'] = {'type': 'exturl', 'url': self.cleaned_data['ext_url']}

    def clean_mail_to(self):
        if self.cleaned_data['link_type'] == 'email':
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


class TextLinkForm(LinkForm):
    """
    Form class with the additional fake field ``link_content`` used to store the content of pure
    text links.
    """
    link_content = fields.CharField(required=False, label=_("Link Content"),
        # replace auto-generated id so that CKEditor automatically transfers the text into this input field
        widget=TextInput(attrs={'id': 'id_name'}), help_text=_("Content of Link"))

    def __init__(self, *args, **kwargs):
        super(TextLinkForm, self).__init__(*args, **kwargs)
        self.base_fields['link_type'].initial = 'cmspage'
        #self.initial.setdefault('link_content', '')

    def clean(self):
        """
        link_content intentionally was rendered outside the glossary field, move its content
        back to the ``glossary``.
        """
        cleaned_data = super(TextLinkForm, self).clean()
        cleaned_data['glossary'].update(link_content=cleaned_data['link_content'])
        return cleaned_data
