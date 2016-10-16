# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _, get_language_from_request
from cms.plugin_pool import plugin_pool
from cms.models.pagemodel import Page
from cmsplugin_cascade.fields import GlossaryField
from .plugin_base import BootstrapPluginBase


class BootstrapSecondaryMenuPlugin(BootstrapPluginBase):
    """
    Use this plugin to display a secondary menu in arbitrary locations.
    This renders links onto  all CMS pages, which are children of the selected Page Id.
    """
    name = _("Secondary Menu")
    default_css_class = 'list-group'
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    allow_children = False
    render_template = 'cascade/bootstrap3/secmenu-list-group.html'

    page_id = GlossaryField(
        widgets.Select(choices=()),
        label=_("CMS Page Id"),
        help_text=_("Select a CMS page with a given unique Id (in advanced settings).")
    )

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapSecondaryMenuPlugin, cls).get_identifier(obj)
        content = obj.glossary.get('page_id', '')
        return format_html('{0}{1}', identifier, content)

    def get_form(self, request, obj=None, **kwargs):
        lang = get_language_from_request(request)
        choices = {}
        for page in Page.objects.filter(reverse_id__isnull=False).order_by('publisher_is_draft'):
            if page.reverse_id not in choices:
                choices[page.reverse_id] = page.get_title(lang)
        self.glossary_fields[0].widget.choices = choices.items()
        return super(BootstrapSecondaryMenuPlugin, self).get_form(request, obj, **kwargs)

plugin_pool.register_plugin(BootstrapSecondaryMenuPlugin)
