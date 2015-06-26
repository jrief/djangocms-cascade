# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from cms.utils.compat.dj import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.utils import resolve_dependencies
from .plugin_base import LinkPluginBase, LinkElementMixin
from .forms import TextLinkForm


@python_2_unicode_compatible
class TextLinkElementMixin(LinkElementMixin):
    def __str__(self):
        """
        A Link inside the Text Editor Plugin are rendered as `str(instance)` rather
        than `instance.content`. Therefore the string representation for this model
        must be overridden.
        """
        return self.content


class TextLinkPlugin(LinkPluginBase):
    name = _("Link")
    form = TextLinkForm
    model_mixins = (TextLinkElementMixin,)
    render_template = 'cascade/link/text-link.html'
    glossary_fields = (
        PartialFormField('title',
            widgets.TextInput(),
            label=_("Title"),
            help_text=_("Link's Title")
        ),
    ) + LinkPluginBase.glossary_fields
    html_tag_attributes = dict(title='title', **LinkPluginBase.html_tag_attributes)
    fields = ('link_content', ('link_type', 'cms_page', 'ext_url', 'mail_to'), 'glossary',)

    class Media:
        js = resolve_dependencies('cascade/js/admin/linkplugin.js')

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(obj.glossary.get('link_content', ''))

plugin_pool.register_plugin(TextLinkPlugin)
