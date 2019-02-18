# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import widgets
from django.forms.fields import ChoiceField
from django.forms.models import ModelForm
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.translation import ungettext_lazy, ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade import app_settings
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.fields import GlossaryField
from .plugin_base import BootstrapPluginBase
from . import grid


def get_widget_choices():
    breakpoints = app_settings.CMSPLUGIN_CASCADE['bootstrap4']['fluid_bounds']
    widget_choices = []
    for index, (bp, bound) in enumerate(breakpoints.items()):
        if index == 0:
            widget_choices.append((bp.name, "{} (<{:.1f}px)".format(bp.label, bound.max)))
        elif index == len(breakpoints) - 1:
            widget_choices.append((bp.name, "{} (≥{:.1f}px)".format(bp.label, bound.min)))
        else:
            widget_choices.append((bp.name, "{} (≥{:.1f}px and <{:.1f}px)".format(bp.label, bound.min, bound.max)))
    return widget_choices


class ContainerBreakpointsWidget(widgets.CheckboxSelectMultiple):
    template_name = 'cascade/forms/widgets/container_breakpoints.html'

    def render(self, name, value, attrs=None, renderer=None):
        attrs = dict(attrs, version=4)
        return super(ContainerBreakpointsWidget, self).render(name, value, attrs, renderer)


class BootstrapContainerForm(ModelForm):
    """
    Form class to validate the container.
    """
    def clean_glossary(self):
        if len(self.cleaned_data['glossary']['breakpoints']) == 0:
            raise ValidationError(_("At least one breakpoint must be selected."))
        return self.cleaned_data['glossary']


class ContainerGridMixin(object):
    def get_grid_instance(self):
        fluid = self.glossary.get('fluid', False)
        try:
            breakpoints = [getattr(grid.Breakpoint, bp) for bp in self.glossary['breakpoints']]
        except KeyError:
            breakpoints = [bp for bp in grid.Breakpoint]
        if fluid:
            bounds = dict((bp, grid.fluid_bounds[bp]) for bp in breakpoints)
        else:
            bounds = dict((bp, grid.default_bounds[bp]) for bp in breakpoints)
        return grid.Bootstrap4Container(bounds=bounds)


class BootstrapContainerPlugin(BootstrapPluginBase):
    name = _("Container")
    parent_classes = None
    require_parent = False
    form = BootstrapContainerForm
    glossary_variables = ['container_max_widths', 'media_queries']
    glossary_field_order = ['breakpoints', 'fluid']
    model_mixins = (ContainerGridMixin,)

    breakpoints = GlossaryField(
        ContainerBreakpointsWidget(choices=get_widget_choices()),
        label=_('Available Breakpoints'),
        initial=[bp.name for bp in app_settings.CMSPLUGIN_CASCADE['bootstrap4']['fluid_bounds'].keys()],
        help_text=_("Supported display widths for Bootstrap's grid system."),
    )

    fluid = GlossaryField(
        widgets.CheckboxInput(),
        label=_('Fluid Container'), initial=False,
        help_text=_("Changing your outermost '.container' to '.container-fluid'.")
    )

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapContainerPlugin, cls).get_identifier(obj)
        breakpoints = obj.glossary.get('breakpoints')
        content = obj.glossary.get('fluid') and '(fluid) ' or ''
        if breakpoints:
            breakpoints = app_settings.CMSPLUGIN_CASCADE['bootstrap4']['fluid_bounds']
            devices = ', '.join([force_text(bp.label) for bp in breakpoints])
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

plugin_pool.register_plugin(BootstrapContainerPlugin)


class BootstrapRowForm(ManageChildrenFormMixin, ModelForm):
    """
    Form class to add non-materialized field to count the number of children.
    """
    ROW_NUM_COLUMNS = [1, 2, 3, 4, 6, 12]
    num_children = ChoiceField(
        choices=[(i, ungettext_lazy('{0} column', '{0} columns', i).format(i)) for i in ROW_NUM_COLUMNS],
        initial=3, label=_('Columns'),
        help_text=_('Number of columns to be created with this row.'))


class RowGridMixin(object):
    def get_grid_instance(self):
        row = grid.Bootstrap4Row()
        query = Q(plugin_type='BootstrapContainerPlugin') | Q(plugin_type='BootstrapColumnPlugin') \
          | Q(plugin_type='BootstrapJumbotronPlugin')
        container = self.get_ancestors().order_by('depth').filter(query).last().get_bound_plugin().get_grid_instance()
        container.add_row(row)
        return row


class BootstrapRowPlugin(BootstrapPluginBase):
    name = _("Row")
    default_css_class = 'row'
    parent_classes = ['BootstrapContainerPlugin', 'BootstrapColumnPlugin', 'BootstrapJumbotronPlugin']
    form = BootstrapRowForm
    fields = ['num_children', 'glossary']
    model_mixins = (RowGridMixin,)

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapRowPlugin, cls).get_identifier(obj)
        num_cols = obj.get_num_children()
        content = ungettext_lazy("with {0} column", "with {0} columns", num_cols).format(num_cols)
        return format_html('{0}{1}', identifier, content)

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super(BootstrapRowPlugin, self).save_model(request, obj, form, change)
        child_glossary = {'xs-column-width': 'col'}
        self.extend_children(obj, wanted_children, BootstrapColumnPlugin, child_glossary=child_glossary)

plugin_pool.register_plugin(BootstrapRowPlugin)


class ColumnGridMixin(object):
    valid_keys = ['xs-column-width', 'sm-column-width', 'md-column-width', 'lg-column-width', 'xs-column-width',
                  'xs-column-offset', 'sm-column-offset', 'md-column-offset', 'lg-column-offset', 'xs-column-offset']
    def get_grid_instance(self):
        column = None
        query = Q(plugin_type='BootstrapRowPlugin')
        row_obj = self.get_ancestors().order_by('depth').filter(query).last().get_bound_plugin()
        # column_siblings = row_obj.get_descendants().order_by('depth').filter(plugin_type='BootstrapColumnPlugin')
        row = row_obj.get_grid_instance()
        for column_sibling in self.get_siblings():
            classes = [val for key, val in column_sibling.get_bound_plugin().glossary.items()
                       if key in self.valid_keys and val]
            if column_sibling.pk == self.pk:
                column = grid.Bootstrap4Column(classes)
                row.add_column(column)
            else:
                row.add_column(grid.Bootstrap4Column(classes))
        return column


class BootstrapColumnPlugin(BootstrapPluginBase):
    name = _("Column")
    parent_classes = ('BootstrapRowPlugin',)
    child_classes = ('BootstrapJumbotronPlugin',)
    alien_child_classes = True
    default_css_attributes = [fmt.format(bp.name) for bp in grid.Breakpoint
        for fmt in ('{}-column-width', '{}-column-offset', '{}-column-ordering', '{}-responsive-utils')]
    glossary_variables = ['container_max_widths']
    model_mixins = (ColumnGridMixin,)

    def get_form(self, request, obj=None, **kwargs):
        def choose_help_text(*phrases):
            bounds = 'fluid_bounds' if container.glossary.get('fluid') else 'default_bounds'
            bs4_breakpoints = app_settings.CMSPLUGIN_CASCADE['bootstrap4'][bounds]
            if last:
                return phrases[0].format(bs4_breakpoints[last].max)
            elif len(breakpoints) > 1:
                return phrases[1].format(bs4_breakpoints[first].min)
            else:
                return phrases[2]
            
        if 'parent' in self._cms_initial_attributes:
            container=self._cms_initial_attributes['parent'].get_ancestors().order_by('depth').last().get_bound_plugin()
        else:
            containers=obj.get_ancestors().filter(plugin_type='BootstrapContainerPlugin')
            if containers:
                container=containers.order_by('depth').last().get_bound_plugin()
            else:
                jumbotrons=obj.get_ancestors().filter(plugin_type='BootstrapJumbotronPlugin')
                container=jumbotrons.order_by('depth').last().get_bound_plugin()
        breakpoints = container.glossary['breakpoints']

        glossary_fields = []
        units = [ungettext_lazy("{} unit", "{} units", i).format(i) for i in range(0, 13)]
        for bp in breakpoints:
            try:
                last = getattr(grid.Breakpoint, breakpoints[breakpoints.index(bp) + 1])
            except IndexError:
                last = None
            finally:
                first = getattr(grid.Breakpoint, bp)
                devices = ', '.join([force_text(b.label) for b in grid.Breakpoint.range(first, last)])

            if bp == 'xs':
                choices = [('col', _("Flex column"))]
                choices.extend(('col-{}'.format(i), _("{} fixed column").format(units[i])) for i in range(1, 13))
                choices.append(('col-auto', _("Auto column")))
            else:
                choices = [('col-{}'.format(bp), _("Flex column"))]
                choices.extend(('col-{}-{}'.format(bp, i), _("{} fixed column").format(units[i])) for i in range(1, 13))
                choices.append(('col-{}-auto'.format(bp), _("Auto column")))
            if breakpoints.index(bp) == 0:
                # first breakpoint
                glossary_fields.append(GlossaryField(
                    widgets.Select(choices=choices),
                    label=_("Column width for {}").format(devices),
                    name='{}-column-width'.format(bp),
                    initial='col-{}-12'.format(bp),
                    help_text=choose_help_text(
                        _("Column width for devices narrower than {:.1f} pixels."),
                        _("Column width for devices wider than {:.1f} pixels."),
                        _("Column width for all devices."),
                    )
                ))
            else:
                # wider breakpoints may inherit from next narrower ones
                choices.insert(0, ('', _("Inherit from above")))
                glossary_fields.append(GlossaryField(
                    widgets.Select(choices=choices),
                    label=_("Column width for {}").format(devices),
                    name='{}-column-width'.format(bp),
                    initial='',
                    help_text=choose_help_text(
                        _("Override column width for devices narrower than {:.1f} pixels."),
                        _("Override column width for devices wider than {:.1f} pixels."),
                        _("Override column width for all devices."),
                    )
                ))

            # handle offset
            if breakpoints.index(bp) == 0:
                choices = [('', _("No offset"))]
                offset_range = range(1, 13)
            else:
                choices = [('', _("Inherit from above"))]
                offset_range = range(0, 13)
            if bp == 'xs':
                choices.extend(('offset-{}'.format(i), units[i]) for i in offset_range)
            else:
                choices.extend(('offset-{}-{}'.format(bp, i), units[i]) for i in offset_range)
            label = _("Offset for {}").format(devices)
            help_text = choose_help_text(
                _("Offset width for devices narrower than {:.1f} pixels."),
                _("Offset width for devices wider than {:.1f} pixels."),
                _("Offset width for all devices.")
            )
            glossary_fields.append(GlossaryField(
                widgets.Select(choices=choices),
                label=label,
                name='{}-column-offset'.format(bp),
                help_text=help_text))

            # handle column reordering
            choices = [('', _("No reordering"))]
            if bp == 'xs':
                choices.extend(('order-{}'.format(i), _("Reorder by {}").format(units[i])) for i in range(1, 13))
            else:
                choices.extend(('order-{}-{}'.format(bp, i), _("Reorder by {}").format(units[i])) for i in range(1, 13))
            label = _("Reordering for {}").format(devices)
            help_text = choose_help_text(
                _("Reordering for devices narrower than {:.1f} pixels."),
                _("Reordering for devices wider than {:.1f} pixels."),
                _("Reordering for all devices.")
            )
            glossary_fields.append(GlossaryField(
                widgets.Select(choices=choices),
                label=label,
                name='{}-column-ordering'.format(bp),
                help_text=help_text))

            # handle responsive utilities
            choices = [('', _("Default")), ('visible-{}'.format(bp), _("Visible")), ('hidden-{}'.format(bp), _("Hidden"))]
            label = _("Responsive utilities for {}").format(devices)
            help_text = choose_help_text(
                _("Utility classes for showing and hiding content by devices narrower than {:.1f} pixels."),
                _("Utility classes for showing and hiding content by devices wider than {:.1f} pixels."),
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
            width = widths[0]
            content = ungettext_lazy('default width: {0} unit', 'default width: {0} units', width).format(width)
        else:
            content = _('unknown width')
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(BootstrapColumnPlugin)
