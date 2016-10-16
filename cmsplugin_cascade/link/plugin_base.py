# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.forms import widgets
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.utils import resolve_dependencies
from .forms import LinkForm


class LinkPluginBase(CascadePluginBase):
    text_enabled = True
    allow_children = False
    parent_classes = []
    require_parent = False
    target = GlossaryField(
        widgets.RadioSelect(choices=(('', _("Same Window")), ('_blank', _("New Window")),
                     ('_parent', _("Parent Window")), ('_top', _("Topmost Frame")),)),
        initial='',
        label=_("Link Target"),
        help_text=_("Open Link in other target.")
    )

    title = GlossaryField(
        widgets.TextInput(),
        label=_("Title"),
        help_text=_("Link's Title")
    )

    html_tag_attributes = {'title': 'title', 'target': 'target'}
    # map field from glossary to these form fields
    glossary_field_map = {'link': ('link_type', 'cms_page', 'section', 'ext_url', 'mail_to',)}

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
                Model = apps.get_model(*link['model'].split('.'))
                try:
                    obj._link_model = Model.objects.get(pk=link['pk'])
                except Model.DoesNotExist:
                    obj._link_model = None
            if obj._link_model:
                href = obj._link_model.get_absolute_url()
                if 'section' in link:
                    try:
                        element_ids = obj._link_model.cascadepage.glossary['element_ids']
                        href = '{}#{}'.format(href, element_ids[link['section']])
                    except (KeyError, ObjectDoesNotExist):
                        pass
                return href

    def get_ring_bases(self):
        bases = super(LinkPluginBase, self).get_ring_bases()
        bases.append('LinkPluginBase')
        return bases

    def get_form(self, request, obj=None, **kwargs):
        kwargs.setdefault('form', LinkForm.get_form_class())
        return super(LinkPluginBase, self).get_form(request, obj, **kwargs)


class DefaultLinkPluginBase(LinkPluginBase):
    """
    The default `LinkPluginBase` class. It is injected by the class creator in link.config
    """
    fields = (('link_type', 'cms_page', 'section', 'ext_url', 'mail_to',), 'glossary',)

    class Media:
        js = resolve_dependencies('cascade/js/admin/defaultlinkplugin.js')


@python_2_unicode_compatible
class LinkElementMixin(object):
    """
    A mixin class to convert a CascadeElement into a proxy model for rendering the ``<a>`` element.
    Note that a Link inside the Text Editor Plugin is rendered using ``str(instance)`` rather
    than ``instance.content``.
    """
    def __str__(self):
        return self.content

    @property
    def link(self):
        return self.plugin_class.get_link(self)

    @property
    def content(self):
        return mark_safe(self.glossary.get('link_content', ''))
