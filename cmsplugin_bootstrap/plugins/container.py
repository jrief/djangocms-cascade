# -*- coding: utf-8 -*-
import string
from django.forms import widgets
from django.forms.widgets import RadioFieldRenderer
from django.utils.html import format_html, format_html_join
from django.utils.encoding import force_text
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
print 'Now here container'
from cms.plugin_pool import plugin_pool
from cmsplugin_bootstrap import settings
from cmsplugin_bootstrap.plugin_base import BootstrapPluginBase, PartialFormField
from cmsplugin_bootstrap.widgets import MultipleTextInputWidget, MultipleInlineStylesWidget, CSS_VERTICAL_SPACING


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
    child_classes = ['BootstrapRowPlugin']
    default_css_class = 'container'
    CONTEXT_WIDGET_CHOICES = (
        ('lg', _('Large (>1200px)')), ('md', _('Medium (>992px)')),
        ('sm', _('Small (>768px)')), ('xs', _('Tiny (<768px)')),
    )
    partial_fields = (
        PartialFormField('breakpoint',
            widgets.RadioSelect(choices=CONTEXT_WIDGET_CHOICES, renderer=ContainerRadioFieldRenderer),
            label=_('Display Breakpoint'), initial='xs',  # settings.BOOTSTRAP_DEFAULT_BREAKPOINT,
            help_text=_("Narrowest display for Bootstrap's grid system.")
        ),
        PartialFormField('inline_styles', MultipleInlineStylesWidget(),
            label=_('Inline Styles'), help_text=_('Margins and minimum height for container.')
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        try:
            texts = [d for c, d in cls.CONTEXT_WIDGET_CHOICES if c == obj.context.get('breakpoint')]
            return _('Narrowest grid: {0}').format(texts[0].lower())
        except (TypeError, KeyError, ValueError):
            return u''

plugin_pool.register_plugin(BootstrapContainerPlugin)


class BootstrapRowPlugin(BootstrapPluginBase):
    name = _("Row")
    default_css_class = 'row'
    parent_classes = ['BootstrapContainerPlugin']
    require_parent = True
    child_classes = ['BootstrapColumnPlugin']
    partial_fields = (
        PartialFormField('num-columns',
            widgets.Select(choices=tuple((i, ungettext_lazy('{0} column', '{0} columns', i).format(i)) for i in range(1, 13))),
            label=_('Number of Columns'), help_text=_('Number of columns to be created with this row.')
        ),
        PartialFormField('inline_styles', MultipleTextInputWidget(CSS_VERTICAL_SPACING),
            label=_('Inline Styles'), help_text=_('Minimum height for this row.')
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        try:
            num_cols = obj.get_children().count()
            return ungettext_lazy('with {0} column', 'with {0} columns', num_cols).format(num_cols)
        except (TypeError, KeyError, ValueError):
            return _('unset')

    def get_object(self, request, object_id):
        obj = super(BootstrapRowPlugin, self).get_object(request, object_id)
        if obj:
            obj.context['num-columns'] = obj.get_children().count()
        return obj

    def save_model(self, request, obj, form, change):
        from cms.api import add_plugin
        # adopt number of columns automatically
        current_cols = obj.get_children().count()
        wanted_cols = int(obj.context['num-columns'])
        del obj.context['num-columns']
        for _ in range(current_cols, wanted_cols):
            column = add_plugin(obj.placeholder, BootstrapColumnPlugin, obj.language, target=obj)
            column.context.update({ 'xs-column-width': 'col-xs-12' })
            column.save()
        return super(BootstrapRowPlugin, self).save_model(request, obj, form, change)

plugin_pool.register_plugin(BootstrapRowPlugin)


class BootstrapColumnPlugin(BootstrapPluginBase):
    name = _("Column")
    parent_classes = ['BootstrapRowPlugin']
    require_parent = True
    child_classes = ['TextPlugin', 'BootstrapRowPlugin', 'CarouselPlugin', 'SimpleWrapperPlugin']
    default_width_widget = PartialFormField('xs-column-width',
        widgets.Select(choices=tuple(('col-xs-{0}'.format(i), ungettext_lazy('{0} unit', '{0} units', i).format(i))
                                     for i in range(1, 13))),
        label=_('Default Width'), initial='col-xs-12',
        help_text=_('Column width for all devices, down to phones narrower than 768 pixels.'),
    )
    default_attributes = tuple('{0}-column-width'.format(size) for size in ('xs', 'sm', 'md', 'lg',))

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

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(BootstrapColumnPlugin, cls).get_css_classes(obj)
        for attr in cls.default_attributes:
            css_class = obj.context.get(attr)
            if css_class:
                css_classes.append(css_class)
        return css_classes

plugin_pool.register_plugin(BootstrapColumnPlugin)
