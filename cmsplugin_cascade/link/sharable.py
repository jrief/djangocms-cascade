# -*- coding: utf-8 -*-
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.utils import resolve_dependencies
from cmsplugin_cascade.sharable.forms import SharableGlossaryMixin
from .plugin_base import TextLinkPluginBase
from .models import SharableLinkElement


class LinkPlugin(SharableGlossaryMixin, TextLinkPluginBase):
    model = SharableLinkElement
    fields = ('link_content', ('link_type', 'cms_page', 'ext_url', 'mail_to'), 'glossary',
              ('save_shared_glossary', 'save_as_identifier'), 'shared_glossary',)
    sharable_fields = ('title', 'link', 'target',)

    class Media:
        js = resolve_dependencies('cascade/js/admin/sharablelinkplugin.js')

plugin_pool.register_plugin(LinkPlugin)
