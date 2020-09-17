from django.forms.fields import ChoiceField, IntegerField
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from entangled.forms import EntangledModelFormMixin
from cms.plugin_pool import plugin_pool
from cms.models.pagemodel import Page
from .plugin_base import BootstrapPluginBase


class SecondaryMenuFormMixin(EntangledModelFormMixin):
    page_id = ChoiceField(
        label=_("CMS Page Id"),
        help_text = _("Select a CMS page with a given unique Id (in advanced settings)."),
    )

    offset = IntegerField(
        label=_("Offset"),
        initial=0,
        help_text=_("Starting from which child menu."),
    )

    limit = IntegerField(
        label=_("Limit"),
        initial=100,
        help_text=_("Number of child menus."),
    )

    class Meta:
        entangled_fields = {'glossary': ['page_id', 'offset', 'limit']}

    def __init__(self, *args, **kwargs):
        choices = [(p.reverse_id, str(p)) for p in Page.objects.filter(reverse_id__isnull=False, publisher_is_draft=False)]
        self.base_fields['page_id'].choices = choices
        super().__init__(*args, **kwargs)


class BootstrapSecondaryMenuPlugin(BootstrapPluginBase):
    """
    Use this plugin to display a secondary menu in arbitrary locations.
    This renders links onto  all CMS pages, which are children of the selected Page Id.
    """
    name = _("Secondary Menu")
    default_css_class = 'list-group'
    require_parent = False
    parent_classes = None
    allow_children = False
    form = SecondaryMenuFormMixin
    render_template = 'cascade/bootstrap4/secmenu-list-group.html'

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(obj.glossary.get('page_id', ''))

    def render(self, context, instance, placeholder):
        context = self.super(BootstrapSecondaryMenuPlugin, self).render(context, instance, placeholder)
        context.update({
            'page_id': instance.glossary['page_id'],
            'offset': instance.glossary.get('offset', 0),
            'limit': instance.glossary.get('limit', 100),
        })
        return context

    @classmethod
    def sanitize_model(cls, instance):
        try:
            if int(instance.glossary['offset']) < 0 or int(instance.glossary['limit']) < 0:
                raise ValueError()
        except (KeyError, ValueError):
            instance.glossary['offset'] = 0
            instance.glossary['limit'] = 100

plugin_pool.register_plugin(BootstrapSecondaryMenuPlugin)
