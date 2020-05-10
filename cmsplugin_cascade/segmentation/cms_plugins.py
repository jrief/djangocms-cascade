from django.core.exceptions import ValidationError
from django.forms.fields import CharField, ChoiceField
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.utils.text import unescape_entities
from django.template import engines, TemplateSyntaxError, Template as DjangoTemplate, Context as TemplateContext
from entangled.forms import EntangledModelFormMixin
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import CascadePluginBase, TransparentContainer


class Template(DjangoTemplate):
    def render(self, context):
        if isinstance(context, dict):
            context = TemplateContext(context)
        return super().render(context)


class SegmentFormMixin(EntangledModelFormMixin):
    eval_template_string = '{{% if {} %}}True{{% endif %}}'

    open_tag = ChoiceField()  # redeclared in get_form

    condition = CharField(
        label=_("Condition evaluation"),
        required=False,
        # widget=widgets.TextInput(attrs={'width': '100%'}),
        help_text=_("Evaluation as used in Django's template tags for conditions")
    )

    class Meta:
        entangled_fields = {'glossary': ['open_tag', 'condition']}

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs and kwargs['instance']:
            pass
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['open_tag'] in ('if', 'elif'):
            if not cleaned_data['condition']:
                raise ValidationError(_("The evaluation condition is missing or empty."))
            try:
                condition = unescape_entities(cleaned_data['condition'])
                engines['django'].from_string(self.eval_template_string.format(condition))
            except TemplateSyntaxError as err:
                raise ValidationError(_("Unable to evaluate condition: {}").format(str(err)))
        elif cleaned_data['open_tag'] == 'else':
            cleaned_data['condition'] = ''  # empty condition for else-block
        return cleaned_data


class SegmentPlugin(TransparentContainer, CascadePluginBase):
    """
    A Segment is a part of the DOM which is rendered or not, depending on a condition.
    As condition you may use any expression which is valid inside a Django's template tag,
    such as ``{% if ... %}``.
    """
    name = _("Segment")
    default_template = engines['django'].from_string('{% load cms_tags %}{% for plugin in instance.child_plugin_instances %}{% render_plugin plugin %}{% endfor %}')
    hiding_template_string = '{% load cms_tags %}<div style="display: none;">{% for plugin in instance.child_plugin_instances %}{% render_plugin plugin %}{% endfor %}</div>'
    hiding_template = engines['django'].from_string(hiding_template_string)
    debug_error_template = '<!-- segment condition "{condition}" for plugin: {instance_id} failed: "{message}" -->{template_string}'
    empty_template = engines['django'].from_string('{% load l10n %}<!-- segment condition for plugin: {{ instance.id|unlocalize }} did not evaluate -->')
    ring_plugin = 'SegmentPlugin'
    require_parent = False
    direct_parent_classes = None
    allow_children = True
    child_classes = None
    cache = False

    class Media:
        js = ['admin/js/jquery.init.js', 'cascade/js/admin/segmentplugin.js']

    @classmethod
    def get_identifier(cls, obj):
        try:
            return format_html("<strong><em>{open_tag}</em></strong> {condition}", **obj.glossary)
        except KeyError:
            return ''

    def get_render_template(self, context, instance, placeholder):
        def conditionally_eval():
            condition = unescape_entities(instance.glossary['condition'])
            evaluated_to = False
            template_error_message = None
            try:
                template_string = SegmentFormMixin.eval_template_string.format(condition)
                eval_template = engines['django'].from_string(template_string)
                evaluated_to = eval_template.render(context) == 'True'
            except TemplateSyntaxError as err:
                template_error_message = str(err)
            finally:
                if evaluated_to:
                    request._evaluated_segments[instance.pk] = True
                    template = self.default_template
                else:
                    request._evaluated_segments[instance.pk] = False
                    if edit_mode:
                        # In edit mode, hidden plugins have to be rendered nevertheless. Therefore
                        # we use `style="display: none"`, otherwise the plugin would be invisible
                        # in structure mode, while editing.
                        if template_error_message:
                            template = self.debug_error_template.format(condition=condition,
                                instance_id=instance.pk, message=template_error_message,
                                template_string=self.hiding_template_string)
                            template = engines['django'].from_string(template)
                        else:
                            template = self.hiding_template
                    else:
                        template = self.empty_template
            return template

        request = context['request']
        edit_mode = self.in_edit_mode(request, placeholder)
        open_tag = instance.glossary.get('open_tag')
        if open_tag == 'if':
            template = conditionally_eval()
        else:
            assert open_tag in ('elif', 'else'), "Expected openening templatetag to be 'elif' or 'else'."
            prev_instance = self.get_previous_instance(instance)
            if prev_instance is None:
                # this can happen, if one moved an `else`- or `elif`-segment in front of an `if`-segment
                template = edit_mode and self.hiding_template or self.empty_template
            elif request._evaluated_segments.get(prev_instance.pk):
                request._evaluated_segments[instance.pk] = (open_tag == 'elif')
                # in edit mode hidden plugins have to be rendered nevertheless
                template = edit_mode and self.hiding_template or self.empty_template
            elif open_tag == 'elif':
                template = conditionally_eval()
            else:
                template = self.default_template
        return template

    def render(self, context, instance, placeholder):
        request = context['request']
        if not hasattr(request, '_evaluated_segments'):
            request._evaluated_segments = {}
        context.update(instance.get_context_override(request))
        return self.super(SegmentPlugin, self).render(context, instance, placeholder)

    def get_form(self, request, obj=None, **kwargs):
        choices = [('if', _("if"))]
        if obj is None or self._get_previous_open_tag(obj) in ('if', 'elif'):
            # if obj is None, we are adding a SegmentPlugin, hence we must offer all conditional
            # tags, which however may be rectified during the save() operation
            choices.extend([('elif', _("elif")), ('else', _("else"))])
        open_tag = ChoiceField(
            label=_("Condition tag"),
            choices=choices,
            help_text=_("Django's condition tag")
        )
        form = type('SegmentForm', (SegmentFormMixin,), {'open_tag': open_tag})
        kwargs.setdefault('form', form)
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.glossary['open_tag'] != 'if' and self._get_previous_open_tag(obj) not in ('if', 'elif'):
           # rectify to an `if`-segment, when plugin is not saved next to an `if`- or `elif`-segment
           obj.glossary['open_tag'] = 'if'
           obj.save(update_fields=['glossary'])

    def _get_previous_open_tag(self, obj):
        """
        Return the open tag of the previous sibling
        """
        prev_instance = self.get_previous_instance(obj)
        if prev_instance and prev_instance.plugin_type == self.__class__.__name__:
            return prev_instance.glossary.get('open_tag')

plugin_pool.register_plugin(SegmentPlugin)
