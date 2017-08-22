# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.forms import fields, widgets, models
from django.http import JsonResponse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _, get_language_from_request

from cms.plugin_pool import plugin_pool
from cms.models.pagemodel import Page
from cmsplugin_cascade.fields import GlossaryField

from django_select2.forms import HeavySelect2TagWidget

from .plugin_base import BootstrapPluginBase


class SelectMultiWidget(HeavySelect2TagWidget):
    # def __init__(self, **kwargs):
    #     kwargs.update(data_url=reverse('admin:get_sec_menuitems'))
    #     super(SelectMultiWidget, self).__init__(**kwargs)

    @property
    def media(self):
        parent_media = super(SelectMultiWidget, self).media
        # prepend JS snippet to re-add 'jQuery' to the global namespace
        parent_media._js.insert(0, 'cascade/js/admin/jquery.restore.js')
        return parent_media

    def value_from_datadict(self, data, files, name):
        values = super(SelectMultiWidget, self).value_from_datadict(data, files, name)
        return ",".join(values)

    def optgroups(self, name, value, attrs=None):
        values = value[0].split(',') if value[0] else []
        selected = set(values)
        subgroup = [self.create_option(name, v, v, selected, i) for i, v in enumerate(values)]
        return [(None, subgroup, 0)]


# class LinkSelectField(fields.MultipleChoiceField):
#     def __init__(self, *args, **kwargs):
#         kwargs.setdefault('widget', SelectMultiWidget)
#         super(LinkSelectField, self).__init__(*args, **kwargs)
#
#     def clean(self, value):
#         try:
#             return int(value)
#         except (TypeError, ValueError):
#             pass
#
#
# class LinkSelectForm(models.ModelForm):
#     selected_links = LinkSelectField(
#         required=False,
#         label='',
#         help_text=_("An internal link onto CMS pages of this site"),
#     )
#
#     class Meta:
#         fields = ['glossary']


class BootstrapSecondaryMenuPlugin(BootstrapPluginBase):
    """
    Use this plugin to display a secondary menu in arbitrary locations.
    This renders links onto all selected CMS pages, which are children of the selected Page Id.
    """
    name = _("Secondary Menu")
    default_css_class = 'list-group'
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    allow_children = False
    render_template = 'cascade/bootstrap3/secmenu-list-group.html'
    glossary_field_order = ['page_id', 'selected_links']
    ring_plugin = 'SecondaryMenuPlugin'

    page_id = GlossaryField(
        widgets.Select(choices=()),
        label=_("CMS Page Id"),
        help_text=_("Select a CMS page with a given unique Id (in advanced settings).")
    )

    selected_links = GlossaryField(
        SelectMultiWidget(data_url='/xyz'), # reverse_lazy('admin:get_sec_menuitems')),
        label=_("Selected Links"),
    )

    class Media:
        js = ['cascade/js/admin/secondarymenuplugin.js']

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapSecondaryMenuPlugin, cls).get_identifier(obj)
        content = obj.glossary.get('page_id', '')
        return format_html('{0}{1}', identifier, content)

    def Xget_urls(self):
        from django.conf.urls import url
        urls = [
            url(r'^get_sec_menuitems/$', lambda: None, name='get_sec_menuitems'),  # just to reverse
            url(r'^get_sec_menuitems/(?P<page_pk>\d+)$',
                self.admin_site.admin_view(self.get_sec_menuitems)),
        ]
        urls.extend(super(BootstrapSecondaryMenuPlugin, self).get_urls())
        return urls

    def get_sec_menuitems(self, request, page_pk=None):
        choices = []
        try:
            for key, val in self.model.objects.get(extended_object_id=page_pk).glossary['element_ids'].items():
                choices.append((key, val))
        except (self.model.DoesNotExist, KeyError):
            pass
        return JsonResponse({'element_ids': choices})

    def get_form(self, request, obj=None, **kwargs):
        lang = get_language_from_request(request)
        choices = {}
        for page in Page.objects.filter(reverse_id__isnull=False).order_by('publisher_is_draft'):
            if page.reverse_id not in choices:
                choices[page.reverse_id] = page.get_title(lang)
        page_id_field = next((f for f in self.glossary_fields if f.name == 'page_id'))
        page_id_field.widget.choices = list(choices.items())
        return super(BootstrapSecondaryMenuPlugin, self).get_form(request, obj, **kwargs)

plugin_pool.register_plugin(BootstrapSecondaryMenuPlugin)
