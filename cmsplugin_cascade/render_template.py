# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
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
