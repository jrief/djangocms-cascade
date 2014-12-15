# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import get_model
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.utils import resolve_dependencies


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
    # map field from glossary to these form fields
    glossary_field_map = {'link': ('link_type', 'cms_page', 'ext_url', 'mail_to',)}

    class Media:
        js = resolve_dependencies('cascade/js/admin/linkplugin.js')

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

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.setdefault('base_plugins', [])
        context['base_plugins'].append('django.cascade.LinkPluginBase')
        return super(LinkPluginBase, self).render_change_form(request, context, add, change, form_url, obj)


class LinkElementMixin(object):
    """
    A proxy model for the ``<a>`` element.
    """
    @property
    def link(self):
        return self.plugin_class.get_link(self)

    @property
    def content(self):
        return self.glossary.get('link_content', '')
