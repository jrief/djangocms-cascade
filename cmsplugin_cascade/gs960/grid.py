# -*- coding: utf-8 -*-
from django.forms import widgets
from django.forms.models import ModelForm
from django.forms.fields import ChoiceField
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.widgets import MultipleCascadingSizeWidget
from . import settings


class GS960RowForm(ManageChildrenFormMixin, ModelForm):
    """
    Form class to add non-materialized field to count the number of children.
    """
    ROW_NUM_COLUMNS = (1, 2, 3, 4, 6, 12,)
    num_children = ChoiceField(choices=tuple((i, ungettext_lazy('{0} column', '{0} columns', i).format(i)) for i in ROW_NUM_COLUMNS),
        initial=3, label=_('Columns'),
        help_text=_('Number of columns to be created with this row.'))


class Container960BasePlugin(CascadePluginBase):
    module = '960.gs'
    form = GS960RowForm
    fields = ('num_children', 'glossary',)
    require_parent = False
    allow_children = True
    default_css_attributes = ('options',)

    def __init__(self, model=None, admin_site=None):
        glossary_fields = (
            PartialFormField('options',
                widgets.CheckboxSelectMultiple(choices=(('clearfix', _('Clearfix')),)),
                label=_('Options'),
            ),
        )
        super(Container960BasePlugin, self).__init__(model, admin_site, glossary_fields)

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super(Container960BasePlugin, self).save_model(request, obj, form, change)
        child_plugin = eval('Grid{0}Plugin'.format(self.CONTAINER_WIDTH))
        child_glossary = {'grid': 'grid_{0}'.format(self.CONTAINER_WIDTH // wanted_children)}
        self.extend_children(obj, wanted_children, child_plugin, child_glossary=child_glossary)


class Container12Plugin(Container960BasePlugin):
    name = _("Container 12")
    default_css_class = 'container_12'
    CONTAINER_WIDTH = 12
    CONTAINER_NUM_COLUMNS = (1, 2, 3, 4, 6, 12,)

plugin_pool.register_plugin(Container12Plugin)


class Container16Plugin(Container960BasePlugin):
    name = _("Container 16")
    default_css_class = 'container_16'
    CONTAINER_WIDTH = 16
    CONTAINER_NUM_COLUMNS = (1, 2, 3, 4, 8, 16,)

plugin_pool.register_plugin(Container16Plugin)


class Grid960BasePlugin(CascadePluginBase):
    module = '960.gs'
    name = _("Grid")
    require_parent = True
    allow_children = True
    alien_child_classes = True
    default_css_attributes = ('grid', 'prefix', 'suffix', 'options',)
    OPTION_CHOICES = (('alpha', _('Left aligned')), ('omega', _('Right aligned')),
                      ('clearfix', _('Clearfix')),)

    def __new__(cls, *args, **kwargs):
        cls.GRID_CHOICES = tuple(('grid_{0}'.format(i), _('{0} units'.format(i))) for i in range(1, cls.MAX_COLUMNS + 1))
        cls.PREFIX_CHOICES = (('', _('unused')),) + tuple(('prefix_{0}'.format(i), _('{0} units'.format(i))) for i in range(1, cls.MAX_COLUMNS))
        cls.SUFFIX_CHOICES = (('', _('unused')),) + tuple(('suffix_{0}'.format(i), _('{0} units'.format(i))) for i in range(1, cls.MAX_COLUMNS))
        return super(Grid960BasePlugin, cls).__new__(cls, *args, **kwargs)

    def __init__(self, model=None, admin_site=None):
        glossary_fields = (
            PartialFormField('grid',
                widgets.Select(choices=self.GRID_CHOICES),
                label=_('Column Grid'), initial='grid_4',
                help_text=_("Grid in column units.")
            ),
            PartialFormField('prefix',
                widgets.Select(choices=self.PREFIX_CHOICES),
                label=_('Prefix'),
            ),
            PartialFormField('suffix',
                widgets.Select(choices=self.SUFFIX_CHOICES),
                label=_('Suffix'),
            ),
            PartialFormField('options',
                widgets.CheckboxSelectMultiple(choices=self.OPTION_CHOICES),
                label=_('Options'),
            ),
            PartialFormField('inline_styles', MultipleCascadingSizeWidget(['min-height', 'margin-top', 'margin-bottom']),
                label=_('Inline Styles'), help_text=_('Minimum height for this column.')
            ),
        )
        super(Grid960BasePlugin, self).__init__(model, admin_site, glossary_fields=glossary_fields)

    @classmethod
    def get_identifier(cls, obj):
        try:
            texts = [d for c, d in cls.GRID_CHOICES if c == obj.glossary.get('grid')]
            return texts[0]
        except (TypeError, KeyError, ValueError):
            return ''


class Grid12Plugin(Grid960BasePlugin):
    parent_classes = ('Container12Plugin', 'Grid12Plugin',)
    MAX_COLUMNS = 12

plugin_pool.register_plugin(Grid12Plugin)


class Grid16Plugin(Grid960BasePlugin):
    parent_classes = ('Container16Plugin', 'Grid16Plugin',)
    MAX_COLUMNS = 16

plugin_pool.register_plugin(Grid16Plugin)
