from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.forms import widgets
from django.forms.fields import BooleanField, CharField, ChoiceField 
from cmsplugin_cascade.fields import SizeField
from .plugin_base import BootstrapPluginBase
from cmsplugin_cascade.bootstrap4.jumbotron import ImageBackgroundMixin
from cmsplugin_cascade.bootstrap4.container import ContainerFormMixin, ContainerGridMixin
from cmsplugin_cascade.image import ImageFormMixin, ImagePropertyMixin
from cmsplugin_cascade.bootstrap4.container import get_widget_choices, ContainerBreakpointsWidget
from cmsplugin_cascade.bootstrap4.image import get_image_tags
from .grid import Breakpoint
from cmsplugin_cascade.link.config import LinkPluginBase
from cms.plugin_pool import plugin_pool
from entangled.forms import EntangledModelFormMixin
from django.core.exceptions import ValidationError

import logging
logger = logging.getLogger('cascade')


class BootstrapNavbarFormMixin(EntangledModelFormMixin):
    OPTION_NAV_COLLAPSE = [(c, c) for c in [ "inherit", "navbar-expand","navbar-expand-sm", "navbar-expand-md","navbar-expand-lg", "navbar-expand-xl"] ]
    OPTION_NAV_COLOR = [(c, c) for c in [ "inherit", "navbar-light", "navbar-dark"]]
    OPTION_NAV_BG_COLOR = [ "inherit", "bg-primary", "bg-secondary","bg-success", "bg-danger", "bg-warning", "bg-info" ,"bg-light", "bg-dark" , "bg-white", "bg-transparent"] 
    OPTION_NAV_BG_GRADIENT = [ "bg-gradient-primary", "bg-gradient-secondary", "bg-gradient-success", "bg-gradient-danger", "bg-gradient-warning", "bg-gradient-info", "bg-gradient-light", "bg-gradient-dark"]
    OPTION_NAV_BG_MIX = OPTION_NAV_BG_COLOR + OPTION_NAV_BG_GRADIENT
    OPTION_NAV_PLACEMENTS=["inherit", "fixed-top" , "fixed-bottom" , "sticky-top"]

    navbar_collapse = ChoiceField(
        label=_('Navbar collapse'),
        choices=OPTION_NAV_COLLAPSE,
        help_text=_("Adjust interval for the navbar_collapse.")
    )

    navbar_color = ChoiceField(
        label=_('Navbar text color'),
        choices=OPTION_NAV_COLOR,
        help_text=_("Adjust the navbar color.")
    )

    navbar_bg_color = ChoiceField(
        label=_('Navbar bg color'),
        choices=[(c, c) for c in OPTION_NAV_BG_MIX ],
        help_text=_("Adjust interval for the  navbar background color."),
    )

    navbar_placement = ChoiceField(
        label=_('navbar-place'),
        choices=[(c, c) for c in OPTION_NAV_PLACEMENTS],
        help_text=_("Adjust position ('fixed-top or fixed-button need to be set in Jumbotron if it is a plugin parent.')")
    )

    class Meta:
        entangled_fields = {'glossary':['navbar_collapse', 'navbar_color', 'navbar_bg_color', 'navbar_placement']}

    def validate_optional_field(self, name):
        field = self.fields[name]
        value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
        if value in field.empty_values:
            self.add_error(name, ValidationError(field.error_messages['required'], code='required'))
        else:
            return value

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


@plugin_pool.register_plugin
class BootstrapNavbarPlugin(BootstrapPluginBase):
    name = _("Navbar")
    parent_classes = None
    require_parent = False
    model_mixins = (ContainerGridMixin,)
    default_css_class = 'navbar'
    default_css_attributes = ('options')
    alien_child_classes = True
    render_template = 'cascade/bootstrap4/navbar.html'
    ring_plugin = 'BootstrapNavbarPlugin'
    fixed_top_and_toolbar = None
    
    class Media:
        js = ['cascade/js/admin/navbarplugin.js']
 
    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = BootstrapNavbarFormMixin
        if hasattr(obj, 'glossary'):
            if obj.glossary.get('navbar_placement') == 'fixed-top':
                obj.fixed_top_and_toolbar=True
        return super().get_form(request, obj, **kwargs)

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = False
        if 'Position' in obj.get_parent_glossary():
            obj.glossary['position_jumbotron'] = obj.get_parent_glossary()['Position']
        if hasattr(obj,'fixed_top_and_toolbar'):
            navbar_placement = obj.glossary.get('navbar_placement')
            del obj.fixed_top_and_toolbar
        super().sanitize_model(obj)
        return sanitized
 
    
    @classmethod
    def get_css_classes(cls, obj, ):
        css_classes = cls.super(BootstrapNavbarPlugin, cls).get_css_classes(obj)
        navbar_collapse = obj.glossary.get('navbar_collapse', '')
        navbar_color = obj.glossary.get('navbar_color', '')
        navbar_bg_color = obj.glossary.get('navbar_bg_color', '')
        navbar_placement = obj.glossary.get('navbar_placement', '')
        if navbar_collapse != 'inherit':
            css_classes.append(navbar_collapse)
        if navbar_color != 'inherit':
            css_classes.append(navbar_color)
        if navbar_bg_color != 'inherit':
            css_classes.append(navbar_bg_color)
        if navbar_placement != 'inherit':
            css_classes.append(navbar_placement)
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super().get_identifier(obj)
        css_classes_without_default = obj.css_classes.replace( cls.default_css_class ,'',1)
        return format_html('<div style="font-size: smaller; white-space: pre-wrap;" >{0}{1}</div>',
          identifier, css_classes_without_default)


 
@plugin_pool.register_plugin
class BootstrapNavBrandPlugin(LinkPluginBase):
    name = _("Nav brand")
    parent_classes = ['BootstrapNavbarPlugin']
    render_template = 'cascade/bootstrap4/navbar_brand.html'
    raw_id_fields = LinkPluginBase.raw_id_fields + ['image_file']
    default_css_class = ''
    require_parent = False
    allow_children = True
    alien_child_classes = True

    @classmethod
    def get_child_css_classes(cls, obj):
        child_css_classes = cls.super(BootstrapNavBrandPlugin, cls).get_child_css_classes(obj)
        child_css_classes = obj.glossary.get('child_css_class')
        if child_css_classes:
            child_css_classes.append(css_class)
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapNavBrandPlugin, cls).get_identifier(obj)
        css_classes_without_default = obj.css_classes.replace( cls.default_css_class,'',1)
        return format_html('<div style="font-size: smaller; white-space: pre-wrap;" >{0}{1}</div>',
        identifier, css_classes_without_default)


class BootstrapNavBrandThumbImageFormMixin(EntangledModelFormMixin):
    image_width_fixed = SizeField(
        label=_("Fixed Image Width"),
        allowed_units=['px'],
        required = False,
        help_text=_("Set a fixed image width in pixels.")
    )

    class Meta:
        entangled_fields = {'glossary': ['image_width_fixed']}

class BootstrapNavBrandImageFormMixin(ImageFormMixin, BootstrapNavBrandThumbImageFormMixin):
    pass


@plugin_pool.register_plugin
class BootstrapNavBrandImagePlugin(BootstrapPluginBase):
    name = _("Nav brand Image") 
    model_mixins = (ImagePropertyMixin,)
    parent_classes = ['BootstrapNavBrandPlugin', 'BootstrapListsPlugin'] 
    allow_children = True
    alien_child_classes = True
    html_tag_attributes = {'image_title': 'title', 'alt_tag': 'tag'}
    raw_id_fields = ['image_file']
    SIZE_CHOICES = ('auto', 'width/height', 'cover', 'contain')
    form = BootstrapNavBrandImageFormMixin
    raw_id_fields = ['image_file']
    render_template = 'cascade/bootstrap4/navbar_brand_image.html'
    default_css_class = 'nav-brand-logo-ts'

    def render(self, context, instance, placeholder, tags=None):
        try:
            tags = get_image_tags(instance)
        except Exception as exc:
            logger.warning("Unable generate image tags. Reason: {}".format(exc))
        tags = tags if tags else {}
        if 'extra_styles' in tags:
            extra_styles = tags.pop('extra_styles')
            inline_styles = instance.glossary.get('inline_styles', {})
            inline_styles.update(extra_styles)
            instance.glossary['inline_styles'] = inline_styles
        context.update(dict(instance=instance, placeholder=placeholder, **tags))
        return context

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapNavBrandImagePlugin, cls).get_css_classes(obj)
        css_class = obj.glossary.get('css_class')
        if css_class:
            css_classes.append(css_class)
        return css_classes

    @classmethod
    def get_child_css_classes(cls, obj):
        child_css_classes = cls.super(BootstrapNavBrandImagePlugin, cls).get_child_css_classes(obj)
        child_css_classes = obj.glossary.get('child_css_class')
        if child_css_classes:
            child_css_classes.append(css_class)
        return css_classes


@plugin_pool.register_plugin
class BootstrapNavCollapsePlugin(BootstrapPluginBase):
    name = _("Nav Collapse")
    parent_classes = ['BootstrapNavbarPlugin']
    if not settings.CMSPLUGIN_CASCADE['bootstrap4'].get('template_basedir'):
        render_template = 'cascade/bootstrap4/navbar_collapse.html'
    else:
        render_template = 'cascade/bootstrap4/ng_navbar_collapse.html'
    default_css_class = 'collapse navbar-collapse'
 
    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super( BootstrapNavCollapsePlugin, cls).get_css_classes(obj)
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapNavCollapsePlugin, cls).get_identifier(obj)
        css_classes_without_default = obj.css_classes.replace( cls.default_css_class,'',1)
        return format_html('<div style="font-size: smaller; white-space: pre-wrap;" >{0}{1}</div>',
        identifier, css_classes_without_default)

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = super().sanitize_model(obj)
        return sanitized

@plugin_pool.register_plugin
class BootstrapNavItemsMainMenuPlugin(BootstrapPluginBase):
    name = _("NavItems MainMenu ")
    parent_classes = ['BootstrapListsPlugin']
    require_parent = False
    allow_children = False
    alien_child_classes = True
    render_template = 'cascade/bootstrap4/navbar_nav_items_li_menu_main_links.html'

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapNavItemsMainMenuPlugin, cls).get_css_classes(obj)
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapNavItemsMainMenuPlugin, cls).get_identifier(obj)
        if hasattr(cls,'default_css_class'):
            css_classes_without_default = obj.css_classes.replace( cls.default_css_class,'',1)
        else:
            css_classes_without_default = obj.css_classes
        return format_html('<div style="font-size: smaller; white-space: pre-wrap;" >{0}{1}</div>',
        identifier, css_classes_without_default)


@plugin_pool.register_plugin
class BootstrapNavbarToogler(BootstrapPluginBase):
    name = _("Nav toogler")
    default_css_class = 'navbar-toggler'
    parent_classes = ['BootstrapNavbarPlugin',]
    if not settings.CMSPLUGIN_CASCADE['bootstrap4'].get('template_basedir'):
        render_template = 'cascade/bootstrap4/navbar_toogler.html'
    else:
        render_template = 'cascade/bootstrap4/ng_navbar_toogler.html'



@plugin_pool.register_plugin
class BootstrapNavbarLanguageChooser(BootstrapPluginBase):
    name = _("Nav Lang Chooser")
    default_css_class = 'nav-item dropdown'
    parent_classes = ['BootstrapListsPlugin']
    if not settings.CMSPLUGIN_CASCADE['bootstrap4'].get('template_basedir'):
        render_template = 'bootstrap4/includes/language-chooser.html'
    else:
        render_template = 'bootstrap4/includes/ng-language-chooser.html'
