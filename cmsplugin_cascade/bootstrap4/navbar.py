from django.db.models import Q
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _


from .plugin_base import BootstrapPluginBase
from cmsplugin_cascade.bootstrap4.jumbotron import ImageBackgroundMixin, JumbotronFormMixin
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade import app_settings
from cmsplugin_cascade.bootstrap4.container import ContainerFormMixin, ContainerGridMixin
from cmsplugin_cascade.bootstrap4.picture import get_picture_elements
from cmsplugin_cascade.image import ImageFormMixin, ImagePropertyMixin

from .grid import Breakpoint
from cmsplugin_cascade.link.config import LinkPluginBase, LinkElementMixin


import logging
logger = logging.getLogger('cascade')


class BootstrapNavbarFormMixin(JumbotronFormMixin):
    pass


@plugin_pool.register_plugin
class BootstrapNavbarPlugin(BootstrapPluginBase):
    name = _("Navbar")
    model_mixins = (ContainerGridMixin, ImagePropertyMixin, ImageBackgroundMixin)
    default_css_class = 'navbar'
    default_css_attributes = ('options',)
    require_parent = False
    parent_classes = None
    render_template = 'cascade/bootstrap4/navbar.html'
    #glossary_variables = ['container_max_widths', 'media_queries']
    raw_id_fields = ['image_file']
    ring_plugin = 'BootstrapNavbarPlugin'
    OPTION_NAV_COLLAPSE = [(c, c) for c in [ "inherit", "navbar-expand","navbar-expand-sm", "navbar-expand-md","navbar-expand-lg", "navbar-expand-xl"] ]
    OPTION_NAV_COLOR = [(c, c) for c in [ "navbar-light", "navbar-dark"]]
    OPTION_NAV_BG_COLOR = [ "bg-primary", "bg-secondary","bg-success", "bg-danger", "bg-warning", "bg-info" ,"bg-light", "bg-dark" , "bg-white", "bg-transparent"] 
    OPTION_NAV_BG_GRADIENT = [ "bg-gradient-primary", "bg-gradient-secondary", "bg-gradient-success", "bg-gradient-danger", "bg-gradient-warning", "bg-gradient-info", "bg-gradient-light", "bg-gradient-dark"]
    OPTION_NAV_BG_MIX = OPTION_NAV_BG_COLOR + OPTION_NAV_BG_GRADIENT
    OPTION_NAV_PLACEMENTS=["inherit", "fixed-top" , "fixed-bottom" , "sticky-top"]

    class Media:
        js = ['cascade/js/admin/navbarplugin.js']

    def get_form(self, request, obj=None, **kwargs):
        if self.get_parent_instance(request, obj) is None:
            # we only ask for breakpoints, if the Navjumbotron is the root of the placeholder
            kwargs['form'] = type('NavbarForm', (ContainerFormMixin, BootstrapNavbarFormMixin), {})
            kwargs['form'].declared_fields['image_file'].required=False
        else:
            kwargs['form'] = BootstrapNavbarFormMixin
            kwargs['form'].declared_fields['image_file'].required=False
        return super().get_form(request, obj, **kwargs)

    def render(self, context, instance, placeholder):
        # image shall be rendered in a responsive context using the ``<picture>`` element
        try:
            elements = get_picture_elements(instance)
        except Exception as exc:
            logger.warning("Unable generate picture elements. Reason: {}".format(exc))
        else:
            try:
                if instance.child_plugin_instances and instance.child_plugin_instances[0].plugin_type == 'BootstrapRowPlugin':
                    padding='padding: {0}px {0}px;'.format(int( app_settings.CMSPLUGIN_CASCADE['bootstrap4']['gutter']/2))
                    context.update({'add_gutter_if_child_is_BootstrapRowPlugin': padding,})
                context.update({
                    'elements': [e for e in elements if 'media' in e] if elements else [],
                    'CSS_PREFIXES': app_settings.CSS_PREFIXES,
                })
            except Exception as exc:
                logger.warning("Unable generate picture elements. Reason: {}".format(exc))        
        return self.super(BootstrapNavbarPlugin, self).render(context, instance, placeholder)

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = False
        # if the jumbotron is the root of the placeholder, we consider it as "fluid"
        obj.glossary['fluid'] = obj.parent is None
        super().sanitize_model(obj)
        grid_container = obj.get_bound_plugin().get_grid_instance()
        obj.glossary.setdefault('media_queries', {})
        for bp, bound in grid_container.bounds.items():
            obj.glossary['media_queries'].setdefault(bp.name, {})
            width = round(bound.max)
            if obj.glossary['media_queries'][bp.name].get('width') != width:
                obj.glossary['media_queries'][bp.name]['width'] = width
                sanitized = True
            if obj.glossary['media_queries'][bp.name].get('media') != bp.media_query:
                obj.glossary['media_queries'][bp.name]['media'] = bp.media_query
                sanitized = True
        return sanitized

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapNavbarPlugin, cls).get_css_classes(obj)
        if obj.glossary.get('fluid'):
            css_classes.append('jumbotron-fluid')
        else:
            css_classes.append('jumbotron')
        navbar_collapse = obj.glossary.get('navbar_collapse', '')
        navbar_color = obj.glossary.get('navbar_color', '')
        navbar_bg_color = obj.glossary.get('navbar_bg_color', '')
        navbar_placement = obj.glossary.get('placement', '')
        if navbar_collapse != 'inherit':
           css_classes.append(navbar_collapse)
        if navbar_color != 'inherit':
            css_classes.append(navbar_color)
        if navbar_bg_color != 'inherit':
            css_classes.append(navbar_bg_color)
        if navbar_placement  != 'inherit':
            css_classes.append(navbar_placement )
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super().get_identifier(obj)
        try:
            content = obj.image.name or obj.image.original_filename
        except AttributeError:
            content = _("Without background image")
        return format_html('{0}{1}', identifier, content)


@plugin_pool.register_plugin
class BootstrapNavBrandPlugin(BootstrapPluginBase, LinkPluginBase,):
    name = _("Nav brand")
    parent_classes = ['BootstrapNavbarPlugin'] 
    model_mixins = (LinkElementMixin,)
    render_template = 'cascade/bootstrap4/navbar_brand.html'
    raw_id_fields = LinkPluginBase.raw_id_fields + ['image_file']


@plugin_pool.register_plugin
class BootstrapNavBrandImagePlugin(BootstrapPluginBase):
    name = _("Nav brand Image") 
    model_mixins = (ImagePropertyMixin,)
    parent_classes = ['BootstrapNavBrandPlugin'] 
    allow_children = True
    alien_child_classes = True
    html_tag_attributes = {'image_title': 'title', 'alt_tag': 'tag'}
    raw_id_fields = ['image_file']
    SIZE_CHOICES = ('auto', 'width/height', 'cover', 'contain')
    form = ImageFormMixin
    raw_id_fields = ['image_file']
    render_template = 'cascade/bootstrap4/navbar_brand_image.html'

    def render(self, context, instance, placeholder):
        context = self.super(BootstrapNavBrandImagePlugin, self).render(context, instance, placeholder)
        try:
            parent_glossary = instance.parent.get_bound_plugin().glossary
            instance.glossary.update(responsive_heights=parent_glossary['container_max_heights'])
            elements = get_picture_elements(instance)
        except Exception as exc:
            logger.warning("Unable generate picture elements. Reason: {}".format(exc))
        else:
            context.update({
                'is_fluid': False,
                'elements': elements,
            })

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = super().sanitize_model(obj)
        resize_options = obj.get_parent_glossary().get('resize_options', [])
        if obj.glossary.get('resize_options') != resize_options:
            obj.glossary.update(resize_options=resize_options)
            sanitized = True
        parent = obj.parent
        
        while parent.plugin_type != 'BootstrapColumnPlugin':
            parent = parent.parent
            if parent is None:
                logger.warning("PicturePlugin(pk={}) has no ColumnPlugin as ancestor.".format(obj.pk))
                return
        grid_column = parent.get_bound_plugin().get_grid_instance()
        obj.glossary.setdefault('media_queries', {})
        for bp in Breakpoint:
            obj.glossary['media_queries'].setdefault(bp.name, {})
            width = round(grid_column.get_bound(bp).max)
            if obj.glossary['media_queries'][bp.name].get('width') != width:
                obj.glossary['media_queries'][bp.name]['width'] = width
                sanitized = True
            if obj.glossary['media_queries'][bp.name].get('media') != bp.media_query:
                obj.glossary['media_queries'][bp.name]['media'] = bp.media_query
                sanitized = True
            return sanitized


@plugin_pool.register_plugin
class BootstrapNavCollapsePlugin(BootstrapPluginBase):
    name = _("Nav Collapse")
    parent_classes = ['BootstrapNavbarPlugin'] 
    alien_child_classes = True
    render_template = 'cascade/bootstrap4/navbar_collapse.html'
    default_css_class = 'collapse navbar-collapse'

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(BootstrapNavCollapsePlugin, cls).get_css_classes(obj)
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapNavCollapsePlugin, cls).get_identifier(obj)
        css_classes_without_default = obj.css_classes.replace( cls.default_css_class , '' , 1)
        return format_html('<div style="font-size: smaller; white-space: pre-wrap;" >{0}{1}</div>',
        identifier, css_classes_without_default)


@plugin_pool.register_plugin
class  BootstrapNavListPlugin(BootstrapPluginBase):
    name = _("Nav list")
    parent_classes = [' BootstrapNavbarPlugin', 'BootstrapNavCollapsePlugin' ] 
    alien_child_classes = True
    render_template = 'cascade/bootstrap4/navbar_nav_list.html'
    default_css_class = 'navbar-nav'

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(BootstrapNavListPlugin, cls).get_css_classes(obj)
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapNavListPlugin, cls).get_identifier(obj)
        if hasattr(cls,'default_css_class'):
            css_classes_without_default = obj.css_classes.replace( cls.default_css_class , '' , 1)
        else:
            css_classes_without_default = obj.css_classes
        return format_html('<div style="font-size: smaller; white-space: pre-wrap;" >{0}{1}</div>',
        identifier, css_classes_without_default )


@plugin_pool.register_plugin
class BootstrapNavItemsMainMemuPlugin(BootstrapPluginBase):
    name = _("Nav items main menu")
    parent_classes = ['BootstrapNavListPlugin'] 
    alien_child_classes = True
    render_template = 'cascade/bootstrap4/navbar_nav_items_links.html'


@plugin_pool.register_plugin
class BootstrapNavItemsPlugin(BootstrapPluginBase):
    default_css_class = 'nav-item'
    name = _("Nav item")
    parent_classes = ['BootstrapNavListPlugin'] 
    alien_child_classes = True
    render_template = 'cascade/bootstrap4/navbar_nav_item.html'


@plugin_pool.register_plugin
class BootstrapNavbarNavLinkPlugin(BootstrapPluginBase):
    name = _("Nav Link")
    parent_classes = ['BootstrapNavItemsPlugin'] 
    alien_child_classes = True
    render_template = 'cascade/bootstrap4/navbar_nav_link.html'


@plugin_pool.register_plugin
class BootstrapNavbarToogler(BootstrapPluginBase):
    name = _("Nav toogler")
    default_css_class = ''
    parent_classes = [' BootstrapNavbarPlugin'] 
    render_template = 'cascade/bootstrap4/navbar_toogler.html'
