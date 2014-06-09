# -*- coding: utf-8 -*-
import string
from django.forms import widgets
from django.forms.widgets import RadioFieldRenderer
from django.utils.html import format_html, format_html_join
from django.utils.encoding import force_text
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap3 import settings
from cmsplugin_cascade.plugin_base import PartialFormField
from cmsplugin_cascade.widgets import MultipleInlineStylesWidget
from cmsplugin_cascade.bootstrap3.plugin_base import BootstrapPluginBase


class ContainerRadioFieldRenderer(RadioFieldRenderer):
    map_icon = { 'xs': 'mobile-phone', 'sm': 'tablet', 'md': 'laptop', 'lg': 'desktop' }

    def render(self):
        return format_html('<div class="row">{0}</div>',
            format_html_join('', '<div class="col-sm-3 text-center">'
                '<div class="thumbnail"><i class="icon-{1}" style="font-size:50pt;"></i><h4>{0}</h4></div>'
                '</div>', ((force_text(w), self.map_icon[w.choice_value]) for w in self)
            ))


class BootstrapContainerPlugin(BootstrapPluginBase):
    name = _("Container")
    default_css_class = 'container'
    require_parent = False
    CONTEXT_WIDGET_CHOICES = (
        ('lg', _('Large (>1200px)')), ('md', _('Medium (>992px)')),
        ('sm', _('Small (>768px)')), ('xs', _('Tiny (<768px)')),
    )
    partial_fields = (
        PartialFormField('breakpoint',
            widgets.RadioSelect(choices=CONTEXT_WIDGET_CHOICES, renderer=ContainerRadioFieldRenderer),
            label=_('Display Breakpoint'), initial=settings.CMS_CASCADE_BOOTSTRAP3_BREAKPOINT,
            help_text=_("Narrowest display for Bootstrap's grid system.")
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        try:
            texts = [d for c, d in cls.CONTEXT_WIDGET_CHOICES if c == obj.context.get('breakpoint')]
            return _('Narrowest grid: {0}').format(texts[0].lower())
        except (TypeError, KeyError, ValueError):
            return ''

plugin_pool.register_plugin(BootstrapContainerPlugin)


class BootstrapRowPlugin(BootstrapPluginBase):
    name = _("Row")
    default_css_class = 'row'
    parent_classes = ['BootstrapContainerPlugin', 'BootstrapColumnPlugin']
    ROW_NUM_COLUMNS = (1, 2, 3, 4, 6, 12,)
    partial_fields = (
        PartialFormField('-num-children-',  # temporary field, not stored in the database
            widgets.Select(choices=tuple((i, ungettext_lazy('{0} column', '{0} columns', i).format(i)) for i in ROW_NUM_COLUMNS)),
            label=_('Number of Columns'), help_text=_('Number of columns to be created with this row.')
        ),
        PartialFormField('inline_styles', MultipleInlineStylesWidget(['min-height']),
            label=_('Inline Styles'), help_text=_('Minimum height for this row.')
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        num_cols = obj.get_children().count()
        return ungettext_lazy('with {0} column', 'with {0} columns', num_cols).format(num_cols)

    def save_model(self, request, obj, form, change):
        wanted_children = int(obj.context['-num-children-'])
        super(BootstrapRowPlugin, self).save_model(request, obj, form, change)
        child_context = { 'xs-column-width': 'col-xs-{0}'.format(12 // wanted_children) }
        self.extend_children(obj, wanted_children, BootstrapColumnPlugin, child_context=child_context)

plugin_pool.register_plugin(BootstrapRowPlugin)


class BootstrapColumnPlugin(BootstrapPluginBase):
    name = _("Column")
    parent_classes = ['BootstrapRowPlugin']
    generic_child_classes = settings.CMS_CASCADE_LEAF_PLUGINS
    default_width_widget = PartialFormField('xs-column-width',
        widgets.Select(choices=tuple(('col-xs-{0}'.format(i), ungettext_lazy('{0} unit', '{0} units', i).format(i))
                                     for i in range(1, 13))),
        label=_('Default Width'), initial='col-xs-12',
        help_text=_('Column width for all devices, down to phones narrower than 768 pixels.'),
    )
    default_css_attributes = tuple('{0}-column-width'.format(size) for size in ('xs', 'sm', 'md', 'lg',))

    def get_form(self, request, obj=None, **kwargs):
        def get_column_width(prefix):
            # full_context from closure
            column_width = full_context.get('{0}-column-width'.format(prefix)) or '12'
            return int(string.replace(column_width, 'col-{0}-'.format(prefix), ''))

        self.partial_fields = [self.default_width_widget]
        if obj:
            full_context = obj.get_full_context()
            breakpoint = full_context.get('breakpoint')
            if breakpoint in ('lg', 'md', 'sm',):
                xs_column_width = get_column_width('xs')
                choices = (('', _('Unset')),) + tuple(('col-sm-{0}'.format(i), ungettext_lazy('{0} unit', '{0} units', i).format(i))
                                   for i in range(1, xs_column_width + 1))
                self.partial_fields.append(PartialFormField('sm-column-width',
                    widgets.Select(choices=choices), label=_('Width for Devices >768px'),
                    help_text=_('Column width for all devices wider than 768 pixels, such as tablets.')
                ))
                choices = (('', _('No offset')),) + tuple(('col-sm-offset-{0}'.format(i), ungettext_lazy('{0} unit', '{0} units', i).format(i))
                                   for i in range(1, xs_column_width))
                self.partial_fields.append(PartialFormField('sm-column-offset',
                    widgets.Select(choices=choices), label=_('Offset for Devices >768px'),
                    help_text=_('Column offset for all devices wider than 768 pixels, such as tablets.')
                ))
            if breakpoint in ('lg', 'md',):
                sm_column_width = get_column_width('sm')
                choices = (('', _('Unset')),) + tuple(('col-md-{0}'.format(i), ungettext_lazy('{0} unit', '{0} units', i).format(i))
                                   for i in range(1, sm_column_width + 1))
                self.partial_fields.append(PartialFormField('md-column-width',
                    widgets.Select(choices=choices), label=_('Width for Devices >992px'),
                    help_text=_('Column width for all devices wider than 992 pixels, such as laptops.')
                ))
                choices = (('', _('No offset')),) + tuple(('col-md-offset-{0}'.format(i), ungettext_lazy('{0} unit', '{0} units', i).format(i))
                                   for i in range(1, sm_column_width))
                self.partial_fields.append(PartialFormField('md-column-offset',
                    widgets.Select(choices=choices), label=_('Offset for Devices >992px'),
                    help_text=_('Column offset for all devices wider than 992 pixels, such as laptops.')
                ))
            if breakpoint in ('lg',):
                md_column_width = get_column_width('md')
                choices = (('', _('Unset')),) + tuple(('col-lg-{0}'.format(i), ungettext_lazy('{0} unit', '{0} units', i).format(i))
                                   for i in range(1, md_column_width + 1))
                self.partial_fields.append(PartialFormField('lg-column-width',
                    widgets.Select(choices=choices), label=_('Width for Devices >1200px'),
                    help_text=_('Column width for all devices wider than 1200 pixels, such as large desktops.'),
                ))
                choices = (('', _('No offset')),) + tuple(('col-lg-offset-{0}'.format(i), ungettext_lazy('{0} unit', '{0} units', i).format(i))
                                   for i in range(1, md_column_width))
                self.partial_fields.append(PartialFormField('lg-column-offset',
                    widgets.Select(choices=choices), label=_('Offset for Devices >1200px'),
                    help_text=_('Column offset for all devices wider than 1200 pixels, such as large desktops.')
                ))
        return super(BootstrapColumnPlugin, self).get_form(request, obj, **kwargs)

    @classmethod
    def get_identifier(cls, obj):
        try:
            width = int(string.replace(obj.context['xs-column-width'], 'col-xs-', ''))
            return ungettext_lazy('default width: {0} unit', 'default width: {0} units', width).format(width)
        except (TypeError, KeyError, ValueError):
            return _('unknown width')

plugin_pool.register_plugin(BootstrapColumnPlugin)
