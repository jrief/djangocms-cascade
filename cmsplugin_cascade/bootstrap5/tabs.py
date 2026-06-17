from django.forms import widgets
from django.forms.fields import BooleanField, CharField
from django.utils.translation import gettext_lazy as _, gettext, ngettext
from django.utils.text import Truncator
from django.utils.safestring import mark_safe
from django.forms.fields import IntegerField

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase, logger
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.mixins import ManageChildrenMixin
from cmsplugin_cascade.models import CascadeElement
from cmsplugin_cascade.widgets import NumberInputWidget

from formset.forms import ModelForm


class TabSetForm(ManageChildrenFormMixin, ModelForm):
    num_children = IntegerField(
        min_value=1,
        initial=1,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em !important;'}),
        label=_("Number of Tabs"),
        help_text=_("Number can be adjusted at any time."),
    )
    justified = BooleanField(
        label=_("Justified tabs"),
        required=False,
    )

    class Meta:
        model = CascadeElement
        exclude = ['shared_glossary']
        fields_map = {'glossary': ['justified']}


class BootstrapTabSetPlugin(ManageChildrenMixin, BootstrapPluginBase):
    name = _("Tab Set")
    require_parent = True
    parent_classes = ['BootstrapContainerPlugin', 'BootstrapColumnPlugin']
    # child_classes = ['BootstrapTabPanePlugin']
    form = TabSetForm
    render_template = 'cascade/bootstrap5/tabset.html'
    default_css_class = 'nav-tabs'

    @classmethod
    def get_identifier(cls, instance):
        num_cols = instance.get_num_children()
        content = ngettext('with {} tab', 'with {} tabs', num_cols).format(num_cols)
        return mark_safe(content)

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super().get_css_classes(obj)
        if obj.glossary.get('justified'):
            css_classes.append('nav-fill')
        return css_classes

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super().save_model(request, obj, form, change)
        child_glossary = {'tab_title': gettext("Extra Tab")}
        self.extend_children(obj, wanted_children, BootstrapTabPanePlugin, child_glossary=child_glossary)

plugin_pool.register_plugin(BootstrapTabSetPlugin)


class TabPaneForm(ModelForm):
    tab_title = CharField(
        label=_("Tab Title"),
        widget=widgets.TextInput(attrs={'size': 80}),
    )

    class Meta:
        model = CascadeElement
        exclude = ['shared_glossary']
        fields_map = {'glossary': ['tab_title']}


class BootstrapTabPanePlugin(BootstrapPluginBase):
    name = _("Tab Pane")
    parent_classes = ['BootstrapTabSetPlugin']
    cache_child_classes = False
    require_parent = True
    form = TabPaneForm

    @classmethod
    def get_identifier(cls, obj):
        content = obj.glossary.get('tab_title', '')
        if content:
            content = Truncator(content).words(3, truncate=' ...')
        return mark_safe(content)

    @classmethod
    def get_child_classes(cls, slot, page=None, instance=None, only_uncached=False):
        child_classes = super().get_child_classes(slot, page, instance, only_uncached)
        if isinstance(instance.parent, BootstrapTabSetPlugin.model):
            if instance.parent.parent:
                _, plugin_class = instance.parent.parent.get_plugin_instance()
                child_classes.extend(plugin_class.get_child_classes(slot, page, instance.parent, only_uncached))
        else:
            logger.error(f"Could not find parent of type {BootstrapTabPanePlugin.model} for instance {instance}")
        return child_classes


plugin_pool.register_plugin(BootstrapTabPanePlugin)
