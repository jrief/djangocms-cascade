# -*- coding: utf-8 -*-
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from .models import LinkElement
from .plugin_base import LinkPluginBase
from .forms import LinkForm


class LinkPlugin(LinkPluginBase):
    name = _("Link")
    model = LinkElement
    form = LinkForm
    render_template = "cms/plugins/link.html"
    text_enabled = True
    allow_children = False
    fields = ('link_content', ('link_type', 'cms_page', 'ext_url', 'mail_to'), 'glossary',)
    glossary_fields = (
        PartialFormField('title',
            widgets.TextInput(),
            label=_("Title"),
            help_text=_("Link's Title")
        ),
    ) + LinkPluginBase.glossary_fields
    html_tag_attributes = dict(title='title', **LinkPluginBase.html_tag_attributes)
    parent_classes = None
    require_parent = False

    def save_model(self, request, obj, form, change):
        obj.glossary.update(link_content=form.cleaned_data.get('link_content', ''))
        super(LinkPlugin, self).save_model(request, obj, form, change)

plugin_pool.register_plugin(LinkPlugin)
