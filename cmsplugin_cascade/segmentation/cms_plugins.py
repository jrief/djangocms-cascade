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
from django.template import Template, TemplateSyntaxError
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.mixins import TransparentMixin
from cmsplugin_cascade.utils import resolve_dependencies


class SegmentPlugin(TransparentMixin, CascadePluginBase):
    """
    A Segment is a part of the DOM which is rendered or not, depending on a condition.
    As condition you may use any expression which is valid inside a Django's template tag,
    such as ``{% if ... %}``.
    """
    name = _("Segment")

    open_tag = GlossaryField(
        widgets.Select(choices=()),
        label=_('Condition tag'),
        help_text=_("Django's condition tag")
    )

    condition = GlossaryField(
        widgets.Input(),
        label=_('Condition evaluation'),
        help_text=_("Evaluation as used in Django's template tags for conditions")
    )

    html_parser = HTMLParser()
    eval_template_string = '{{% if {} %}}True{{% endif %}}'
    default_template = Template('{% load cms_tags %}{% for plugin in instance.child_plugin_instances %}{% render_plugin plugin %}{% endfor %}')
    hiding_template_string = '{% load cms_tags %}<div style="display: none;">{% for plugin in instance.child_plugin_instances %}{% render_plugin plugin %}{% endfor %}</div>'
    hiding_template = Template(hiding_template_string)
    debug_error_template = '<!-- segment condition "{condition}" for plugin: {instance_id} failed: "{message}" -->{template_string}'
    empty_template = Template('<!-- segment condition for plugin: {{ instance.id }} did not evaluate -->')
    require_parent = False
    parent_classes = None
    allow_children = True
    child_classes = None
    cache = False

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
            evaluated_to = False
            template_error_message = None
            try:
                eval_template = Template(self.eval_template_string.format(condition))
                evaluated_to = eval_template.render(context) == 'True'
            except TemplateSyntaxError as err:
                # TODO: render error message into template
                template_error_message = err.message
            finally:
                if evaluated_to:
                    request._evaluated_instances[instance.id] = True
                    template = self.default_template
                else:
                    request._evaluated_instances[instance.id] = False
                    if edit_mode:
                        # in edit mode hidden plugins have to be rendered nevertheless using CSS
                        # style="display: none", otherwise they are invisible in the plugin structure
                        if template_error_message:
                            template = self.debug_error_template.format(condition=condition,
                                instance_id=instance.id, message=template_error_message,
                                template_string=self.hiding_template_string)
                            template = Template(template)
                        else:
                            template = self.hiding_template
                    else:
                        template = self.empty_template
            return template

        request = context['request']
        toolbar = getattr(request, 'toolbar', None)
        edit_mode = (toolbar and toolbar.edit_mode and placeholder.has_change_permission(request) and
                     getattr(placeholder, 'is_editable', True))
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
