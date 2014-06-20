# -*- coding: utf-8 -*-
import six
from django.contrib.sites.models import Site
from cms.models import Page
try:
    from djangocms_link.fields import PageSearchField as PageSelectFormField
except ImportError:
    from cms.forms.fields import PageSelectFormField
from cmsplugin_cascade.plugin_base import CascadePluginBase


class LinkPluginBase(CascadePluginBase):
    require_parent = True

    def get_site(self):
        try:
            return self.cms_plugin_instance.page.site
        except AttributeError:
            pass
        try:
            return self.page.site
        except AttributeError:
            return Site.objects.get_current()

    def get_form(self, request, obj=None, **kwargs):
        page_link_field = self.model.page_link.field
        page_link = PageSelectFormField(queryset=Page.objects.drafts().on_site(self.get_site()),
            label=page_link_field.verbose_name, help_text=page_link_field.help_text, required=False)
        # create a Form class on the fly, containing our page_link field
        kwargs.update(form=type('PageLinkForm', (self.form,), {'page_link': page_link}))
        return super(LinkPluginBase, self).get_form(request, obj, **kwargs)

    @classmethod
    def get_identifier(cls, model):
        """
        Returns the descriptive name for the current model
        """
        # TODO: return the line name
        return six.u('')

    def save_model(self, request, obj, form, change):
        # depending on the 'link_type', save the form's data into page_link or text_link
        link_type = form.cleaned_data.get('link_type')
        if link_type == 'int':
            obj.text_link = ''
        elif link_type == 'ext':
            obj.page_link = None
            obj.text_link = form.cleaned_data.get('url')
        elif link_type == 'email':
            obj.page_link = None
            obj.text_link = 'mailto: ' + form.cleaned_data.get('email')
        else:
            obj.page_link = None
            obj.text_link = ''
        super(LinkPluginBase, self).save_model(request, obj, form, change)
