# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.forms import widgets
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.link.forms import LinkForm
from filer.models.filemodels import File as FilerFileModel


class LinkPluginBase(CascadePluginBase):
    allow_children = False
    parent_classes = []
    require_parent = False
    ring_plugin = 'LinkPluginBase'
    raw_id_fields = ['download_file']

    class Media:
        js = ['cascade/js/admin/linkplugin.js']

    target = GlossaryField(
        widgets.RadioSelect(choices=[
            ('', _("Same Window")),
            ('_blank', _("New Window")),
            ('_parent', _("Parent Window")),
            ('_top', _("Topmost Frame")),
        ]),
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
    glossary_field_map = {'link': ('link_type', 'cms_page', 'section', 'download_file', 'ext_url', 'mail_to',)}

    @classmethod
    def get_link(cls, obj):
        link = obj.glossary.get('link', {})
        linktype = link.get('type')
        if linktype == 'exturl':
            return '{url}'.format(**link)
        if linktype == 'email':
            return 'mailto:{email}'.format(**link)

        # otherwise resolve by model
        if obj.link_model:
            if linktype == 'download':
                return obj.link_model.url if isinstance(obj.link_model, FilerFileModel) else None
            href = obj.link_model.get_absolute_url()
            if 'section' in link:
                try:
                    element_ids = obj.link_model.cascadepage.glossary['element_ids']
                    href = '{}#{}'.format(href, element_ids[link['section']])
                except (KeyError, ObjectDoesNotExist):
                    pass
            return href

    def get_form(self, request, obj=None, **kwargs):
        kwargs.setdefault('form', LinkForm.get_form_class())
        return super(LinkPluginBase, self).get_form(request, obj, **kwargs)


class DefaultLinkPluginBase(LinkPluginBase):
    """
    The default `LinkPluginBase` class. It is injected by the class creator in link.config
    """
    fields = (('link_type', 'cms_page', 'section', 'download_file', 'ext_url', 'mail_to',), 'glossary',)
    ring_plugin = 'LinkPluginBase'


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

    @cached_property
    def link_model(self):
        try:
            link = self.glossary['link']
            Model = apps.get_model(*link['model'].split('.'))
            return Model.objects.get(pk=link['pk'])
        except (KeyError, LookupError):
            return
        except Model.DoesNotExist:  # catch separately, 'Model' may be unassigned yet
            return

    @cached_property
    def download_name(self):
        link = self.glossary.get('link', {})
        if link.get('type') == 'download' and isinstance(self.link_model, FilerFileModel):
            return mark_safe(self.link_model.original_filename)
