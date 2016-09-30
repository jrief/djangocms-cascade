# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.forms import widgets
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade import settings
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.widgets import MultipleCascadingSizeWidget


@python_2_unicode_compatible
class ExtraFieldsMixin(object):
    """
    If a Cascade plugin is listed in ``settings.CMSPLUGIN_CASCADE['plugins_with_extra_fields']``,
    then this ``ExtraFieldsMixin`` class is added automatically to its plugin class in order to
    offer extra fields for customizing CSS classes and styles.
    """

    def __str__(self):
        return self.plugin_class.get_identifier(self)

    def get_form(self, request, obj=None, **kwargs):
        from cmsplugin_cascade.models import PluginExtraFields
        from .config import PluginExtraFieldsConfig

        glossary_fields = list(kwargs.pop('glossary_fields', self.glossary_fields))
        clsname = self.__class__.__name__
        try:
            site = get_current_site(request)
            extra_fields = PluginExtraFields.objects.get(plugin_type=clsname, site=site)
        except ObjectDoesNotExist:
            extra_fields = settings.CMSPLUGIN_CASCADE['plugins_with_extra_fields'].get(clsname)

        if isinstance(extra_fields, (PluginExtraFields, PluginExtraFieldsConfig)):
            # add a text input field to let the user name an ID tag for this HTML element
            if extra_fields.allow_id_tag:
                glossary_fields.append(GlossaryField(
                    widgets.TextInput(),
                    label=_("Named Element ID"),
                    name='extra_element_id'
                ))

            # add a select box to let the user choose one or more CSS classes
            class_names = extra_fields.css_classes.get('class_names', '').replace(' ', '')
            if class_names:
                choices = [(clsname, clsname) for clsname in class_names.split(',')]
                if extra_fields.css_classes.get('multiple'):
                    widget = widgets.CheckboxSelectMultiple(choices=choices)
                else:
                    widget = widgets.Select(choices=((None, _("Select CSS")),) + tuple(choices))
                glossary_fields.append(GlossaryField(
                    widget,
                    label=_("Customized CSS Classes"),
                    name='extra_css_classes',
                    help_text=_("Customized CSS classes to be added to this element.")
                ))

            # add input fields to let the user enter styling information
            for style, choices_tuples in settings.CMSPLUGIN_CASCADE['extra_inline_styles'].items():
                inline_styles = extra_fields.inline_styles.get('extra_fields:{0}'.format(style))
                if not inline_styles:
                    continue
                Widget = choices_tuples[1]
                if issubclass(Widget, MultipleCascadingSizeWidget):
                    key = 'extra_inline_styles:{0}'.format(style)
                    allowed_units = extra_fields.inline_styles.get('extra_units:{0}'.format(style)).split(',')
                    widget = Widget(inline_styles, allowed_units=allowed_units, required=False)
                    glossary_fields.append(GlossaryField(widget, label=style, name=key))
                else:
                    for inline_style in inline_styles:
                        key = 'extra_inline_styles:{0}'.format(inline_style)
                        label = '{0}: {1}'.format(style, inline_style)
                        glossary_fields.append(GlossaryField(Widget(), label=label, name=key))

        kwargs.update(glossary_fields=glossary_fields)
        return super(ExtraFieldsMixin, self).get_form(request, obj, **kwargs)

    @classmethod
    def get_css_classes(cls, obj):
        """Enrich list of CSS classes with customized ones"""
        css_classes = super(ExtraFieldsMixin, cls).get_css_classes(obj)
        extra_css_classes = obj.glossary.get('extra_css_classes')
        if isinstance(extra_css_classes, six.string_types):
            css_classes.append(extra_css_classes)
        elif isinstance(extra_css_classes, (list, tuple)):
            css_classes.extend(extra_css_classes)
        return css_classes

    @classmethod
    def get_inline_styles(cls, obj):
        """Enrich inline CSS styles with customized ones"""
        inline_styles = super(ExtraFieldsMixin, cls).get_inline_styles(obj)
        for key, eis in obj.glossary.items():
            if key.startswith('extra_inline_styles:'):
                if isinstance(eis, dict):
                    inline_styles.update(dict((k, v) for k, v in eis.items() if v))
                if isinstance(eis, (list, tuple)):
                    # the first entry of a sequence is used to disable an inline style
                    if eis[0] != 'on':
                        inline_styles.update({key.split(':')[1]: eis[1]})
                elif isinstance(eis, six.string_types):
                    inline_styles.update({key.split(':')[1]: eis})
        return inline_styles

    @classmethod
    def get_html_tag_attributes(cls, obj):
        attributes = super(ExtraFieldsMixin, cls).get_html_tag_attributes(obj)
        extra_element_id = obj.glossary.get('extra_element_id')
        if extra_element_id:
            attributes.update(id=extra_element_id)
        return attributes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(ExtraFieldsMixin, cls).get_identifier(obj)
        extra_element_id = obj.glossary and obj.glossary.get('extra_element_id')
        if extra_element_id:
            return format_html('{0}<em>{1}:</em> ', identifier, extra_element_id)
        return identifier
