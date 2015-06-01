# -*- coding: utf-8 -*-
from __future__ import unicode_literals
try:
    from html.parser import HTMLParser  # py3
except ImportError:
    from HTMLParser import HTMLParser  # py2
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.template import Template, TemplateSyntaxError, RequestContext
from cms.plugin_pool import plugin_pool
from cms.utils.placeholder import get_placeholder_conf
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.utils import resolve_dependencies


class SegmentPluginBase(CascadePluginBase):
    require_parent = False
    parent_classes = None
    allow_children = True
    child_classes = None

    def get_context_override(self, request):
        """
        Return a dictionary to override the context during evaluation. Normally this is an empty
        dict. However, when a staff user overrides the segmentation, then update the context with
        the returned dict.
        """
        return {}


class SegmentPlugin(SegmentPluginBase):
    """
    This button is used as a final step to convert the Cart object into an Order object.
    """
    name = _("Segment")
    glossary_fields = (
        PartialFormField('open_tag',
            widgets.Select(choices=()),
            label=_('Condition tag'),
            help_text=_("Django's condition tag")
        ),
        PartialFormField('condition',
            widgets.Input(),
            label=_('Condition evaluation'),
            help_text=_("Evaluation as used in Django's template tags for conditions")
        ),
    )
    html_parser = HTMLParser()
    eval_template_string = "{{% if {} %}}True{{% endif %}}"
    default_template = Template("{% load cms_tags %}{% for plugin in instance.child_plugin_instances %}{% render_plugin plugin %}{% endfor %}")
    hiding_template = Template("{% load cms_tags %}<div style=\"display: none;\">{% for plugin in instance.child_plugin_instances %}{% render_plugin plugin %}{% endfor %}</div>")
    empty_template = Template('')
    cache = False

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
            context = RequestContext(request, {})
            context.update(context_override)
            condition = self.html_parser.unescape(instance.glossary['condition'])
            try:
                eval_template = Template(self.eval_template_string.format(condition))
                evaluated_to = eval_template.render(context) == 'True'
            except TemplateSyntaxError:
                evaluated_to = False
            finally:
                if evaluated_to:
                    request._evaluated_instances[instance.id] = True
                    template = self.default_template
                else:
                    request._evaluated_instances[instance.id] = False
                    # in edit mode hidden plugins have to be rendered nevertheless
                    template = edit_mode and self.hiding_template or self.empty_template
            return template

        request = context['request']
        toolbar = getattr(request, 'toolbar', None)
        edit_mode = (toolbar and toolbar.edit_mode and placeholder.has_change_permission(request) and
                     getattr(placeholder, 'is_editable', True))
        context_override = self.get_context_override(request)
        open_tag = instance.glossary.get('open_tag')
        if open_tag == 'if':
            template = conditionally_eval()
        else:
            assert open_tag in ('elif', 'else')
            prev_inst, _ = self.get_previous_instance(instance)
            if prev_inst is None:
                # this can happen, if one moves an else- or elif-segment in front of an if-segment
                template = edit_mode and self.hiding_template or self.empty_template
            elif request._evaluated_instances.get(prev_inst.id):
                request._evaluated_instances[instance.id] = True
                # in edit mode hidden plugins have to be rendered nevertheless
                template = edit_mode and self.hiding_template or self.empty_template
            elif open_tag == 'elif':
                template = conditionally_eval()
            else:
                template = self.default_template
        return template

    def render(self, context, instance, placeholder):
        if not hasattr(context['request'], '_evaluated_instances'):
            context['request']._evaluated_instances = {}
        return super(SegmentPlugin, self).render(context, instance, placeholder)

    def get_form(self, request, obj=None, **kwargs):
        def clean_condition(value):
            """
            Compile condition using the Django template system to find potential syntax errors
            """
            try:
                if value:
                    condition = self.html_parser.unescape(value)
                    Template(self.eval_template_string.format(condition))
            except TemplateSyntaxError as err:
                raise ValidationError(_("Unable to evaluate condition: {err}").format(err=err.message))

        choices = self.get_allowed_open_tags(obj)
        print choices
        self.glossary_fields[0].widget.choices = choices
        self.glossary_fields[1].widget.validate = clean_condition
        # remove escape quotes, added by JSON serializer
        if obj:
            condition = self.html_parser.unescape(obj.glossary.get('condition', ''))
            obj.glossary.update(condition=condition)
        return super(SegmentPlugin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        # compile condition for testing purpose
        open_tag = obj.glossary.get('open_tag')
        if open_tag not in dict(self.get_allowed_open_tags(obj, change)):
            obj.glossary['open_tag'] = 'if'
        if open_tag == 'else':
            obj.glossary.update(condition='')
        super(SegmentPlugin, self).save_model(request, obj, form, change)

    def get_allowed_open_tags(self, obj, change=False):
        """
        Returns the tuple of allowed open tags: `if`, `elif` and `else` or `if` only
        """
        prev_inst, prev_model = self.get_previous_instance(obj)
        if prev_inst and issubclass(prev_model.__class__, self.__class__):
            prev_open_tag = prev_inst.glossary.get('open_tag')
        else:
            prev_open_tag = None
        if (change is True and prev_open_tag in ('if', 'elif') or
          change is False and prev_open_tag in ('if', 'elif', None)):
            return (('if', _("if")), ('elif', _("elif")), ('else', _("else")),)
        return (('if', _("if")),)

plugin_pool.register_plugin(SegmentPlugin)
