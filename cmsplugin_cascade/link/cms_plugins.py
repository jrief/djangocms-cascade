# -*- coding: utf-8 -*-
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from .models import LinkElement
from .plugin_base import LinkPluginBase
from .forms import LinkForm


class TextLinkPlugin(LinkPluginBase):
    name = _("TextLink")
    model = LinkElement
    form = LinkForm
    render_template = "cms/plugins/link.html"
    text_enabled = True
    allow_children = False
    fields = ('link_content', ('link_type', 'page_link', 'url', 'email'), 'glossary',)
    glossary_fields = (
        PartialFormField('text',
            widgets.TextInput(),
            label=_("Title"),
            help_text=_("Link's Title")
        ),
        LinkPluginBase.LINK_TARGET,
    )

plugin_pool.register_plugin(TextLinkPlugin)
