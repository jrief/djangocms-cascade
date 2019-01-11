# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps
from django.forms import fields
from django.forms.models import ModelForm
from django.forms.widgets import Select as SelectWidget
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _, get_language
from cms.models import Page
from cmsplugin_cascade.utils import validate_link

try:
    from cms.utils import get_current_site
except ImportError:
    def get_current_site():
        from django.contrib.sites.models import Site
        return Site.objects.get_current()


def format_page_link(*args, **kwargs):
    return format_html("{} ({})", *args, **kwargs)


if 'django_select2' in settings.INSTALLED_APPS:
    from django_select2.forms import HeavySelect2Widget

    class HeavySelectWidget(HeavySelect2Widget):
        @property
        def media(self):
            parent_media = super(HeavySelectWidget, self).media
            # prepend JS snippet to re-add 'jQuery' to the global namespace
            parent_media._js.insert(0, 'cascade/js/admin/jquery.restore.js')
            return parent_media

        def render(self, name, value, attrs=None):
            try:
                page = Page.objects.get(pk=value)
            except (Page.DoesNotExist, ValueError):
                pass
            else:
                language = get_language()
                text = format_page_link(page.get_title(language), page.get_absolute_url(language))
                self.choices.append((value, text))
            html = super(HeavySelectWidget, self).render(name, value, attrs=attrs)
            return html


class LinkSearchField(fields.ChoiceField):
    def __init__(self, *args, **kwargs):
        if 'django_select2' in settings.INSTALLED_APPS:
            widget = HeavySelectWidget(data_view='admin:get_published_pagelist')
        else:
            widget = SelectWidget
        kwargs.setdefault('widget', widget)
        super(LinkSearchField, self).__init__(*args, **kwargs)

    def clean(self, value):
        try:
            return int(value)
        except (TypeError, ValueError):
            pass


class LinkForm(ModelForm):
    """
    Form class to add fake fields for rendering the ModelAdmin's form, which later are used to
    populate the glossary of the model.
    """
    LINK_TYPE_CHOICES = [('cmspage', _("CMS Page")), ('exturl', _("External URL")), ('email', _("Mail To"))]
    link_type = fields.ChoiceField(
        label=_("Link"),
        help_text=_("Type of link"),
    )

    cms_page = LinkSearchField(
        required=False,
        label='',
        help_text=_("An internal link any CMS page of this site"),
    )

    section = fields.ChoiceField(
        required=False,
        label='',
        help_text=_("Page bookmark"),
    )

    ext_url = fields.URLField(
        required=False,
        label='',
        help_text=_("Link onto external page"),
    )

    mail_to = fields.EmailField(
        required=False,
        label='',
        help_text=_("Open Email program with this address"),
    )

    class Meta:
        fields = ('glossary',)

    def __init__(self, data=None, *args, **kwargs):
        instance = kwargs.get('instance')
        default_link_type = {'type': self.LINK_TYPE_CHOICES[0][0]}
        initial = dict(instance.glossary) if instance else {'link': default_link_type}
        initial.update(kwargs.pop('initial', {}))
        initial.setdefault('link', {'type': default_link_type})
        link_type = initial['link']['type']
        self.base_fields['link_type'].choices = self.LINK_TYPE_CHOICES
        self.base_fields['link_type'].initial = link_type
        if data and data.get('shared_glossary'):
            # convert this into an optional field since it is disabled with ``shared_glossary`` set
            self.base_fields['link_type'].required = False
        set_initial_linktype = getattr(self, 'set_initial_{}'.format(link_type), None)
        if 'django_select2' not in settings.INSTALLED_APPS:
            # populate classic Select field for choosing a CMS page
            site = get_current_site()
            choices = [(p.pk, format_page_link(p.get_page_title(), p.get_absolute_url()))
                       for p in Page.objects.drafts().on_site(site)]
            self.base_fields['cms_page'].choices = choices

        if callable(set_initial_linktype):
            set_initial_linktype(initial)
        self._preset_section(data, initial)
        super(LinkForm, self).__init__(data, initial=initial, *args, **kwargs)

    def _preset_section(self, data, initial):
        choices = [(None, _("Page root"))]
        try:
            if data:
                cascade_page = Page.objects.get(pk=data['cms_page']).cascadepage
            else:
                cascade_page = Page.objects.get(pk=initial['link']['pk']).cascadepage
        except (KeyError, ValueError, ObjectDoesNotExist):
            pass
        else:
            for key, val in cascade_page.glossary.get('element_ids', {}).items():
                choices.append((key, val))

        self.base_fields['section'].initial = initial['link'].get('section')
        self.base_fields['section'].choices = choices

    def clean_glossary(self):
        """
        This method rectifies the behavior of JSONFormFieldBase.clean which converts
        the value of empty fields to None, although it shall be an empty dict.
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
                'pk': self.cleaned_data['cms_page'],
            }
            validate_link(self.cleaned_data['link_data'])
        return self.cleaned_data['cms_page']

    def clean_section(self):
        if self.cleaned_data.get('link_type') == 'cmspage':
            self.cleaned_data['link_data']['section'] = self.cleaned_data['section']
        return self.cleaned_data['section']

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
            Model = apps.get_model(*initial['link']['model'].split('.'))
            initial['cms_page'] = Model.objects.get(pk=initial['link']['pk']).pk
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


class TextLinkFormMixin(object):
    """
    To be used in combination with `LinkForm` for easily accessing the field `link_content`.
    """
    def clean(self):
        cleaned_data = super(TextLinkFormMixin, self).clean()
        if self.is_valid():
            cleaned_data['glossary'].update(link_content=cleaned_data['link_content'])
        return cleaned_data
