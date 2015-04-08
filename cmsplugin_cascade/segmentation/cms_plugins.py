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
    eval_template = "{{% if {} %}}True{{% endif %}}"
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
        def conditionally_eval():
            condition = self.html_parser.unescape(instance.glossary['condition'])
            if Template(self.eval_template.format(condition)).render(context) == 'True':
                context['request']._evaluated_instances[instance.id] = True
                return Template(self.default_template)
            else:
                context['request']._evaluated_instances[instance.id] = False
                return Template('')

        open_tag = instance.glossary.get('open_tag')
        if open_tag == 'if':
            return conditionally_eval()
        elif open_tag in ('elif', 'else'):
            prev_inst, _ = self.get_previous_instance(instance)
            if context['request']._evaluated_instances.get(prev_inst.id):
                context['request']._evaluated_instances[instance.id] = True
                return Template('')
            if open_tag == 'elif':
                return conditionally_eval()
        return Template(self.default_template)

    def render(self, context, instance, placeholder):
        if not hasattr(context['request'], '_evaluated_instances'):
            context['request']._evaluated_instances = {}
        return super(SegmentPlugin, self).render(context, instance, placeholder)

    def get_form(self, request, obj=None, **kwargs):
        # adopt select open_tag to `if`, `elif` and `else` or `if` only
        prev_inst, prev_model = self.get_previous_instance(obj)
        if issubclass(prev_model.__class__, self.__class__) and \
                (prev_inst is None or prev_inst.glossary.get('open_tag') != 'else'):
            choices = (('if', _("if")), ('elif', _("elif")), ('else', _("else")),)
        else:
            choices = (('if', _("if")),)
        self.glossary_fields[0].widget.choices = choices
        # remove escape quotes, added by JSON serializer
        if obj:
            condition = self.html_parser.unescape(obj.glossary.get('condition', ''))
            obj.glossary.update(condition=condition)
        return super(SegmentPlugin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.glossary.get('open_tag') == 'else':
            obj.glossary.update(condition='')
        super(SegmentPlugin, self).save_model(request, obj, form, change)

plugin_pool.register_plugin(SegmentPlugin)
