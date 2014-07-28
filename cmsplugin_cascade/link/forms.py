# -*- coding: utf-8 -*-
from django.db.models import get_model
from django.forms import fields
from django.forms import widgets
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
    Form class to add fake fields for rendering the ModelAdmin's form, when later are combined
    with the model data.
    """
    TYPE_CHOICES = (('cmspage', _("CMS Page")), ('exturl', _("External URL")), ('email', _("Mail To")),)
    link_content = fields.CharField(required=False, label=_("Link Content"),
        # replace auto-generated id so that CKEditor automatically transfers the text into this input field
        widget=widgets.TextInput(attrs={'id': 'id_name'}), help_text=_("Content of Link"))
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
        self.base_fields['cms_page'].queryset = Page.objects.drafts().on_site(instance.get_site())
        initial = instance.glossary and instance.glossary.copy() or {}
        initial.setdefault('link_content', '')
        link = initial.get('link', {})
        initial['link_type'] = link.get('type', 'cmspage')
        getattr(self, 'set_initial_{link_type}'.format(**initial))(initial)
        kwargs.update(initial=initial)
        super(LinkForm, self).__init__(*args, **kwargs)

    @classmethod
    def get_link_cmspage(cls, data):
        return {'type': 'cmspage', 'pk': data['cms_page'].pk, 'model': 'cms.Page'}

    @classmethod
    def set_initial_cmspage(cls, initial):
        link = initial.get('link', {})
        Model = get_model(*link['model'].split('.'))
        try:
            initial['cms_page'] = Model.objects.get(pk=link['pk'])
        except ObjectDoesNotExist:
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
