# -*- coding: utf-8 -*-
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.common.forms import SharableGlossaryMixin
from .models import LinkElement
from .plugin_base import LinkPluginBase
from .forms import TextLinkForm


class LinkPlugin(SharableGlossaryMixin, LinkPluginBase):
    name = _("Link")
    model = LinkElement
    form = TextLinkForm
    render_template = "cms/plugins/link.html"
    text_enabled = True
    allow_children = False
    fields = ('link_content', ('link_type', 'cms_page', 'ext_url', 'mail_to'), 'glossary',
              ('save_shared_glossary', 'save_as_identifier'), 'shared_glossary',)
    glossary_fields = (
        PartialFormField('title',
            widgets.TextInput(),
            label=_("Title"),
            help_text=_("Link's Title")
        ),
    ) + LinkPluginBase.glossary_fields
    sharable_fields = ('title', 'link', 'target',)
    html_tag_attributes = dict(title='title', **LinkPluginBase.html_tag_attributes)
    parent_classes = None
    require_parent = False

    class Media:
        js = ['admin/js/cascade-linkplugin.js', 'admin/js/cascade-sharable-linkplugin.js', 'admin/js/cascade-textlinkplugin.js']

plugin_pool.register_plugin(LinkPlugin)
