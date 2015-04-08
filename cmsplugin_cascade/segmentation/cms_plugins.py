# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import copy
try:
    from html.parser import HTMLParser  # py3
except ImportError:
    from HTMLParser import HTMLParser  # py2
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.template import Template, TemplateSyntaxError
from django.template.loader import select_template
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.utils import resolve_dependencies


class SegmentPlugin(CascadePluginBase):
    """
    This button is used as a final step to convert the Cart object into an Order object.
    """
    name = _("Segment")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    allow_children = True
    generic_child_classes = ('TextPlugin',)
    glossary_fields = (
        PartialFormField('open_tag',
            widgets.Select(choices=()),
            label=_('Condition tag'),
            help_text=_("Django's condition tag")
        ),
        PartialFormField('condition',
            widgets.Input(),
            label=_('Condition evaluation'),
            help_text=_("Evaluation as used in Django's condition tags")
        ),
    )
    html_parser = HTMLParser()
    template_template = """
{{% load cms_tags %}}
{{% {open_tag} {condition} %}}
    {{% for plugin in instance.child_plugin_instances %}}
        {{% render_plugin plugin %}}
    {{% endfor %}}
{{% {close_tag} %}}"""
    default_template = "{% load cms_tags %}{% for plugin in instance.child_plugin_instances %}{% render_plugin plugin %}{% endfor %}"

    class Media:
        js = resolve_dependencies('cascade/js/admin/segmentplugin.js')

    @classmethod
    def get_identifier(cls, obj):
        try:
            return mark_safe("<strong><em>{open_tag}</em></strong> {condition}".format(**obj.glossary))
        except KeyError:
            return ''

    def get_render_template(self, context, instance, placeholder):
        try:
            fmt_args = {
                'open_tag': instance.glossary['open_tag'],
                'condition': self.html_parser.unescape(instance.glossary['condition']),
                'close_tag': 'endif'
            }
            template = Template(self.template_template.format(**fmt_args))
        except (KeyError, TemplateSyntaxError):
            template = Template(self.default_template)
        return template

    def get_combined_condition_instances(self, instance):
        """
        From a given SegmentPluginModel instance with `open_tag == "if"`, search all other
        instances belonging together, ie. those with instance with `open_tag == "elif"` and
        `open_tag == "else"`
        """
        condition_instances = []
        if instance.parent:
            parent_obj, _ = instance.parent.get_plugin_instance()
            for child in parent_obj.get_children_instances():
                open_tag = child.glossary.get('open_tag')
                if child.id == instance.id and open_tag == 'if':
                    # first search myself, it must be an `if` condition
                    condition_instances.append(child)
                elif condition_instances:
                    # only append to condition_instances, if instance belongs to the same block
                    if open_tag == 'elif':
                        condition_instances.append(child)
                    elif open_tag == 'else':
                        condition_instances.append(child)
                        break
                    else:
                        break
        return condition_instances

    def get_form(self, request, obj=None, **kwargs):
        # adopt select open_tag to `if`, `elif` and `else` or `if` only
        previous_sibling = obj.get_previous_sibling()
        if previous_sibling and previous_sibling.glossary.get('open_tag') in ('if', 'elif'):
            choices = (('if', _("if")), ('elif', _("elif")), ('else', _("else")),)
        else:
            choices = (('if', _("if")),)
        self.glossary_fields[0].widget.choices = choices
        # remove escape quotes, added by JSON serializer
        if obj:
            condition = self.html_parser.unescape(obj.glossary.get('condition', ''))
            obj.glossary.update(condition=condition)
        return super(SegmentPlugin, self).get_form(request, obj, **kwargs)

plugin_pool.register_plugin(SegmentPlugin)
