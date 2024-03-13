from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

from entangled.utils import get_related_object
from cms.models.contentmodels import PageContent
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
        css = {'all': ['cascade/css/admin/linkplugin.css']}
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
            href = 'javascript:void(0)'
            if cms_page := get_related_object(obj.glossary, 'cms_page'):
                page_content = cms_page.get_content_obj(obj.language)
                if isinstance(page_content, PageContent):
                    href = page_content.get_absolute_url()
                    if section := obj.glossary.get('section'):
                        href = f'{href}#{section}'
            return href
        elif linktype == 'download':
            relobj = get_related_object(obj.glossary, 'download_file')
            if isinstance(relobj, FilerFileModel):
                return relobj.url
            else:
                return 'javascript:void(0)'
        return linktype


class DefaultLinkPluginBase(LinkPluginBase):
    """
    The default `LinkPluginBase` class. It is injected by the class creator in link.config
    """
    ring_plugin = 'LinkPluginBase'


class LinkElementMixin:
    """
    A mixin class to convert a CascadeElement into a proxy model for rendering the ``<a>`` element.
    Note that a Link inside the Text Editor Plugin is rendered using ``str(instance)`` rather
    than ``instance.content``.
    """
    def __str__(self):
        return self.plugin_class.get_identifier(self)

    @cached_property
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
