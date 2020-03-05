from django.core.exceptions import ObjectDoesNotExist
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from entangled.forms import get_related_object
from cmsplugin_cascade.plugin_base import CascadePluginBase
from filer.models.filemodels import File as FilerFileModel


class LinkPluginBase(CascadePluginBase):
    allow_children = False
    parent_classes = []
    require_parent = False
    ring_plugin = 'LinkPluginBase'
    raw_id_fields = ['download_file']
    html_tag_attributes = {'title': 'title', 'target': 'target'}

    class Media:
        js = ['admin/js/jquery.init.js', 'cascade/js/admin/linkplugin.js']

    @classmethod
    def get_link(cls, obj):
        linktype = obj.glossary.get('link_type')
        if linktype == 'exturl':
            return '{ext_url}'.format(**obj.glossary)
        if linktype == 'email':
            return 'mailto:{mail_to}'.format(**obj.glossary)
        if linktype == 'phonenumber':
            return 'tel:{phone_number}'.format(**obj.glossary)

        # otherwise resolve by model
        if linktype == 'cmspage':
            relobj = get_related_object(obj.glossary, 'cms_page')
            if relobj:
                href = relobj.get_absolute_url()
                try:
                    element_ids = relobj.cascadepage.glossary['element_ids']
                    section = obj.glossary['section']
                    href = '{}#{}'.format(href, element_ids[section])
                except (KeyError, ObjectDoesNotExist):
                    pass
                return href
        elif linktype == 'download':
            relobj = get_related_object(obj.glossary, 'download_file')
            if isinstance(relobj, FilerFileModel):
                return relobj.url
        return linktype


class DefaultLinkPluginBase(LinkPluginBase):
    """
    The default `LinkPluginBase` class. It is injected by the class creator in link.config
    """
    ring_plugin = 'LinkPluginBase'


class LinkElementMixin(object):
    """
    A mixin class to convert a CascadeElement into a proxy model for rendering the ``<a>`` element.
    Note that a Link inside the Text Editor Plugin is rendered using ``str(instance)`` rather
    than ``instance.content``.
    """
    def __str__(self):
        return self.plugin_class.get_identifier(self)

    @property
    def link(self):
        return self.plugin_class.get_link(self)

    @property
    def content(self):
        return mark_safe(self.glossary.get('link_content', ''))

    @cached_property
    def download_name(self):
        link_type = self.glossary.get('link_type')
        if link_type == 'download':
            relobj = get_related_object(self.glossary, 'download_file')
            if isinstance(relobj, FilerFileModel):
                return mark_safe(relobj.original_filename)
