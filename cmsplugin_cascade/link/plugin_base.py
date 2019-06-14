from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from cmsplugin_cascade.plugin_base import CascadePluginBase
from filer.models.filemodels import File as FilerFileModel
from entangled.forms import get_related_object


class LinkPluginBase(CascadePluginBase):
    allow_children = False
    parent_classes = []
    require_parent = False
    ring_plugin = 'LinkPluginBase'
    raw_id_fields = ['download_file']

    class Media:
        js = ['cascade/js/admin/linkplugin.js']

    html_tag_attributes = {'title': 'title', 'target': 'target'}
    # map field from glossary to these form fields
    # glossary_field_map = {'link': ('link_type', 'cms_page', 'section', 'download_file', 'ext_url', 'mail_to',)}

    @classmethod
    def get_link(cls, obj):
        linktype = obj.glossary.get('link_type')
        if linktype == 'exturl':
            return '{ext_url}'.format(**obj.glossary)
        if linktype == 'email':
            return 'mailto:{mail_to}'.format(**obj.glossary)

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

    def get_form(self, request, obj=None, **kwargs):
        from cmsplugin_cascade.link.config import LinkForm as MandatoryLinkForm, VoluntaryLinkForm

        if getattr(self, 'link_required', True):
            LinkForm = MandatoryLinkForm  # the default
        else:
            LinkForm = VoluntaryLinkForm  # link type can be "No Link"
        if 'form' in kwargs:
            kwargs['form'] = type(kwargs['form'].__name__, (LinkForm, kwargs['form']), {})
        else:
            kwargs['form'] = LinkForm
        return super().get_form(request, obj, **kwargs)


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
    def Xlink_model(self):
        """deprecated"""
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
        link_type = self.glossary.get('link_type')
        if link_type == 'download':
            relobj = get_related_object(self.glossary, 'download_file')
            if isinstance(relobj.link_model, FilerFileModel):
                return mark_safe(relobj.original_filename)
