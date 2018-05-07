# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools

from django import VERSION as DJANGO_VERSION
from django.conf import settings
from django.forms import widgets
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.utils.html import format_html, format_html_join
from django.utils.encoding import force_text
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.forms.models import ModelForm
from django.forms.fields import ChoiceField

from cms.plugin_pool import plugin_pool

from cmsplugin_cascade import app_settings
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.fields import GlossaryField
from .plugin_base import BootstrapPluginBase
from .utils import compute_media_queries, get_widget_choices, BS3_BREAKPOINTS, BS3_BREAKPOINT_KEYS

import json

class ContainerBreakpointsWidget(widgets.CheckboxSelectMultiple):
    template_name = 'cascade/forms/widgets/container_breakpoints.html'

    def render(self, name, value, attrs=None, renderer=None):
        if DJANGO_VERSION >= (1, 11):
            return super(ContainerBreakpointsWidget, self).render(name, value, attrs, renderer)

        renderer = self.get_renderer(name, value, attrs)
        return format_html('<div class="form-row">{0}</div>',
            format_html_join('',
                '<div class="field-box">'
                    '<div class="container-thumbnail">'
                        '<img src="' + settings.STATIC_URL + 'cascade/admin/breakpoints/{1}.svg" style="height: 55px;" />'
                        '<div class="label">{0}</div>'
                    '</div>'
                '</div>', ((force_text(w), w.choice_value) for w in renderer)
            ))


class BootstrapContainerForm(ModelForm):
    """
    Form class to validate the container.
    """
    def clean_glossary(self):
        if len(self.cleaned_data['glossary']['breakpoints']) == 0:
            raise ValidationError(_("At least one breakpoint must be selected."))
        return self.cleaned_data['glossary']


class BootstrapContainerPlugin(BootstrapPluginBase):
    name = _("Container")
    parent_classes = None
    require_parent = False
    form = BootstrapContainerForm
    glossary_variables = ['container_max_widths', 'media_queries']
    glossary_field_order = ('breakpoints', 'fluid')

    breakpoints = GlossaryField(
        ContainerBreakpointsWidget(choices=get_widget_choices()),
        label=_('Available Breakpoints'),
        initial=list(BS3_BREAKPOINTS)[::-1],
        help_text=_("Supported display widths for Bootstrap's grid system.")
    )

    fluid = GlossaryField(
        widgets.CheckboxInput(),
        label=_('Fluid Container'), initial=False,
        help_text=_("Changing your outermost '.container' to '.container-fluid'.")
    )

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapContainerPlugin, cls).get_identifier(obj)
        while isinstance(obj.glossary, str):
            obj.glossary=json.loads(obj.glossary)
        breakpoints = obj.glossary.get('breakpoints')
        content = obj.glossary.get('fluid') and '(fluid) ' or ''
        if breakpoints:
            devices = ', '.join([force_text(BS3_BREAKPOINTS[bp][2]) for bp in breakpoints])
            content = _("{0}for {1}").format(content, devices)
        return format_html('{0}{1}', identifier, content)

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapContainerPlugin, cls).get_css_classes(obj)
        if obj.glossary.get('fluid'):
            css_classes.append('container-fluid')
        else:
            css_classes.append('container')
        return css_classes

    def save_model(self, request, obj, form, change):
        super(BootstrapContainerPlugin, self).save_model(request, obj, form, change)
        obj.sanitize_children()

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = super(BootstrapContainerPlugin, cls).sanitize_model(obj)
        compute_media_queries(obj)
        return sanitized

plugin_pool.register_plugin(BootstrapContainerPlugin)


class BootstrapRowForm(ManageChildrenFormMixin, ModelForm):
    """
    Form class to add non-materialized field to count the number of children.
    """
    ROW_NUM_COLUMNS = (1, 2, 3, 4, 6, 12,)
    num_children = ChoiceField(choices=tuple((i, ungettext_lazy('{0} column', '{0} columns', i).format(i)) for i in ROW_NUM_COLUMNS),
        initial=3, label=_('Columns'),
        help_text=_('Number of columns to be created with this row.'))


class BootstrapRowPlugin(BootstrapPluginBase):
    name = _("Row")
    default_css_class = 'row'
    parent_classes = ('BootstrapContainerPlugin', 'BootstrapColumnPlugin', 'BootstrapJumbotronPlugin')
    form = BootstrapRowForm
    fields = ('num_children', 'glossary',)

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapRowPlugin, cls).get_identifier(obj)
        num_cols = obj.get_num_children()
        content = ungettext_lazy("with {0} column", "with {0} columns", num_cols).format(num_cols)
        return format_html('{0}{1}', identifier, content)

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super(BootstrapRowPlugin, self).save_model(request, obj, form, change)
        parent_glossary = obj.get_complete_glossary()
        narrowest = parent_glossary['breakpoints'][0]
        column_width = 12 // wanted_children
        child_glossary = {
            '{0}-column-width'.format(narrowest): 'col-{0}-{1}'.format(narrowest, column_width)
        }
        self.extend_children(obj, wanted_children, BootstrapColumnPlugin, child_glossary=child_glossary)

plugin_pool.register_plugin(BootstrapRowPlugin)


class BootstrapColumnPlugin(BootstrapPluginBase):
    name = _("Column")
    parent_classes = ('BootstrapRowPlugin',)
    child_classes = ('BootstrapJumbotronPlugin',)
    alien_child_classes = True
    default_css_attributes = list(itertools.chain(*(('{}-column-width'.format(s),
        '{}-column-offset'.format(s), '{}-column-ordering'.format(s), '{}-responsive-utils'.format(s),)
        for s in BS3_BREAKPOINT_KEYS)))
    glossary_variables = ['container_max_widths']

    def get_form(self, request, obj=None, **kwargs):
        def choose_help_text(*phrases):
            if next_bp:
                return phrases[0].format(*BS3_BREAKPOINTS[next_bp])
            elif len(breakpoints) > 1:
                return phrases[1].format(*BS3_BREAKPOINTS[bp])
            else:
                return phrases[2]

        parent_obj = self.get_parent_instance(request, obj)
        if not (parent_obj and issubclass(parent_obj.plugin_class, BootstrapPluginBase)):
            raise ImproperlyConfigured("A BootstrapColumnPlugin requires a valid parent")

        glossary_fields = []
        units = [ungettext_lazy("{} unit", "{} units", i).format(i) for i in range(0, 13)]
        breakpoints = parent_obj.get_complete_glossary()['breakpoints']
        for bp in breakpoints:
            try:
                next_bp = breakpoints[breakpoints.index(bp) + 1]
                last = BS3_BREAKPOINT_KEYS.index(next_bp)
            except IndexError:
                next_bp = None
                last = None
            finally:
                first = BS3_BREAKPOINT_KEYS.index(bp)
                devices = ', '.join([force_text(BS3_BREAKPOINTS[b][2]) for b in BS3_BREAKPOINT_KEYS[first:last]])
            if breakpoints.index(bp) == 0:
                # first breakpoint
                choices = tuple(('col-{}-{}'.format(bp, i), units[i]) for i in range(1, 13))
                label = _("Column width for {}").format(devices)
                help_text = choose_help_text(
                    _("Number of column units for devices narrower than {} pixels."),
                    _("Number of column units for devices wider than {} pixels."),
                    _("Number of column units for all devices.")
                )
                glossary_fields.append(GlossaryField(
                    widgets.Select(choices=choices),
                    label=label,
                    name='{}-column-width'.format(bp),
                    initial='col-{}-12'.format(bp),
                    help_text=help_text))
            else:
                choices = (('', _("Inherit from above")),) + \
                    tuple(('col-{}-{}'.format(bp, i), units[i]) for i in range(1, 13))
                label = _("Column width for {}").format(devices)
                help_text = choose_help_text(
                    _("Override column units for devices narrower than {} pixels."),
                    _("Override column units for devices wider than {} pixels."),
                    _("Override column units for all devices.")
                )
                glossary_fields.append(GlossaryField(
                    widgets.Select(choices=choices),
                    label=label,
                    name='{}-column-width'.format(bp),
                    initial='',
                    help_text=help_text))

            # handle offset
            if breakpoints.index(bp) == 0:
                empty_offset_choice = _("No offset")
                offset_range = range(1, 13)
            else:
                empty_offset_choice = _("Inherit from above")
                offset_range = range(0, 13)
            choices = (('', empty_offset_choice),) + \
                tuple(('col-{}-offset-{}'.format(bp, i), units[i])
                      for i in offset_range)
            label = _("Offset for {}").format(devices)
            help_text = choose_help_text(
                _("Number of offset units for devices narrower than {} pixels."),
                _("Number of offset units for devices wider than {} pixels."),
                _("Number of offset units for all devices.")
            )
            glossary_fields.append(GlossaryField(
                widgets.Select(choices=choices),
                label=label,
                name='{}-column-offset'.format(bp),
                help_text=help_text))

            # handle column ordering using push/pull settings
            choices = (('', _("No reordering")),) + \
                tuple(('col-{}-push-{}'.format(bp, i), _("Push {}").format(units[i])) for i in range(0, 12)) + \
                tuple(('col-{}-pull-{}'.format(bp, i), _("Pull {}").format(units[i])) for i in range(0, 12))
            label = _("Column ordering for {0}").format(devices)
            help_text = choose_help_text(
                _("Column ordering for devices narrower than {} pixels."),
                _("Column ordering for devices wider than {} pixels."),
                _("Column ordering for all devices.")
            )
            glossary_fields.append(GlossaryField(
                widgets.Select(choices=choices),
                label=label,
                name='{}-column-ordering'.format(bp),
                help_text=help_text))

            # handle responsive utilies
            choices = (('', _("Default")), ('visible-{}'.format(bp), _("Visible")), ('hidden-{}'.format(bp), _("Hidden")),)
            label = _("Responsive utilities for {}").format(devices)
            help_text = choose_help_text(
                _("Utility classes for showing and hiding content by devices narrower than {} pixels."),
                _("Utility classes for showing and hiding content by devices wider than {} pixels."),
                _("Utility classes for showing and hiding content for all devices.")
            )
            glossary_fields.append(GlossaryField(
                widgets.RadioSelect(choices=choices),
                label=label,
                name='{}-responsive-utils'.format(bp),
                initial='',
                help_text=help_text))
        glossary_fields = [
            glossary_fields[i + len(glossary_fields) // len(breakpoints) * j]
            for i in range(0, len(glossary_fields) // len(breakpoints))
            for j in range(0, len(breakpoints))
        ]
        kwargs.update(glossary_fields=glossary_fields)
        return super(BootstrapColumnPlugin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        super(BootstrapColumnPlugin, self).save_model(request, obj, form, change)
        obj.sanitize_children()

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = super(BootstrapColumnPlugin, cls).sanitize_model(obj)
        parent_glossary = obj.get_parent_glossary()
        column_units = 12
        if isinstance(obj.glossary, str):
            obj.glossary=json.loads(obj.glossary)
        obj.glossary['container_max_widths'] = {}
        breakpoints = parent_glossary.get('breakpoints', [])
        for bp in BS3_BREAKPOINT_KEYS:
            width_key = '{0}-column-width'.format(bp)
            offset_key = '{0}-column-offset'.format(bp)
            if bp in breakpoints:
                width_val = obj.glossary.get(width_key, '').lstrip('col-{0}-'.format(bp))
                if width_val.isdigit():
                    column_units = int(width_val)
                new_width = float(parent_glossary['container_max_widths'][bp]) * column_units / 12
                new_width = round(new_width - app_settings.CMSPLUGIN_CASCADE['bootstrap3']['gutter'], 2)
                if new_width != obj.glossary['container_max_widths'].get(bp):
                    obj.glossary['container_max_widths'][bp] = new_width
                    sanitized = True
            else:
                # remove obsolete entries from own glossary
                # If no breakpoints are set, the plugin is not inside a BootstrapContainerPlugin,
                # probably in the clipboard placeholder. Don't delete widths and offsets from the
                # glossary in this case, as we would otherwise lose this information.
                if breakpoints:
                    if width_key in obj.glossary:
                        del obj.glossary[width_key]
                        sanitized = True
                    if offset_key in obj.glossary:
                        del obj.glossary[offset_key]
                        sanitized = True
        return sanitized

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapColumnPlugin, cls).get_identifier(obj)
        glossary = obj.get_complete_glossary()
        widths = []
        for bp in glossary.get('breakpoints', []):
            width = obj.glossary.get('{0}-column-width'.format(bp), '').replace('col-{0}-'.format(bp), '')

            if width:
                widths.append(width)
        if len(widths) > 1:
            content = _('widths: {0} units').format(' / '.join(widths))
        elif len(widths) == 1:
            width = int(widths[0])
            content = ungettext_lazy('default width: {0} unit', 'default width: {0} units', width).format(width)
        else:
            content = _('unknown width')
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(BootstrapColumnPlugin)
