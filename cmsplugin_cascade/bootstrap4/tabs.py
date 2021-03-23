from django.forms import widgets
from django.forms.fields import BooleanField, CharField
from django.utils.translation import ngettext_lazy, gettext_lazy as _
from django.utils.text import Truncator
from django.utils.safestring import mark_safe
from django.forms.fields import IntegerField

from entangled.forms import EntangledModelFormMixin
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.plugin_base import TransparentWrapper, TransparentContainer
from cmsplugin_cascade.widgets import NumberInputWidget
from .plugin_base import BootstrapPluginBase


class TabSetFormMixin(ManageChildrenFormMixin, EntangledModelFormMixin):
    num_children = IntegerField(
        min_value=1,
        initial=1,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em !important;'}),
        label=_("Tabs"),
        help_text=_("Number of tabs to start with."),
    )

    justified = BooleanField(
        label=_("Justified tabs"),
        required=False,
    )

    class Meta:
        untangled_fields = ['num_children']
        entangled_fields = {'glossary': ['justified']}


class BootstrapTabSetPlugin(TransparentWrapper, BootstrapPluginBase):
    name = _("Tab Set")
    parent_classes = ['BootstrapColumnPlugin']
    direct_child_classes = ['BootstrapTabPanePlugin']
    require_parent = True
    allow_children = True
    form = TabSetFormMixin
    render_template = 'cascade/bootstrap4/{}tabset.html'
    default_css_class = 'nav-tabs'

    @classmethod
    def get_identifier(cls, instance):
        num_cols = instance.get_num_children()
        content = ngettext_lazy('with {} tab', 'with {} tabs', num_cols).format(num_cols)
        return mark_safe(content)

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super().save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, BootstrapTabPanePlugin)

plugin_pool.register_plugin(BootstrapTabSetPlugin)


class TabPaneFormMixin(EntangledModelFormMixin):
    tab_title = CharField(
        label=_("Tab Title"),
        widget=widgets.TextInput(attrs={'size': 80}),
    )

    class Meta:
        entangled_fields = {'glossary': ['tab_title']}


class BootstrapTabPanePlugin(TransparentContainer, BootstrapPluginBase):
    name = _("Tab Pane")
    direct_parent_classes = parent_classes = ['BootstrapTabSetPlugin']
    require_parent = True
    allow_children = True
    alien_child_classes = True
    form = TabPaneFormMixin

    @classmethod
    def get_identifier(cls, obj):
        content = obj.glossary.get('tab_title', '')
        if content:
            content = Truncator(content).words(3, truncate=' ...')
        return mark_safe(content)

plugin_pool.register_plugin(BootstrapTabPanePlugin)
