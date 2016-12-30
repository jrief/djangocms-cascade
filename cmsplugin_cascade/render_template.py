# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from django.template import engines
from django.template.loader import get_template, TemplateDoesNotExist

from cmsplugin_cascade import settings
from cmsplugin_cascade.fields import GlossaryField


class RenderTemplateMixin(object):
    """
    If a Cascade plugin is listed in ``settings.CMSPLUGIN_CASCADE['plugins_with_extra_templates']``,
    then this ``RenderTemplateMixin`` class is added automatically to its plugin class in order
    to add an additional select box used for choosing an alternative render template.
    """
    @classmethod
    def get_template_choices(cls):
        return settings.CMSPLUGIN_CASCADE['plugins_with_extra_render_templates'][cls.__name__]

    def get_form(self, request, obj=None, **kwargs):
        glossary_fields = list(kwargs.pop('glossary_fields', self.glossary_fields))
        glossary_fields.append(GlossaryField(
            widgets.Select(choices=self.get_template_choices()),
            label=_("Render template"),
            name='render_template',
            help_text=_("Use alternative template for rendering this plugin.")
        ))
        kwargs.update(glossary_fields=glossary_fields)
        return super(RenderTemplateMixin, self).get_form(request, obj, **kwargs)

    def get_render_template(self, context, instance, placeholder):
        try:
            template = instance.glossary.get('render_template', self.get_template_choices()[0][0])
            get_template(template)
        except (IndexError, TemplateDoesNotExist):
            template = self.render_template
        return template


class HidePluginMixin(object):
    """
    This mixin class adds a checkbox to each named plugin, which if checked hides that
    plugin during the rendering phase.
    """
    suppress_template = engines['django'].from_string('')
    hiding_template_string = '''
{{% load cms_tags %}}
<div style="display: none;">
{{% for plugin in instance.child_plugin_instances %}}{{% render_plugin plugin %}}{{% endfor %}}
</div>
<style>
div.cms .cms-structure .cms-draggable-{plugin_id} .cms-dragitem {{
color: gray;
background-color: lightgray;
background-image: repeating-linear-gradient(-45deg, transparent, transparent 4px, rgba(255,255,255,.5) 4px, rgba(255,255,255,.5) 8px);
background-size: contain;
}}
</style>
'''

    def get_form(self, request, obj=None, **kwargs):
        glossary_fields = list(kwargs.pop('glossary_fields', self.glossary_fields))
        glossary_fields.insert(0, GlossaryField(
            widgets.CheckboxInput(),
            label=_("Hide plugin"),
            name='hide_plugin',
            help_text=_("Hide this plugin and all of it's children.")
        ))
        kwargs.update(glossary_fields=glossary_fields)
        return super(HidePluginMixin, self).get_form(request, obj, **kwargs)

    def get_render_template(self, context, instance, placeholder):
        if instance.glossary.get('hide_plugin'):
            if self.in_edit_mode(context['request'], placeholder):
                # in edit mode we actually must render the children, otherwise they won't show
                # up in Structure Mode
                template_string = self.hiding_template_string.format(plugin_id=instance.pk)
                return engines['django'].from_string(template_string)
            else:
                return self.suppress_template

        super_self = super(HidePluginMixin, self)
        if hasattr(super_self, 'get_render_template'):
            template = super_self.get_render_template(context, instance, placeholder)
        elif getattr(self, 'render_template', False):
            template = getattr(self, 'render_template', False)
        else:
            template = None
        if not template:
            raise ImproperlyConfigured("Plugin {} has no render_template.".format(self.__class__))
        return template
