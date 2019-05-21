# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
    from html.parser import HTMLParser  # py3
except ImportError:
    from HTMLParser import HTMLParser  # py2

from django.forms import widgets, ModelChoiceField
from django.utils.html import format_html
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.forms.models import ModelForm

from cms.plugin_pool import plugin_pool
from filer.models.imagemodels import Image

from cmsplugin_cascade import app_settings
from cmsplugin_cascade.fields import GlossaryField

from cmsplugin_cascade.bootstrap4.plugin_base import BootstrapPluginBase

from cmsplugin_cascade.image import ImageAnnotationMixin, ImagePropertyMixin, ImageFormMixin
from cmsplugin_cascade.bootstrap4.image import get_image_tags
from cmsplugin_cascade.bootstrap4.picture import BootstrapPicturePlugin, get_picture_elements
from cmsplugin_cascade.bootstrap4.container import ContainerBreakpointsWidget, ContainerGridMixin, get_widget_choices
from cmsplugin_cascade.widgets import MultipleCascadingSizeWidget, CascadingSizeWidget
from cmsplugin_cascade.bootstrap4.grid import Breakpoint

from cmsplugin_cascade.link.config import LinkPluginBase, LinkElementMixin, LinkForm
from . import grid

import logging
logger = logging.getLogger('cascade')


class NavbarPluginForm(ImageFormMixin, ModelForm):
    """
    Form class to validate the JumbotronPlugin.
    """
    image_file = ModelChoiceField(queryset=Image.objects.all(), required=False, label=_("Image"))

    def clean_glossary(self):
        glossary = super(NavbarPluginForm, self).clean_glossary()
        return glossary


class NavbarGridMixin(object):

    def get_grid_instance(self):
        fluid = self.glossary.get('fluid', False)
        try:
            breakpoints = [getattr(grid.Breakpoint, bp) for bp in self.glossary['breakpoints']]
        except KeyError:
            breakpoints = [bp for bp in grid.Breakpoint]
        if fluid:
            bounds = dict((bp, grid.fluid_bounds[bp]) for bp in breakpoints)
        else:
            bounds = dict((bp, grid.default_bounds[bp]) for bp in breakpoints)
        return grid.Bootstrap4Container(bounds=bounds)


class NavbarPlugin(BootstrapPluginBase):
    name = _("Navbar")
    model_mixins = ( NavbarGridMixin,)
    default_css_class = 'navbar'
    default_css_attributes = ('options',)
    require_parent = False
    parent_classes = None
    render_template = 'cascade/bootstrap4/navbar.html'
    glossary_variables = ['container_max_widths', 'media_queries']
    ring_plugin = 'JumbotronPlugin'
    OPTION_NAV_COLLAPSE = [(s, s) for s in [ "inherit", "navbar-expand","navbar-expand-sm", "navbar-expand-md","navbar-expand-lg", "navbar-expand-xl"] ]
    OPTION_NAV_COLOR = [(s, s) for s in [ "navbar-light", "navbar-dark"]]
    OPTION_NAV_BG_COLOR = [ "bg-primary", "bg-secondary","bg-success", "bg-danger", "bg-warning", "bg-info" ,"bg-light", "bg-dark" , "bg-white", "bg-transparent"] 
    OPTION_NAV_BG_GRADIENT = [ "bg-gradient-primary", "bg-gradient-secondary", "bg-gradient-success", "bg-gradient-danger", "bg-gradient-warning", "bg-gradient-info", "bg-gradient-light", "bg-gradient-dark"]
    OPTION_NAV_BG_MIX = OPTION_NAV_BG_COLOR + OPTION_NAV_BG_GRADIENT
    OPTION_NAV_PLACEMENTS=["inherit", "fixed-top" , "fixed-bottom" , "sticky-top"]

    container_glossary_fields = (
        GlossaryField(
            ContainerBreakpointsWidget(choices=get_widget_choices()),
            label=_("Available Breakpoints"),
            name='breakpoints',
            initial=app_settings.CMSPLUGIN_CASCADE['bootstrap4']['default_bounds'].keys(),
            help_text=_("Supported display widths for Bootstrap's grid system.")
        ),
        GlossaryField(
            MultipleCascadingSizeWidget([bp.name for bp in Breakpoint], allowed_units=['px', '%'], required=False),
            label=_("Adapt Picture Heights"),
            name='container_max_heights',
            initial={'xs': '100%', 'sm': '100%', 'md': '100%', 'lg': '100%', 'xl': '100%'},
            help_text=_("Heights of picture in percent or pixels for distinct Bootstrap's breakpoints.")
        ),
        GlossaryField(
            widgets.CheckboxSelectMultiple(choices=BootstrapPicturePlugin.RESIZE_OPTIONS),
            label=_("Resize Options"),
            name='resize_options',
            initial=['crop', 'subject_location', 'high_resolution'],
            help_text=_("Options to use when resizing the image.")
        ),
    )

    navbar_collapse = GlossaryField(
        widgets.Select(choices=OPTION_NAV_COLLAPSE),
        label=_('navbar collapse'),
        name='navbar_classes collapse',
        help_text=_("Adjust interval for the  navbar_collapse."),
    )

    navbar_color = GlossaryField(
        widgets.Select(choices=OPTION_NAV_COLOR),
        label=_('navbar bg color'),
        name='navbar_bg_color',
        help_text=_("Adjust interval for the  navbar color."),
    )

    navbar_bg_color= GlossaryField(
        widgets.Select(choices=[(s, s) for s in OPTION_NAV_BG_MIX ]),
        label=_('navbar-bg'),
        name='navbar_navbg',
        help_text=_("Adjust interval for the  navbar background color."),
    )

    navbar_placement= GlossaryField(
        widgets.Select(choices= [(s, s) for s in OPTION_NAV_PLACEMENTS]),
        label=_('navbar-place'),
        name='navbar_place',
        help_text=_("Adjust interval place s."),
    )

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(NavbarPlugin, cls).get_css_classes(obj)
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

    def get_form(self, request, obj=None, **kwargs):
        if self.get_parent_instance(request, obj) is None:
            # we only ask for breakpoints, if the jumbotron is the root of the placeholder
            kwargs.update(glossary_fields=list(self.container_glossary_fields))
            kwargs['glossary_fields'].extend(self.glossary_fields)
        form = super(NavbarPlugin, self).get_form(request, obj, **kwargs)
        return form


    @classmethod
    def get_identifier(cls, obj):
        identifier = super(NavbarPlugin, cls).get_identifier(obj)
        glossary = obj.get_complete_glossary()
        css_classes_without_default = obj.css_classes.replace( cls.default_css_class , '' , 1)
        return format_html('<div style="font-size: smaller; white-space: pre-wrap;" >{0}{1}</div>',
        identifier, css_classes_without_default)

plugin_pool.register_plugin(NavbarPlugin)


class  NavbarLinksItemsPlugin(BootstrapPluginBase):
    name = _("Nav Links Items")
    chojust=[ "inherit", "justify-content-start","justify-content-end", "justify-content-center", "justify-content-between", "justify-content-around" ] 
    chomrml=[ "inherit", "mr-auto", "ml-auto" ]
    choflex=[ "flex-row", "flex-wrap"]
    default_css_class = ''
    parent_classes = ['NavbarPlugin'] 
    render_template = 'cascade/bootstrap4/navbar_links.html'
    
    jus= GlossaryField(
        widgets.Select(choices= [(s, s) for s in chojust]),
        label=_('navbar-place'),
        name='navbar_place',
        help_text=_("Adjust interval place s."),
    )


    navflex= GlossaryField(
        widgets.Select(choices= [(s, s) for s in choflex]),
        label=_('navbar-place'),
        name='navbar_place',
        help_text=_("Adjust interval place s."),
    )

    mrml= GlossaryField(
        widgets.Select(choices= [(s, s) for s in chomrml]),
        label=_('navbar-place'),
        name='navbar_place',
        help_text=_("Adjust interval place UL"),
    )

plugin_pool.register_plugin(NavbarLinksItemsPlugin)


class  NavbarBrandPlugin(BootstrapPluginBase, LinkPluginBase,):
    name = _("Nav brand")
    parent_classes = ['NavbarPlugin'] 
    model_mixins = (LinkElementMixin,)
    render_template = 'cascade/bootstrap4/navbar_brand.html'
    fields =  list(LinkPluginBase.fields)

plugin_pool.register_plugin(NavbarBrandPlugin)


class NavbarBrandImagePluginForm(ImageFormMixin, ModelForm):
    """
    Form class to validate the NavbarBrandImage.
    """
    image_file = ModelChoiceField(queryset=Image.objects.all(), required=False, label=_("Image"))

    def clean_glossary(self):
        glossary = super(NavbarBrandImagePluginForm  , self).clean_glossary()
        return glossary


class  NavbarBrandImagePlugin(ImageAnnotationMixin, BootstrapPluginBase,  ):
    name = _("Nav brand Image")
    model_mixins = (ImagePropertyMixin,)
    form = NavbarBrandImagePluginForm
    parent_classes = ['NavbarBrandPlugin'] 
    allow_children = True
    alien_child_classes = True
    html_tag_attributes = {'image_title': 'title', 'alt_tag': 'tag'}
    raw_id_fields = ['image_file']
    fields = [  'glossary','image_file', ]
    SIZE_CHOICES = ('auto', 'width/height', 'cover', 'contain')
    
    RESIZE_OPTIONS = [
        ('upscale', _("Upscale image")),
        ('crop', _("Crop image")),
        ('subject_location', _("With subject location")),
        ('high_resolution', _("Optimized for Retina")),
]
    render_template = 'cascade/bootstrap4/navbar_brand_image.html'

    image_width_fixed = GlossaryField(
        CascadingSizeWidget(allowed_units=['px'], required=False),
        label=_("Fixed Image Width"),
        help_text=_("Set a fixed image width in pixels."),
    )

    image_height = GlossaryField(
        CascadingSizeWidget(allowed_units=['px', '%'], required=False),
        label=_("Adapt Image Height"),
        help_text=_("Set a fixed height in pixels, or percent relative to the image width."),
    )

    resize_options = GlossaryField(
        widgets.CheckboxSelectMultiple(choices=RESIZE_OPTIONS),
        label=_("Resize Options"),
        help_text=_("Options to use when resizing the image."),
        initial=['subject_location', 'high_resolution'],
    )

    def get_form(self, request, obj=None, **kwargs):
        if self.get_parent_instance(request, obj) is None:
            print(self.container_glossary_fields)
            # we only ask for breakpoints, if the jumbotron is the root of the placeholder
            kwargs.update(glossary_fields=list(self.container_glossary_fields))
            kwargs['glossary_fields'].extend(self.glossary_fields)
        form = super(NavbarBrandImagePlugin, self).get_form(request, obj, **kwargs)
        return form

    def render(self, context, instance, placeholder):
        tags = get_image_tags(instance)
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

plugin_pool.register_plugin(NavbarBrandImagePlugin)


class  NavbarCollapsePlugin(BootstrapPluginBase):
    name = _("Nav Collapse")
    parent_classes = ['NavbarPlugin'] 
    alien_child_classes = True
    render_template = 'cascade/bootstrap4/navbar_collapse.html'
    default_css_class = 'collapse navbar-collapse'

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(NavbarCollapsePlugin, cls).get_css_classes(obj)
        return css_classes

plugin_pool.register_plugin(NavbarCollapsePlugin)


class  NavbarNavListPlugin(BootstrapPluginBase):
    name = _("Nav list")
    parent_classes = ['NavbarPlugin', 'NavbarCollapsePlugin' ] 
    alien_child_classes = True
    render_template = 'cascade/bootstrap4/navbar_nav_list.html'
    default_css_class = 'navbar-nav'

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(NavbarNavListPlugin, cls).get_css_classes(obj)
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(NavbarNavListPlugin, cls).get_identifier(obj)
        glossary = obj.get_complete_glossary()
        if hasattr(cls,'default_css_class'):
            css_classes_without_default = obj.css_classes.replace( cls.default_css_class , '' , 1)
            print(obj.css_classes.__dict__)
        else:
            css_classes_without_default = obj.css_classes
        return format_html('<div style="font-size: smaller; white-space: pre-wrap;" >{0}{1}</div>',
        identifier, css_classes_without_default )

plugin_pool.register_plugin(NavbarNavListPlugin)


class  NavbarNavItemsMainMemuPlugin(BootstrapPluginBase):
    name = _("Nav items main menu")
    parent_classes = ['NavbarNavListPlugin'] 
    alien_child_classes = True
    render_template = 'cascade/bootstrap4/navbar_nav_items_links.html'

plugin_pool.register_plugin(NavbarNavItemsMainMemuPlugin)


class  NavbarNavItemsPlugin(BootstrapPluginBase):
    default_css_class = 'nav-item'
    name = _("Nav item")
    parent_classes = ['NavbarNavListPlugin'] 
    alien_child_classes = True
    render_template = 'cascade/bootstrap4/navbar_nav_item.html'

plugin_pool.register_plugin(NavbarNavItemsPlugin)


class  NavbarNavLinkPlugin(BootstrapPluginBase):

    name = _("Nav Link")
    parent_classes = ['NavbarNavItemsPlugin'] 
    alien_child_classes = True
    render_template = 'cascade/bootstrap4/navbar_nav_link.html'

plugin_pool.register_plugin(NavbarNavLinkPlugin)


class  NavbarToogler(BootstrapPluginBase):
    name = _("Nav toogler")
    default_css_class = ''
    parent_classes = ['NavbarPlugin'] 
    render_template = 'cascade/bootstrap4/navbar_toogler.html'

plugin_pool.register_plugin(NavbarToogler)
