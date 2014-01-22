# -*- coding: utf-8 -*-
from django.forms import widgets
from django.forms.widgets import RadioFieldRenderer
from django.utils.html import format_html, format_html_join
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_bootstrap.plugin_base import BootstrapPluginBase
from cmsplugin_bootstrap.widgets import MultipleTextInputWidget, CSS_MARGIN_STYLES, CSS_VERTICAL_SPACING


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
        ('xs', _('Tiny (<768px)')), ('sm', _('Small (>768px)')),
        ('md', _('Medium (>992px)')), ('lg', _('Large (>1200px)')),
    )
    change_form_template = 'cms/admin/change_form.html'
    context_widgets = [{
        'key': 'breakpoint',
        'label': _('Display Breakpoint'),
        'help_text': _('Narrowest Display Grid'),
        'widget': widgets.RadioSelect(choices=CONTEXT_WIDGET_CHOICES, renderer=ContainerRadioFieldRenderer),
        'initial': 'xs',
    }, {
        'key': 'inline_styles',
        'label': _('Inline Styles'),
        'help_text': _('Margins and minimum height for container'),
        'widget': MultipleTextInputWidget(CSS_MARGIN_STYLES),
    }, {
        'key': 'tagged',
        'label': _('Tags'),
        'help_text': _('Tag choices'),
        'widget': widgets.CheckboxSelectMultiple(choices=(('relative', 'relative'), ('static', 'static'), ('fixed', 'fixed'),)),
    }]

    @classmethod
    def get_identifier(cls, model):
        try:
            texts = [d for c, d in cls.CONTEXT_WIDGET_CHOICES if c == model.extra_context.get('breakpoint')]
            return _('Narrowest grid: {0}').format(texts[0].lower())
        except IndexError:
            return u''

plugin_pool.register_plugin(BootstrapContainerPlugin)


class BootstrapRowPlugin(BootstrapPluginBase):
    name = _("Row")
    render_template = "cms/plugins/bootstrap/row.html"
    parent_classes = ['BootstrapContainerPlugin']
    require_parent = True
    child_classes = ['BootstrapColumnPlugin']
    COLUMN_WIDGET_CHOICES = ((cs, _('{0} columns').format(cs)) for cs in range(1, 13))
    CSS_CLASSES_CHOICES = (('a', 'a'), ('b', 'b'))
    context_widgets = [{
        'key': 'columns',
        'label': _('Number of Columns'),
        'help_text': _('Maximum number of columns for this row'),
        'widget': widgets.Select(choices=COLUMN_WIDGET_CHOICES),
    }, {
        'key': 'inline_styles',
        'label': _('Inline Styles'),
        'help_text': _('Minimum height for this row'),
        'widget': MultipleTextInputWidget(CSS_VERTICAL_SPACING),
    }]

    @classmethod
    def get_identifier(cls, model):
        return _('with {0} columns').format(model.extra_context.get('columns'))

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
    child_classes = ['TextPlugin', 'BootstrapRowPlugin', 'CarouselPlugin']

    @classmethod
    def get_identifier(cls, model):
        return u'99'
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
