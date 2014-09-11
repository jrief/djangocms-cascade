# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from django.db.models import get_model
from django.core.exceptions import ObjectDoesNotExist
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

    @classmethod
    def get_link(cls, obj):
        link = obj.glossary.get('link', {})
        linktype = link.get('type')
        if linktype == 'exturl':
            return '{url}'.format(**link)
        if linktype == 'email':
            return 'mailto:{email}'.format(**link)
        # otherwise try to resolve by model
        if 'model' in link and 'pk' in link:
            if not hasattr(obj, '_link_model'):
                Model = get_model(*link['model'].split('.'))
                try:
                    obj._link_model = Model.objects.get(pk=link['pk'])
                except ObjectDoesNotExist:
                    obj._link_model = None
            if obj._link_model:
                return obj._link_model.get_absolute_url()


class TextLinkPluginBase(LinkPluginBase):
    name = _("Link")
    form = TextLinkForm
    render_template = 'cascade/plugins/link.html'
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
