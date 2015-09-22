# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import itertools
from django.forms import widgets
from django.core.exceptions import ValidationError
from django.utils.html import format_html, format_html_join
from django.utils.encoding import force_text
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.forms.models import ModelForm
from django.forms.fields import ChoiceField
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.fields import PartialFormField
from .plugin_base import FoundationPluginBase
from .settings import CASCADE_BREAKPOINTS_DICT, CASCADE_BREAKPOINTS_LIST, CASCADE_FOUNDATION4_GUTTER


class ContainerBreakpointsRenderer(widgets.CheckboxFieldRenderer):
    def render(self):
        return format_html('<div class="form-row">{0}</div>',
            format_html_join('', '<div class="field-box">'
                '<div class="container-thumbnail"><i class="icon-{1}"></i><div class="label">{0}</div></div>'
                '</div>', ((force_text(w), CASCADE_BREAKPOINTS_DICT[w.choice_value][1]) for w in self)
            ))


class FoundationContainerForm(ModelForm):
    """
    Form class to validate the container.
    """
    def clean_glossary(self):
        if len(self.cleaned_data['glossary']['breakpoints']) == 0:
            raise ValidationError(_("At least one breakpoint must be selected."))
        return self.cleaned_data['glossary']


class FoundationContainerPlugin(FoundationPluginBase):
    name = _("Container")
    require_parent = False
    form = FoundationContainerForm
    WIDGET_CHOICES = (
        ('small', _("Tiny (<{small[0]}em)".format(**CASCADE_BREAKPOINTS_DICT))),
        ('medium', _("Small (≥{small[0]}em and <{medium[0]}em)".format(**CASCADE_BREAKPOINTS_DICT))),
        ('large', _("Medium (≥{medium[0]}em and <{large[0]}em)".format(**CASCADE_BREAKPOINTS_DICT))),
        ('xlarge', _("Large (≥{large[0]}em)".format(**CASCADE_BREAKPOINTS_DICT))),
    )
    glossary_fields = (
        PartialFormField('breakpoints',
            widgets.CheckboxSelectMultiple(choices=WIDGET_CHOICES, renderer=ContainerBreakpointsRenderer),
            label=_('Available Breakpoints'),
            initial=['lg', 'md', 'sm', 'xs'],
            help_text=_("Supported display widths for Foundation's grid system.")
        ),
        PartialFormField('fluid',
            widgets.CheckboxInput(),
            label=_('Fluid Container'), initial=False,
            help_text=_("Changing your outermost '.container' to '.container-fluid'.")
        ),
    )
    glossary_variables = ['container_max_widths', 'media_queries']

    class Media:
        css = {'all': ('//netdna.bootstrapcdn.com/font-awesome/3.2.1/css/font-awesome.min.css',)}
        js = ['cascade/js/admin/containerplugin.js']

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(FoundationContainerPlugin, cls).get_identifier(obj)
        breakpoints = obj.glossary.get('breakpoints')
        content = obj.glossary.get('fluid') and '(fluid) ' or ''
        if breakpoints:
            devices = ', '.join([force_text(CASCADE_BREAKPOINTS_DICT[bp][2]) for bp in breakpoints])
            content = _("{0}for {1}").format(content, devices)
        return format_html('{0}{1}', identifier, content)

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(FoundationContainerPlugin, cls).get_css_classes(obj)
        if obj.glossary.get('fluid'):
            css_classes.append('container-fluid')
        else:
            css_classes.append('container')
        return css_classes

    def save_model(self, request, obj, form, change):
        super(FoundationContainerPlugin, self).save_model(request, obj, form, change)
        obj.sanitize_children()

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = super(FoundationContainerPlugin, cls).sanitize_model(obj)
        parent_glossary = obj.get_parent_glossary()
        # compute the max width and the required media queries for each chosen breakpoint
        obj.glossary['container_max_widths'] = max_widths = {}
        obj.glossary['media_queries'] = media_queries = {}
        breakpoints = obj.glossary.get('breakpoints', [])
        last_index = len(breakpoints) - 1
        for index, bp in enumerate(breakpoints):
            try:
                max_widths[bp] = parent_glossary['container_max_widths'][bp]
            except KeyError:
                max_widths[bp] = CASCADE_BREAKPOINTS_DICT[bp][3]
            if last_index > 0:
                if index == 0:
                    next_bp = breakpoints[1]
                    media_queries[bp] = ['(max-width: {0}px)'.format(CASCADE_BREAKPOINTS_DICT[next_bp][0])]
                elif index == last_index:
                    media_queries[bp] = ['(min-width: {0}px)'.format(CASCADE_BREAKPOINTS_DICT[bp][0])]
                else:
                    next_bp = breakpoints[index + 1]
                    media_queries[bp] = ['(min-width: {0}px)'.format(CASCADE_BREAKPOINTS_DICT[bp][0]),
                                         '(max-width: {0}px)'.format(CASCADE_BREAKPOINTS_DICT[next_bp][0])]
        return sanitized

    def get_parent_classes(self, slot, page):
        if self.cms_plugin_instance and self.cms_plugin_instance.parent:
            # enforce that a ContainerPlugin can't have a parent
            return []
        return super(FoundationContainerPlugin, self).get_parent_classes(slot, page)

plugin_pool.register_plugin(FoundationContainerPlugin)


class FoundationRowForm(ManageChildrenFormMixin, ModelForm):
    """
    Form class to add non-materialized field to count the number of children.
    """
    ROW_NUM_COLUMNS = (1, 2, 3, 4, 6, 12,)
    num_children = ChoiceField(choices=tuple((i, ungettext_lazy('{0} column', '{0} columns', i).format(i)) for i in ROW_NUM_COLUMNS),
        initial=3, label=_('Columns'),
        help_text=_('Number of columns to be created with this row.'))


class FoundationRowPlugin(FoundationPluginBase):
    name = _("Row")
    default_css_class = 'row'
    parent_classes = ('FoundationContainerPlugin', 'FoundationColumnPlugin',)
    form = FoundationRowForm
    fields = ('num_children', 'glossary',)

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(FoundationRowPlugin, cls).get_identifier(obj)
        num_cols = obj.get_children().count()
        content = ungettext_lazy("with {0} column", "with {0} columns", num_cols).format(num_cols)
        return format_html('{0}{1}', identifier, content)

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super(FoundationRowPlugin, self).save_model(request, obj, form, change)
        parent_glossary = obj.get_complete_glossary()
        narrowest = parent_glossary['breakpoints'][0]
        column_width = 12 // wanted_children
        child_glossary = {
            '{0}-column-width'.format(narrowest): 'col-{0}-{1}'.format(narrowest, column_width)
        }
        self.extend_children(obj, wanted_children, FoundationColumnPlugin, child_glossary=child_glossary)

plugin_pool.register_plugin(FoundationRowPlugin)


class FoundationColumnPlugin(FoundationPluginBase):
    name = _("Column")
    parent_classes = ('FoundationRowPlugin',)
    alien_child_classes = True
    default_css_attributes = list(itertools.chain(*(('{}-column-width'.format(s),
        '{}-column-offset'.format(s), '{}-column-ordering'.format(s), '{}-responsive-utils'.format(s),)
        for s in CASCADE_BREAKPOINTS_LIST)))
    glossary_variables = ['container_max_widths']

    def get_form(self, request, obj=None, **kwargs):
        def chose_help_text(*phrases):
            if next_bp:
                return phrases[0].format(*CASCADE_BREAKPOINTS_DICT[next_bp])
            elif len(breakpoints) > 1:
                return phrases[1].format(*CASCADE_BREAKPOINTS_DICT[bp])
            else:
                return phrases[2]

        glossary_fields = []
        parent_obj, parent_plugin = self.parent.get_plugin_instance()
        units = [ungettext_lazy("{} unit", "{} units", i).format(i) for i in range(0, 13)]
        if isinstance(parent_plugin, FoundationPluginBase):
            breakpoints = parent_obj.get_complete_glossary()['breakpoints']
            for bp in breakpoints:
                try:
                    next_bp = breakpoints[breakpoints.index(bp) + 1]
                    last = CASCADE_BREAKPOINTS_LIST.index(next_bp)
                except IndexError:
                    next_bp = None
                    last = None
                finally:
                    first = CASCADE_BREAKPOINTS_LIST.index(bp)
                    devices = ', '.join([force_text(CASCADE_BREAKPOINTS_DICT[b][2]) for b in CASCADE_BREAKPOINTS_LIST[first:last]])
                if breakpoints.index(bp) == 0:
                    # first breakpoint
                    choices = tuple(('col-{}-{}'.format(bp, i), units[i]) for i in range(1, 13))
                    label = _("Column width for {}").format(devices)
                    help_text = chose_help_text(
                        _("Number of column units for devices narrower than {} pixels."),
                        _("Number of column units for devices wider than {} pixels."),
                        _("Number of column units for all devices.")
                    )
                    glossary_fields.append(PartialFormField('{}-column-width'.format(bp),
                        widgets.Select(choices=choices),
                        initial='col-{}-12'.format(bp), label=label, help_text=help_text))
                else:
                    choices = (('', _("Inherit from above")),) + \
                        tuple(('col-{}-{}'.format(bp, i), units[i]) for i in range(1, 13))
                    label = _("Column width for {}").format(devices)
                    help_text = chose_help_text(
                        _("Override column units for devices narrower than {} pixels."),
                        _("Override column units for devices wider than {} pixels."),
                        _("Override column units for all devices.")
                    )
                    glossary_fields.append(PartialFormField('{}-column-width'.format(bp),
                        widgets.Select(choices=choices),
                        initial='', label=label, help_text=help_text))

                # handle offset
                choices = (('', _("No offset")),) + \
                    tuple(('col-{}-offset-{}'.format(bp, i), units[i]) for i in range(1, 12))
                label = _("Offset for {}").format(devices)
                help_text = chose_help_text(
                    _("Number of offset units for devices narrower than {} pixels."),
                    _("Number of offset units for devices wider than {} pixels."),
                    _("Number of offset units for all devices.")
                )
                glossary_fields.append(PartialFormField('{}-column-offset'.format(bp),
                    widgets.Select(choices=choices), label=label, help_text=help_text))

                # handle column ordering using push/pull settings
                choices = (('', _("No reordering")),) + \
                    tuple(('col-{}-push-{}'.format(bp, i), _("Push {}").format(units[i])) for i in range(0, 12)) + \
                    tuple(('col-{}-pull-{}'.format(bp, i), _("Pull {}").format(units[i])) for i in range(0, 12))
                label = _("Column ordering for {0}").format(devices)
                help_text = chose_help_text(
                    _("Column ordering for devices narrower than {} pixels."),
                    _("Column ordering for devices wider than {} pixels."),
                    _("Column ordering for all devices.")
                )
                glossary_fields.append(PartialFormField('{}-column-ordering'.format(bp),
                    widgets.Select(choices=choices), label=label, help_text=help_text))

                # handle responsive utilies
                choices = (('', _("Default")), ('visible-{}'.format(bp), _("Visible")), ('hidden-{}'.format(bp), _("Hidden")),)
                label = _("Responsive utilities for {}").format(devices)
                help_text = chose_help_text(
                    _("Utility classes for showing and hiding content by devices narrower than {} pixels."),
                    _("Utility classes for showing and hiding content by devices wider than {} pixels."),
                    _("Utility classes for showing and hiding content for all devices.")
                )
                glossary_fields.append(PartialFormField('{}-responsive-utils'.format(bp),
                    widgets.RadioSelect(choices=choices), label=label, help_text=help_text, initial=''))
        glossary_fields = [
            glossary_fields[i + len(glossary_fields) // len(breakpoints) * j]
            for i in range(0, len(glossary_fields) // len(breakpoints))
            for j in range(0, len(breakpoints))
        ]
        kwargs.update(glossary_fields=glossary_fields)
        return super(FoundationColumnPlugin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        super(FoundationColumnPlugin, self).save_model(request, obj, form, change)
        obj.sanitize_children()

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = super(FoundationColumnPlugin, cls).sanitize_model(obj)
        parent_glossary = obj.get_parent_glossary()
        column_units = 12
        obj.glossary['container_max_widths'] = {}
        breakpoints = parent_glossary.get('breakpoints', [])
        for bp in CASCADE_BREAKPOINTS_LIST:
            width_key = '{0}-column-width'.format(bp)
            offset_key = '{0}-column-offset'.format(bp)
            if bp in breakpoints:
                width_val = obj.glossary.get(width_key, '').lstrip('col-{0}-'.format(bp))
                if width_val.isdigit():
                    column_units = int(width_val)
                new_width = parent_glossary['container_max_widths'][bp] * column_units / 12 - CASCADE_BOOTSTRAP3_GUTTER
                if new_width != obj.glossary['container_max_widths'].get(bp):
                    obj.glossary['container_max_widths'][bp] = new_width
                    sanitized = True
            else:
                # remove obsolete entries from own glossary
                # If no breakpoints are set, the plugin is not inside a FoundationContainerPlugin,
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
        identifier = super(FoundationColumnPlugin, cls).get_identifier(obj)
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

plugin_pool.register_plugin(FoundationColumnPlugin)
