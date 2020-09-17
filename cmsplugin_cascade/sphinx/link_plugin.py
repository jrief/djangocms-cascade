import io
import json
import os
from django.conf import settings
from django.forms import fields
from django.utils.translation import gettext_lazy as _
from django_select2.forms import Select2Widget
from cms.models.pagemodel import Page
from cmsplugin_cascade.link.plugin_base import LinkPluginBase
from cmsplugin_cascade.link.forms import LinkForm


class DocumentationSelect2Widget(Select2Widget):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs=attrs, renderer=None)
        return html


def get_documents_map():
    docsmap_file = os.path.join(settings.SPHINX_DOCS_ROOT, 'docsmap.json')
    if not os.path.exists(docsmap_file):
        return ()
    with io.open(docsmap_file) as fh:
        docs_map = json.load(fh, encoding='utf-8')
    result = []
    for path, title in docs_map.items():
        bits = path.split('/')
        if len(bits) == 2 and bits[1] == 'index':
            result.append((bits[0], title))
        elif bits[0] != 'index':
            result.append((path, title))
    return result


class SphinxDocsLinkForm(LinkForm):
    LINK_TYPE_CHOICES = [
        ('cmspage', _("CMS Page")),
        ('documentation', _("Documentation")),
        ('exturl', _("External URL")),
        ('email', _("Mail To")),
    ]

    documentation = fields.ChoiceField(
        required=False,
        label='',
        choices=get_documents_map(),
        widget=Select2Widget,
        help_text=_("An internal link onto a documentation page"),
    )

    def clean_documentation(self):
        if self.cleaned_data.get('link_type') == 'documentation':
            self.cleaned_data['link_data'] = {
                'type': 'documentation',
                'value': self.cleaned_data.get('documentation'),
            }

    def set_initial_documentation(self, initial):
        try:
            initial['documentation'] = initial['link']['value']
        except KeyError:
            pass


class SphinxDocsLinkPlugin(LinkPluginBase):
    fields = [
        ('link_type', 'cms_page', 'section', 'documentation', 'ext_url', 'mail_to'),
        'glossary',
    ]
    ring_plugin = 'SphinxDocsLinkPlugin'

    class Media:
        js = ['cascade/sphinx/js/link_plugin.js']

    @classmethod
    def get_link(cls, obj):
        link = obj.glossary.get('link', {})
        if link.get('type') == 'documentation':
            page = Page.objects.filter(navigation_extenders='DocumentationMenu', publisher_is_draft=False).first()
            if page:
                return page.get_public_url()
        return super().get_link(obj)
