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
    TYPE_CHOICES = (('cmspage', _("CMS Page")), ('exturl', _("External URL")), ('email', _("Mail To")),)
    link_type = fields.ChoiceField(choices=TYPE_CHOICES, initial='cmspage')
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
        try:
            link_type = instance.glossary['link']['type']
        except (KeyError, AttributeError):
            link_type = 'cmspage'
        if instance:
            cms_page_queryset = Page.objects.drafts().on_site(instance.get_site())
            initial = dict(instance.glossary, link_type=link_type)
        else:
            cms_page_queryset = Page.objects.drafts().on_site(Site.objects.get_current())
            initial = {'link_type': link_type}
        self.base_fields['cms_page'].queryset = cms_page_queryset
        getattr(self, 'set_initial_{0}'.format(link_type))(initial)
        kwargs.update(initial=initial)
        super(LinkForm, self).__init__(*args, **kwargs)

    @classmethod
    def get_link_cmspage(cls, data):
        return {'type': 'cmspage', 'pk': data['cms_page'].pk, 'model': 'cms.Page'}

    @classmethod
    def set_initial_cmspage(cls, initial):
        link = initial.get('link', {})
        try:
            Model = get_model(*link['model'].split('.'))
            initial['cms_page'] = Model.objects.get(pk=link['pk'])
        except (KeyError, ObjectDoesNotExist):
            initial['cms_page'] = None

    @classmethod
    def get_link_exturl(cls, data):
        return {'type': 'exturl', 'url': data['ext_url']}

    @classmethod
    def set_initial_exturl(cls, initial):
        link = initial.get('link', {})
        initial['ext_url'] = link.get('url', '')

    @classmethod
    def get_link_email(cls, data):
        return {'type': 'email', 'email': data['mail_to']}

    @classmethod
    def set_initial_email(cls, initial):
        link = initial.get('link', {})
        initial['mail_to'] = link.get('email', '')


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
        self.initial.setdefault('link_content', '')
