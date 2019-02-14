# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from distutils.version import LooseVersion
from django.forms import MediaDefiningClass, widgets
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.utils.six.moves.urllib.parse import urlparse


from cms import __version__ as CMS_VERSION
if LooseVersion(CMS_VERSION) < LooseVersion('3.5'):
    from cms.utils.page_resolver import get_page_from_request
else:
    from cms.utils.page import get_page_from_request


from cmsplugin_cascade import app_settings
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.widgets import MultipleCascadingSizeWidget


@python_2_unicode_compatible
class ExtraFieldsMixin(six.with_metaclass(MediaDefiningClass)):
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
            extra_fields = app_settings.CMSPLUGIN_CASCADE['plugins_with_extra_fields'].get(clsname)

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
                    choices.insert(0, (None, _("Select CSS")))
                    widget = widgets.Select(choices=choices)
                glossary_fields.append(GlossaryField(
                    widget,
                    label=_("Customized CSS Classes"),
                    name='extra_css_classes',
                    help_text=_("Customized CSS classes to be added to this element.")
                ))

            # add input fields to let the user enter styling information
            for style, choices_tuples in app_settings.CMSPLUGIN_CASCADE['extra_inline_styles'].items():
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

            # add input fields to let the user enter html tag attibutes information
            for html_tag_attrs, choices_tuples in app_settings.CMSPLUGIN_CASCADE['extra_html_tag_attributes'].items():
                html_tag_attributes = extra_fields.html_tag_attributes.get('extra_fields:{0}'.format(html_tag_attrs))
                if html_tag_attributes is not None:
                    for data_set in html_tag_attributes:
                        Widget = choices_tuples[1]
                        Widget.request_cms_path=urlparse(request.GET.dict()['cms_path']).path
                        if isinstance(data_set, tuple):
                            Widget.widget_name = data_set[0]
                            Widget.attributes_extra = data_set[1]
                            if 'widget_choices_cms_page' in str(Widget.attributes_extra.values()):
                                cms_path = urlparse(request.GET.dict()['cms_path']).path
                                page = get_page_from_request(request, use_path=cms_path, clean_path=True)
                                Widget.current_page = page
                        key = 'extra_html_tag_attributes:{0}'.format(Widget.widget_name)
                        label = '{0}: {1}'.format(  html_tag_attrs , Widget.widget_name)
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
        extra_html_tag_attributes = obj.glossary.get('extra_html_tag_attributes')
        for key, eis in obj.glossary.items():
            if key.startswith('extra_html_tag_attributes:'):
                if isinstance(eis, dict):
                    attributes.update(dict((k, v) for k, v in eis.items() if v))
                if isinstance(eis, (list, tuple)):
                    attributes.update({key.split(':')[1]: eis[0]})
                    attributes.update({key.split(':')[1]: eis[0]})
                elif isinstance(eis, six.string_types):
                    attributes.update({key.split(':')[1]: eis})
                    attributes.update({key.split(':')[0]: eis})
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
