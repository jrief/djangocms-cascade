# -*- coding: utf-8 -*-
import six
from django.forms import widgets
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cms.models import Page
try:
    from djangocms_link.fields import PageSearchField as PageSelectFormField
except ImportError:
    from cms.forms.fields import PageSelectFormField
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.fields import PartialFormField
from .models import LinkElement
from .forms import LinkForm


class TextLinkPlugin(CascadePluginBase):
    name = _("TextLink")
    model = LinkElement
    render_template = "cms/plugins/link.html"
    text_enabled = True
    allow_children = False
    TYPE_CHOICES = (('int', _("Internal")), ('ext', _("External")), ('mail', _("Mail To")),)
    fields = (('link_type', 'page_link', 'url', 'email'), 'context',)
    partial_fields = (
        PartialFormField('text',
            widgets.TextInput(), label=_("Link"), help_text=_("Content of Link")
        ),
    )

    class Media:
        js = ['admin/js/cascade-linkplugin.js']

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
        page_link = PageSelectFormField(queryset=Page.objects.drafts().on_site(self.get_site()),
                                        label=_("page"), required=False)
        # create a Form class on the fly, containing our page_link field
        kwargs.update(form=type('PageLinkForm', (LinkForm,), {'page_link': page_link}))
        return super(TextLinkPlugin, self).get_form(request, obj, **kwargs)

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
        super(TextLinkPlugin, self).save_model(request, obj, form, change)

plugin_pool.register_plugin(TextLinkPlugin)
