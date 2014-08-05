# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.db.models import get_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.plugin_base import CascadePluginBase
from .forms import TextLinkForm


class LinkPluginBase(CascadePluginBase):
    glossary_fields = (
        PartialFormField('target',
            widgets.RadioSelect(choices=(('', _("Same Window")), ('_blank', _("New Window")),
                         ('_parent', _("Parent Window")), ('_top', _("Topmost Frame")),)),
            initial='',
            label=_('Link Target'),
            help_text=_("Open Link in other target.")
        ),
    )
    html_tag_attributes = {'target': 'target'}


class TextLinkPluginBase(LinkPluginBase):
    name = _("Link")
    form = TextLinkForm
    render_template = "cms/plugins/link.html"
    text_enabled = True
    allow_children = False
    parent_classes = None
    require_parent = False
    glossary_fields = (
        PartialFormField('title',
            widgets.TextInput(),
            label=_("Title"),
            help_text=_("Link's Title")
        ),
    ) + LinkPluginBase.glossary_fields
    html_tag_attributes = dict(title='title', **LinkPluginBase.html_tag_attributes)
