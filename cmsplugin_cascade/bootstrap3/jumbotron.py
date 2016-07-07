# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import widgets
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.mixins import ImagePropertyMixin
from cmsplugin_cascade.utils import resolve_dependencies
from cmsplugin_cascade.widgets import MultipleCascadingSizeWidget, ColorPickerWidget
from .plugin_base import BootstrapPluginBase
from .image import ImageForm
from .utils import get_widget_choices, compute_media_queries, get_picture_elements, BS3_BREAKPOINT_KEYS
from .container import ContainerBreakpointsRenderer


class BootstrapJumbotronPlugin(BootstrapPluginBase):
    name = _("Jumbotron")
    model_mixins = (ImagePropertyMixin,)
    form = ImageForm
    default_css_class = 'jumbotron'
    parent_classes = None
    require_parent = False
    allow_children = True
    alien_child_classes = True
    raw_id_fields = ('image_file',)
    fields = ('glossary', 'image_file',)
    render_template = 'cascade/bootstrap3/jumbotron.html'
    change_form_template = 'cascade/admin/text_plugin_change_form.html'
    POSITION_CHOICES = ('a', 'b', 'c')
    glossary_fields = (
        PartialFormField(
            'background-color',
            ColorPickerWidget(),
            label=_("Background color"),
        ),
        PartialFormField(
            'background-position',
            widgets.Select(choices=[(c, c) for c in POSITION_CHOICES]),
            label=_("Background position"),
        ),
    )
    optional_glossary_fields = (
        PartialFormField(
           'breakpoints',
            widgets.CheckboxSelectMultiple(choices=get_widget_choices(),
                                           renderer=ContainerBreakpointsRenderer),
            label=_("Available Breakpoints"),
            initial=list(BS3_BREAKPOINT_KEYS)[::-1],
            help_text=_("Supported display widths for Bootstrap's grid system.")
        ),
        PartialFormField(
            'responsive-heights',
            MultipleCascadingSizeWidget(BS3_BREAKPOINT_KEYS,
                                        allowed_units=['px', '%'], required=False),
            label=_("Adapt Picture Heights"),
            initial={'xs': '100%', 'sm': '100%', 'md': '100%', 'lg': '100%'},
            help_text=_("Heights of picture in percent or pixels for distinct Bootstrap's breakpoints."),
        ),
    )

    class Media:
        css = {'all': ('//netdna.bootstrapcdn.com/font-awesome/3.2.1/css/font-awesome.min.css',)}
        js = resolve_dependencies('cascade/js/admin/jumbotronplugin.js')

    def get_form(self, request, obj=None, **kwargs):
        if self.get_parent_instance(request) is None:
            # we only ask for breakpoints, if the jumbotron is the root of the placeholder
            kwargs.update(glossary_fields=self.optional_glossary_fields)
        form = super(BootstrapJumbotronPlugin, self).get_form(request, obj, **kwargs)
        return form

    def render(self, context, instance, placeholder):
        # image shall be rendered in a responsive context using the ``<picture>`` element
        print(instance.glossary)
        elements = [e for e in get_picture_elements(context, instance) if 'media' in e]
        context.update({
            'instance': instance,
            'placeholder': placeholder,
            'elements': elements,
        })
        return super(BootstrapJumbotronPlugin, self).render(context, instance, placeholder)

    @classmethod
    def sanitize_model(cls, obj):
        # if the jumbotron is the root of the placeholder, we consider it as "fluid"
        obj.glossary.setdefault('fluid', obj.parent is None)
        sanitized = super(BootstrapJumbotronPlugin, cls).sanitize_model(obj)
        compute_media_queries(obj)
        return sanitized

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapJumbotronPlugin, cls).get_identifier(obj)
        try:
            content = obj.image.name or obj.image.original_filename
        except AttributeError:
            content = _("Without background image")
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(BootstrapJumbotronPlugin)
