# -*- coding: utf-8 -*-
from django.forms import widgets
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.utils.text import Truncator
from cms.plugin_pool import plugin_pool
from cmsplugin_bootstrap.plugin_base import BootstrapPluginBase, PartialFormField
from cmsplugin_bootstrap.widgets import NumberInputWidget


class PanelGroupPlugin(BootstrapPluginBase):
    name = _("Panel Group")
    default_css_class = 'panel-group'
    parent_classes = ['BootstrapColumnPlugin']
    require_parent = True
    render_template = 'cms/plugins/bootstrap/collapse.html'
    partial_fields = (
        PartialFormField('-num-children-',  # temporary field, not stored in the database
            NumberInputWidget(attrs={ 'style': 'width: 30px;' }),
            label=_('Number of Panels'), help_text=_('Number of panels for this panel group.')
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        num_cols = obj.get_children().count()
        return ungettext_lazy('with {0} panel', 'with {0} panels', num_cols).format(num_cols)

    def save_model(self, request, obj, form, change):
        wanted_children = int(obj.context['-num-children-'])
        super(PanelGroupPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, PanelPlugin)

plugin_pool.register_plugin(PanelGroupPlugin)


class PanelPlugin(BootstrapPluginBase):
    name = _("Panel")
    default_css_class = 'panel-body'
    parent_classes = ['PanelGroupPlugin']
    require_parent = True
    generic_child_classes = ['TextPlugin']
    partial_fields = (
        PartialFormField('panel_title',
            widgets.TextInput(attrs={ 'size': 150 }),
            label=_('Panel Title')
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        value = obj.context.get('panel_title')
        if value:
            return unicode(Truncator(value).words(3, truncate=' ...'))
        return u''

plugin_pool.register_plugin(PanelPlugin)
