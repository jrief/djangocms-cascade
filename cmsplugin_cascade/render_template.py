# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from django.template.loader import get_template, TemplateDoesNotExist
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade import settings as cascade_settings


class RenderTemplateMixin(object):
    """
    If a Cascade plugin is listed in ``settings.CASCADE_PLUGINS_WITH_EXTRA_RENDER_TEMPLATES``,
    then this ``RenderTemplateMixin`` class is added automatically to its plugin class in order
    to add an additional select box used for choosing an alternative render template.
    """
    @classmethod
    def get_template_choices(cls):
        return cascade_settings.CASCADE_PLUGINS_WITH_EXTRA_RENDER_TEMPLATES[cls.__name__]

    def get_form(self, request, obj=None, **kwargs):
        glossary_fields = list(kwargs.pop('glossary_fields', self.glossary_fields))
        glossary_fields.append(PartialFormField('render_template',
            widgets.Select(choices=self.get_template_choices()),
            label=_("Render template"),
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
