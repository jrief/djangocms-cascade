# -*- coding: utf-8 -*-
from __future__ import unicode_literals
try:
    from html.parser import HTMLParser  # py3
except ImportError:
    from HTMLParser import HTMLParser  # py2
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.template import Template, TemplateSyntaxError
from cms.plugin_pool import plugin_pool
from cms.utils.placeholder import get_placeholder_conf
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.utils import resolve_dependencies


class SegmentPlugin(CascadePluginBase):
    """
    This button is used as a final step to convert the Cart object into an Order object.
    """
    name = _("Segment")
    require_parent = False
    parent_classes = None
    allow_children = True
    child_classes = None
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

    def get_child_classes(self, slot, page):
        if self.cms_plugin_instance:
            if self.cms_plugin_instance.parent:
                plugin_class = self.cms_plugin_instance.parent.get_plugin_class()
                child_classes = plugin_class().get_child_classes(slot, page)
            else:  # SegmentPlugin is at the root level
                template = page and page.get_template() or None
                child_classes = get_placeholder_conf('plugins', slot, template, default=[])
        else:
            child_classes = super(SegmentPlugin, self).get_child_classes(slot, page)
        return child_classes

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
        # compile condition for testing purpose
        if obj.glossary.get('open_tag') == 'else':
            obj.glossary.update(condition='')
        super(SegmentPlugin, self).save_model(request, obj, form, change)

plugin_pool.register_plugin(SegmentPlugin)
