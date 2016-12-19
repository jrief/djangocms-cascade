# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import widgets
from django.forms.models import ModelForm
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.utils.text import Truncator
from django.utils.html import format_html
from django.forms.fields import IntegerField
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import TransparentWrapper, TransparentContainer
from cmsplugin_cascade.widgets import NumberInputWidget
from .plugin_base import BootstrapPluginBase


class TabForm(ManageChildrenFormMixin, ModelForm):
    num_children = IntegerField(min_value=1, initial=1,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em !important;'}),
        label=_("Tabs"),
        help_text=_("Number of tabs."))


class BootstrapTabSetPlugin(TransparentWrapper, BootstrapPluginBase):
    name = _("Tab Set")
    form = TabForm
    parent_classes = ('BootstrapColumnPlugin',)
    direct_child_classes = ('BootstrapTabPanePlugin',)
    require_parent = True
    allow_children = True
    render_template = 'cascade/bootstrap3/{}/tabset.html'

    justified = GlossaryField(
        widgets.CheckboxInput(),
        label=_("Justified tabs")
    )

    @classmethod
    def get_identifier(cls, instance):
        identifier = super(BootstrapTabSetPlugin, cls).get_identifier(instance)
        num_cols = instance.get_children().count()
        content = ungettext_lazy('with {} tab', 'with {} tabs', num_cols).format(num_cols)
        return format_html('{0}{1}', identifier, content)

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super(BootstrapTabSetPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, BootstrapTabPanePlugin)

plugin_pool.register_plugin(BootstrapTabSetPlugin)


class BootstrapTabPanePlugin(TransparentContainer, BootstrapPluginBase):
    name = _("Tab Pane")
    direct_parent_classes = parent_classes = ('BootstrapTabSetPlugin',)
    require_parent = True
    allow_children = True
    alien_child_classes = True

    tab_title = GlossaryField(
        widgets.TextInput(attrs={'size': 80}),
        label=_("Tab Title")
    )

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapTabPanePlugin, cls).get_identifier(obj)
        content = obj.glossary.get('tab_title', '')
        if content:
            content = Truncator(content).words(3, truncate=' ...')
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(BootstrapTabPanePlugin)
