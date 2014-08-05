# -*- coding: utf-8 -*-
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.utils import resolve_dependencies
from .plugin_base import TextLinkPluginBase
from .models import SimpleLinkElement


class LinkPlugin(TextLinkPluginBase):
    model = SimpleLinkElement
    fields = ('link_content', ('link_type', 'cms_page', 'ext_url', 'mail_to'), 'glossary',)

    class Media:
        js = resolve_dependencies('cascade/js/admin/simplelinkplugin.js')

plugin_pool.register_plugin(LinkPlugin)
