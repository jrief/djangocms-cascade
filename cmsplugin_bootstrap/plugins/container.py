# -*- coding: utf-8 -*-
from django.forms import widgets
from django.forms.widgets import RadioFieldRenderer
from django.utils.html import format_html_join
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_bootstrap.plugin_base import BootstrapPluginBase, CSS_VERTICAL_SPACING
from cmsplugin_bootstrap.widgets import MultipleCheckboxesWidget


class ContainerRadioFieldRenderer(RadioFieldRenderer):
    map_icon = { 'xs': 'mobile-phone', 'sm': 'tablet', 'md': 'laptop', 'lg': 'desktop' }

    def render(self):
        return format_html_join('\n',
            '<div class="col-sm-3 text-center">\n<div class="thumbnail">'
            '<i class="icon-{1}" style="font-size:50pt;"></i><h4>{0}</h4></div>\n'
            '</div>', [(force_text(w), self.map_icon[w.choice_value]) for w in self]
        )


class BootstrapContainerPlugin(BootstrapPluginBase):
    name = _("Container")
    child_classes = ['BootstrapRowPlugin']
    css_class_choices = (('container', 'container'),)
    CONTEXT_WIDGET_CHOICES = (
        ('xs', _('Tiny (<768px)')), ('sm', _('Small (>768px)')),
        ('md', _('Medium (>992px)')), ('lg', _('Large (>1200px)')),
    )
    change_form_template = 'cms/admin/change_form.html'
    context_widgets = [{
        'key': 'breakpoint',
        'label': _('Breakpoint'),
        'help_text': _('Narrowest Display Breakpoint'),
        'widget': widgets.RadioSelect(choices=CONTEXT_WIDGET_CHOICES, renderer=ContainerRadioFieldRenderer),
        'initial': 'xs',
    }, {
        'key': 'min-height',
        'label': _('Min. height'),
        'help_text': _('Minimum height for container'),
        'widget': widgets.TextInput({ 'placeholder': 'minimum height' }),
    }, {
        'key': 'tagged',
        'label': _('Tags'),
        'help_text': _('Tag choices'),
        'widget': MultipleCheckboxesWidget(choices=(('relative', 'relative'), ('static', 'static'), ('fixed', 'fixed'),)),
    }]

    @classmethod
    def get_identifier(cls, model):
        try:
            texts = [d for c, d in cls.CONTEXT_WIDGET_CHOICES if c == model.extra_context.get('breakpoint')]
            return _('Narrowest grid: {0}').format(texts[0].lower())
        except IndexError:
            return u''

    def save_model(self, request, obj, form, change):
        return super(BootstrapContainerPlugin, self).save_model(request, obj, form, change)

plugin_pool.register_plugin(BootstrapContainerPlugin)


class BootstrapRowPlugin(BootstrapPluginBase):
    name = _("Row")
    render_template = "cms/plugins/bootstrap/row.html"
    parent_classes = ['BootstrapContainerPlugin']
    require_parent = True
    child_classes = ['BootstrapColumnPlugin']
    CONTEXT_WIDGET_CHOICES = ((cs, _('{0} columns').format(cs)) for cs in range(1, 13))
    context_widgets = [{
        'key': 'columns',
        'label': _('ColumnsBreakpoint'),
        'help_text': _('Maximum number of column for this row'),
        'widget': widgets.Select(choices=CONTEXT_WIDGET_CHOICES),
    }]

    def save_model(self, request, obj, form, change):
        # on row creation, add columns automatically
        return super(BootstrapRowPlugin, self).save_model(request, obj, form, change)

plugin_pool.register_plugin(BootstrapRowPlugin)


class BootstrapColumnPlugin(BootstrapPluginBase):
    name = _("Column")
    render_template = "cms/plugins/bootstrap/column.html"
    parent_classes = ['BootstrapRowPlugin']
    require_parent = True
    css_class_choices = tuple((i, '{0} units'.format(i)) for i in range(1, 13))
    #extra_classes_widget = MultipleRadioButtonsWidget((
    #    ('offset', (('', 'no offset'),) + tuple(2 * ('offset%s' % o,) for o in range(1, 12))),
    #))
    child_classes = ['TextPlugin', 'CarouselPlugin']

    @classmethod
    def get_identifier(cls, model):
        try:
            return [d for c, d in cls.css_class_choices if str(c) == model.class_name][0]
        except IndexError:
            return u''

plugin_pool.register_plugin(BootstrapColumnPlugin)


class BootstrapDivPlugin(BootstrapPluginBase):
    name = _("Simple div container")
    parent_classes = ['BootstrapColumnPlugin']
    require_parent = True
    tag_type = 'div'
    css_class_choices = (('', '---'), ('hero-unit', 'hero-unit'))

plugin_pool.register_plugin(BootstrapDivPlugin)


class HorizontalRulePlugin(BootstrapPluginBase):
    name = _("Horizontal Rule")
    require_parent = False
    allow_children = False
    tag_type = 'hr'
    render_template = 'cms/plugins/bootstrap/single.html'

plugin_pool.register_plugin(HorizontalRulePlugin)
