# -*- coding: utf-8 -*-
import six
import string
import itertools
from django.forms import widgets
from django.forms.widgets import RadioFieldRenderer
from django.utils.html import format_html, format_html_join
from django.utils.encoding import force_text
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.forms.models import ModelForm
from django.forms.fields import ChoiceField
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.widgets import MultipleCascadingSizeWidget
from .plugin_base import BootstrapPluginBase
from .settings import CASCADE_BREAKPOINTS_DICT, CASCADE_BREAKPOINTS_LIST, CMS_CASCADE_LEAF_PLUGINS


class ContainerRadioFieldRenderer(RadioFieldRenderer):
    def render(self):
        return format_html('<div class="form-row">{0}</div>',
            format_html_join('', '<div class="field-box">'
                '<div class="container-thumbnail"><i class="icon-{1}"></i><div class="label">{0}</div></div>'
                '</div>', ((force_text(w), CASCADE_BREAKPOINTS_DICT[w.choice_value][1]) for w in self)
            ))


class BootstrapContainerPlugin(BootstrapPluginBase):
    name = _("Container")
    default_css_class = 'container'
    require_parent = False
    WIDGET_CHOICES_WIDEST = (
        ('lg', _("Large (>{0}px)".format(*CASCADE_BREAKPOINTS_DICT['lg']))),
        ('md', _("Medium (>{0}px)".format(*CASCADE_BREAKPOINTS_DICT['md']))),
        ('sm', _("Small (>{0}px)".format(*CASCADE_BREAKPOINTS_DICT['sm']))),
        ('xs', _("Tiny (<{0}px)".format(*CASCADE_BREAKPOINTS_DICT['sm']))),
    )
    WIDGET_CHOICES_NARROW = (
        ('lg', _("Large (>{0}px)".format(*CASCADE_BREAKPOINTS_DICT['lg']))),
        ('md', _("Medium (<{0}px)".format(*CASCADE_BREAKPOINTS_DICT['lg']))),
        ('sm', _("Small (<{0}px)".format(*CASCADE_BREAKPOINTS_DICT['md']))),
        ('xs', _("Tiny (<{0}px)".format(*CASCADE_BREAKPOINTS_DICT['sm']))),
    )
    glossary_fields = (
        PartialFormField('widest',
            widgets.RadioSelect(choices=WIDGET_CHOICES_WIDEST, renderer=ContainerRadioFieldRenderer),
            label=_('Widest Display'), initial='lg',
            help_text=_("Widest supported display for Bootstrap's grid system.")
        ),
        PartialFormField('narrowest',
            widgets.RadioSelect(choices=WIDGET_CHOICES_NARROW, renderer=ContainerRadioFieldRenderer),
            label=_('Narrowest Display'), initial='xs',
            help_text=_("Narrowest supported display for Bootstrap's grid system.")
        ),
    )
    glossary_variables = ['container_max_widths']

    class Media:
        css = {'all': ('//netdna.bootstrapcdn.com/font-awesome/3.2.1/css/font-awesome.min.css',)}
        js = ['cascade/js/admin/containerplugin.js']

    @classmethod
    def get_identifier(cls, obj):
        container_max_widths = obj.glossary.get('container_max_widths')
        if container_max_widths:
            values = container_max_widths.values()
            return _("ranging from {0} through {1} pixels").format(min(values), max(values))
        return six.u('')

    def save_model(self, request, obj, form, change):
        widest = CASCADE_BREAKPOINTS_LIST.index(obj.glossary['widest'])
        narrowest = CASCADE_BREAKPOINTS_LIST.index(obj.glossary['narrowest'])
        breakpoints = [bp for i, bp in enumerate(CASCADE_BREAKPOINTS_LIST) if i <= widest and i >= narrowest]
        obj.glossary.update(breakpoints=breakpoints)
        super(BootstrapContainerPlugin, self).save_model(request, obj, form, change)
        obj.sanitize_children()

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = super(BootstrapContainerPlugin, cls).sanitize_model(obj)
        complete_glossary = obj.get_complete_glossary()
        obj.glossary['container_max_widths'] = {}
        for bp in complete_glossary['breakpoints']:
            try:
                obj.glossary['container_max_widths'][bp] = complete_glossary['container_max_widths'][bp]
            except KeyError:
                obj.glossary['container_max_widths'][bp] = CASCADE_BREAKPOINTS_DICT[bp][4]
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
    parent_classes = ['BootstrapContainerPlugin', 'BootstrapColumnPlugin']
    form = BootstrapRowForm
    fields = ('num_children', 'glossary',)
    glossary_fields = (
        PartialFormField('inline_styles',
            MultipleCascadingSizeWidget(['min-height'], required=False),
            label=_('Inline Styles'),
            help_text=_('Minimum height for this row.')
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        num_cols = obj.get_children().count()
        return ungettext_lazy('with {0} column', 'with {0} columns', num_cols).format(num_cols)

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super(BootstrapRowPlugin, self).save_model(request, obj, form, change)
        child_glossary = {'xs-column-width': 'col-xs-{0}'.format(12 // wanted_children)}
        self.extend_children(obj, wanted_children, BootstrapColumnPlugin, child_glossary=child_glossary)

plugin_pool.register_plugin(BootstrapRowPlugin)


class BootstrapColumnPlugin(BootstrapPluginBase):
    name = _("Column")
    parent_classes = ['BootstrapRowPlugin']
    generic_child_classes = CMS_CASCADE_LEAF_PLUGINS
    default_css_attributes = list(itertools.chain(*(('{0}-column-width'.format(s), '{0}-responsive-utils'.format(s),) for s in CASCADE_BREAKPOINTS_LIST)))
    glossary_variables = ['container_max_widths']

    def get_form(self, request, obj=None, **kwargs):
        self.glossary_fields = []
        parent_obj, parent_plugin = self.parent.get_plugin_instance()
        if isinstance(parent_plugin, BootstrapPluginBase):
            complete_glossary = parent_obj.get_complete_glossary()
            for bp in complete_glossary['breakpoints']:
                desc = list(CASCADE_BREAKPOINTS_DICT[bp])
                desc[2] = force_text(desc[2])
                if bp == complete_glossary['breakpoints'][0]:
                    # first element
                    choices = tuple(('col-{0}-{1}'.format(bp, i),
                        ungettext_lazy('{0} unit', '{0} units', i).format(i)) for i in range(1, 13))
                    label = _("Default column width")
                    if bp == 'xs':
                        help_text = _("Number of column units for devices, narrower than {0} pixels, such as {2}.".format(*desc))
                    else:
                        help_text = _("Number of column units for devices wider than {0} pixels, such as {2}.".format(*desc))
                    self.glossary_fields.append(PartialFormField('{0}-column-width'.format(bp),
                        widgets.Select(choices=choices),
                        initial='col-{0}-12'.format(bp), label=label, help_text=help_text))
                else:
                    choices = (('', _('Inherit from above')),) + tuple(('col-{0}-{1}'.format(bp, i),
                        ungettext_lazy('{0} unit', '{0} units', i).format(i)) for i in range(1, 13))
                    label = _("Column width for {2}".format(*desc))
                    help_text = _("Override column units for devices wider than {0} pixels, such as {2}.".format(*desc))
                    self.glossary_fields.append(PartialFormField('{0}-column-width'.format(bp),
                        widgets.Select(choices=choices),
                        initial='', label=label, help_text=help_text))
                if bp != 'xs':
                    choices = (('', _('No offset')),) + tuple(('col-{0}-offset-{1}'.format(bp, i),
                        ungettext_lazy('{0} unit', '{0} units', i).format(i)) for i in range(1, 12))
                    label = _("Offset for {2}".format(*desc))
                    help_text = _("Number of offset units for devices wider than {0} pixels, such as {2}.".format(*desc))
                    self.glossary_fields.append(PartialFormField('{0}-column-offset'.format(bp),
                        widgets.Select(choices=choices), label=label, help_text=help_text))
                self.glossary_fields.append(PartialFormField('{0}-responsive-utils'.format(bp),
                    widgets.CheckboxSelectMultiple(choices=(('visible-{0}'.format(bp), _("Visible")),
                                                            ('hidden-{0}'.format(bp), _("Hidden")),)),
                    label=_("Responsive utilities for {2}").format(*desc)
                ))
        return super(BootstrapColumnPlugin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        super(BootstrapColumnPlugin, self).save_model(request, obj, form, change)
        obj.sanitize_children()

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = super(BootstrapColumnPlugin, cls).sanitize_model(obj)
        parent_glossary = obj.get_parent().get_complete_glossary()
        column_units = 12
        obj.glossary['container_max_widths'] = {}
        for bp in CASCADE_BREAKPOINTS_LIST:
            width_key = '{0}-column-width'.format(bp)
            offset_key = '{0}-column-offset'.format(bp)
            if bp in parent_glossary['breakpoints']:
                # if miss-set, reduce column width for larger displays
                width_val = obj.glossary.get(width_key, '').lstrip('col-{0}-'.format(bp))
                if width_val.isdigit():
                    if int(width_val) > column_units:
                        obj.glossary[width_key] = 'col-{0}-{1}'.format(bp, column_units)
                        sanitized = True
                    column_units = int(width_val)
            else:
                # remove obsolete entries from glossary
                if width_key in obj.glossary:
                    del obj.glossary[width_key]
                    sanitized = True
                if offset_key in obj.glossary:
                    del obj.glossary[offset_key]
                    sanitized = True
            new_width = parent_glossary['container_max_widths'][bp] * column_units / 12
            if new_width != obj.glossary['container_max_widths'].get(bp):
                obj.glossary['container_max_widths'][bp] = new_width
                sanitized = True
        return sanitized

    @classmethod
    def get_identifier(cls, obj):
        try:
            width = int(string.replace(obj.glossary['xs-column-width'], 'col-xs-', ''))
            return ungettext_lazy('default width: {0} unit', 'default width: {0} units', width).format(width)
        except (TypeError, KeyError, ValueError):
            return _('unknown width')

plugin_pool.register_plugin(BootstrapColumnPlugin)
