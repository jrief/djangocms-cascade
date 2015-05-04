# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.forms import widgets
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.utils.text import Truncator
from django.utils.html import format_html
from django.forms.models import ModelForm
from django.forms.fields import IntegerField
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.widgets import NumberInputWidget
from .plugin_base import BootstrapPluginBase
from .settings import CASCADE_TEMPLATE_DIR


class PanelGroupForm(ManageChildrenFormMixin, ModelForm):
    num_children = IntegerField(min_value=1, initial=1,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em;'}),
        label=_("Panels"),
        help_text=_("Number of panels for this panel group."))


class PanelGroupPlugin(BootstrapPluginBase):
    name = _("Panel Group")
    form = PanelGroupForm
    default_css_class = 'panel-group'
    parent_classes = ('BootstrapColumnPlugin',)
    require_parent = True
    render_template = os.path.join(CASCADE_TEMPLATE_DIR, 'collapse.html')
    fields = ('num_children', 'glossary',)

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(PanelGroupPlugin, cls).get_identifier(obj)
        num_cols = obj.get_children().count()
        content = ungettext_lazy('with {0} panel', 'with {0} panels', num_cols).format(num_cols)
        return format_html('{0}{1}', identifier, content)

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super(PanelGroupPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, PanelPlugin)

plugin_pool.register_plugin(PanelGroupPlugin)


class PanelPlugin(BootstrapPluginBase):
    name = _("Panel")
    default_css_class = 'panel-body'
    parent_classes = ('PanelGroupPlugin',)
    require_parent = True
    alien_child_classes = True
    glossary_fields = (
        PartialFormField('panel_title',
            widgets.TextInput(attrs={'size': 150}),
            label=_("Panel Title")
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(PanelPlugin, cls).get_identifier(obj)
        content = obj.glossary.get('panel_title', '')
        if content:
            content = unicode(Truncator(content).words(3, truncate=' ...'))
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(PanelPlugin)
