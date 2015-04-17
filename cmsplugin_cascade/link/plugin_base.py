# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import get_model
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from cms.utils.compat.dj import python_2_unicode_compatible
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.utils import resolve_dependencies


class LinkPluginBase(CascadePluginBase):
    text_enabled = True
    allow_children = False
    parent_classes = []
    require_parent = False
    glossary_fields = (
        PartialFormField('target',
            widgets.RadioSelect(choices=(('', _("Same Window")), ('_blank', _("New Window")),
                         ('_parent', _("Parent Window")), ('_top', _("Topmost Frame")),)),
            initial='',
            label=_("Link Target"),
            help_text=_("Open Link in other target.")
        ),
    )
    html_tag_attributes = {'target': 'target'}
    # map field from glossary to these form fields
    glossary_field_map = {'link': ('link_type', 'cms_page', 'ext_url', 'mail_to',)}

    class Media:
        js = resolve_dependencies('cascade/js/admin/linkpluginbase.js')

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
                except Model.DoesNotExist:
                    obj._link_model = None
            if obj._link_model:
                return obj._link_model.get_absolute_url()

    def get_ring_bases(self):
        bases = super(LinkPluginBase, self).get_ring_bases()
        bases.append('LinkPluginBase')
        return bases


@python_2_unicode_compatible
class LinkElementMixin(object):
    """
    A mixin class to convert a CascadeElement into a proxy model for rendering the ``<a>`` element.
    """
    def __str__(self):
        """Required representation of this model as a Link inside the Text Editor Plugin"""
        return self.content

    @property
    def link(self):
        return self.plugin_class.get_link(self)

    @property
    def content(self):
        return self.plugin_class.get_identifier(self)
