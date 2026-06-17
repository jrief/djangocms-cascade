from django.forms.fields import IntegerField
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from cms.plugin_pool import plugin_pool
from cms.models.pagemodel import Page
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.bootstrap5.hyperlink import PageChoiceField
from cmsplugin_cascade.models import CascadeElement

from formset.forms import ModelForm
from formset.fieldsmapping import get_related_object


class SecondaryMenuForm(ModelForm):
    cms_page = PageChoiceField(
        label=_("CMS Page"),
        queryset=Page.objects.filter(reverse_id__isnull=False),
        help_text = _("Select a CMS page with a given unique Id (in advanced settings)."),
    )
    offset = IntegerField(
        label=_("Offset"),
        initial=0,
        min_value=0,
        help_text=_("Starting from which child menu."),
    )
    limit = IntegerField(
        label=_("Limit"),
        initial=100,
        min_value=1,
        help_text=_("Number of child menus."),
    )

    class Meta:
        model = CascadeElement
        exclude = ['shared_glossary']
        fields_map = {'glossary': ['cms_page', 'offset', 'limit']}


class BootstrapSecondaryMenuPlugin(BootstrapPluginBase):
    """
    Use this plugin to display a secondary menu in arbitrary locations.
    This renders links onto  all CMS pages, which are children of the selected Page Id.
    """
    name = _("Secondary Menu")
    default_css_class = 'list-group'
    require_parent = True
    parent_classes = ['BootstrapContainerPlugin', 'BootstrapColumnPlugin']
    form = SecondaryMenuForm
    render_template = 'cascade/bootstrap5/secmenu-list-group.html'

    @classmethod
    def get_identifier(cls, instance):
        cms_page = get_related_object(instance.glossary, 'cms_page')
        return format_html('<code>{}</code>', cms_page.reverse_id)

    def render(self, context, instance, placeholder):
        context = self.super(BootstrapSecondaryMenuPlugin, self).render(context, instance, placeholder)
        cms_page = get_related_object(instance.glossary, 'cms_page')
        context.update({
            'root_id': cms_page.reverse_id,
            'offset': instance.glossary.get('offset', 0),
            'limit': instance.glossary.get('limit', 100),
        })
        return context


plugin_pool.register_plugin(BootstrapSecondaryMenuPlugin)
