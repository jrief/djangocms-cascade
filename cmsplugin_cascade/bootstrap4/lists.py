from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from .plugin_base import BootstrapPluginBase
from django.forms.fields import ChoiceField
from cms.plugin_pool import plugin_pool
from entangled.forms import EntangledModelFormMixin

import logging
logger = logging.getLogger('cascade')

class  BootstrapListsMixin( EntangledModelFormMixin):
    list_options = ChoiceField(
        label=_("List Options"),
        choices=[
            ('inherit', _("inherit")),
            ('inline-item', _('ul(class="inline-item").li(class="list-inline-item")')),
            ('navbar-nav', _('ul(class="navbar-nav").li(class="nav-item")')),
        ],
        required=False,
    )
    class Meta:
        entangled_fields = {'glossary': ['list_options']}


@plugin_pool.register_plugin
class  BootstrapListsPlugin(BootstrapPluginBase):
    name = _("Lists")
    alien_plugins = True
    form = BootstrapListsMixin
    alien_child_classes = True
    render_template = 'cascade/bootstrap4/navbar_list.html'
    default_css_class = ''
    require_parent = False
    
    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapListsPlugin, cls).get_css_classes(obj)
        list_options = [obj.glossary.get('list_options')] if obj.glossary.get('list_options') else ''
        if list_options:
            for opts in list_options:
               css_classes.append(opts)
        return css_classes


    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapListsPlugin, cls).get_identifier(obj)
        if hasattr(cls,'default_css_class'):
            css_classes_without_default = obj.css_classes.replace( cls.default_css_class , '' , 1)
        else:
            css_classes_without_default = obj.css_classes
        return format_html('<div style="font-size: smaller; white-space: pre-wrap;" >{0}{1}</div>',
        identifier, css_classes_without_default )

    @classmethod
    def sanitize_model(cls, obj):
        list_child_css_classes = obj.glossary['child_css_classes'].split(' ') if 'child_css_classes' in obj.glossary else []
        list_options = 'list-inline-item' if obj.glossary.get('list_options') else ''
        list_options = 'nav-item' if obj.glossary.get('list_options') == 'navbar-nav' else list_options 
        if list_options:
             list_child_css_classes.append(list_options)
        obj.glossary['child_css_classes'] = ' '.join(list_child_css_classes)
        super().sanitize_model(obj)

