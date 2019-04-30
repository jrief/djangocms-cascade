# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
try:
    from html.parser import HTMLParser  # py3
except ImportError:
    from HTMLParser import HTMLParser  # py2

from django.forms import widgets, ModelChoiceField
from django.utils.html import format_html
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.forms.fields import IntegerField
from django.forms.models import ModelForm

from cms.plugin_pool import plugin_pool
from filer.models.imagemodels import Image

from cmsplugin_cascade import app_settings
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.image import ImageFormMixin, ImagePropertyMixin

from cmsplugin_cascade.forms import ManageChildrenFormMixin
#from cmsplugin_cascade.mixins import ImagePropertyMixin , WithInlineElementsMixin
from cmsplugin_cascade.mixins import WithInlineElementsMixin
from cmsplugin_cascade.widgets import NumberInputWidget, MultipleCascadingSizeWidget

from cmsplugin_cascade.bootstrap4.plugin_base import BootstrapPluginBase
#from cmsplugin_bs4forcascade.bootstrap4.image import ImageForm, ImageAnnotationMixin,ImageFormMixin
from cmsplugin_cascade.image import ImageAnnotationMixin, ImagePropertyMixin, ImageFormMixin
from cmsplugin_cascade.bootstrap4.picture import BootstrapPicturePlugin

from cmsplugin_cascade.plugin_base import CascadePluginBase, TransparentContainer
from django.template.loader import get_template

from cmsplugin_cascade.widgets import CascadingSizeWidget

from django.forms import widgets, ModelChoiceField
 
from cmsplugin_cascade.widgets import  ColorPickerWidget 
from cmsplugin_cascade.bootstrap4.container import ContainerBreakpointsWidget,ContainerGridMixin, get_widget_choices,  ColumnGridMixin

from cmsplugin_cascade.bootstrap4.grid import Breakpoint

from cmsplugin_cascade.link.config import LinkPluginBase, LinkElementMixin, LinkForm
from cmsplugin_cascade.bootstrap4.image import BootstrapImagePlugin

from .picture import BootstrapPicturePlugin, get_picture_elements
from .plugin_base import BootstrapPluginBase
from .grid import Breakpoint
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
        #if glossary['background_size'] == 'width/height' and not glossary['background_width_height']['width']:
        #    raise ValidationError(_("You must at least set a background width."))
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
    OPTION_NAV_COLLAPSE = [(s, s) for s in [ "navbar-expand","navbar-expand-sm", "navbar-expand-md","navbar-expand-lg", "navbar-expand-xl"] ]
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

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))

        super(NavbarPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, NavbarLinksItemsPlugin)
        obj.sanitize_children()

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
        identifier, css_classes_without_default )

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
 #   BootstrapImagePlugin.__module__
    print('okok')
    print(BootstrapImagePlugin.sharable_fields)
    print(dir(BootstrapImagePlugin))
    print(BootstrapImagePlugin)
#    fields = ('glossary', 'image_file',)
    name = _("Nav brand Image")
    model_mixins = (ImagePropertyMixin, )
    form = NavbarBrandImagePluginForm
    parent_classes = ['NavbarBrandPlugin'] 
    allow_children = True
    alien_child_classes = True
    html_tag_attributes = {'image_title': 'title', 'alt_tag': 'tag'}
    raw_id_fields = ['image_file']
    fields = [  'glossary','image_file', ]
    render_template = 'cascade/bootstrap4/navbar_brand_image.html'

    def get_form(self, request, obj=None, **kwargs):
        print('self.get_parent_instance(request, obj)' )
        print(self.get_parent_instance(request, obj) )

        if self.get_parent_instance(request, obj) is None:
            print(self.container_glossary_fields)
            # we only ask for breakpoints, if the jumbotron is the root of the placeholder
            kwargs.update(glossary_fields=list(self.container_glossary_fields))
            kwargs['glossary_fields'].extend(self.glossary_fields)
        form = super(NavbarBrandImagePlugin, self).get_form(request, obj, **kwargs)
        return form
    
    def render(self, context, instance, placeholder):
        # slide image shall be rendered in a responsive context using the ``<picture>`` element
        try:
            elements = get_picture_elements(instance)
        except Exception as exc:

            logger.warning("Unable generate picture elements. Reason: {}".format(exc))
        else:
            context.update({
                'instance': instance,
                'is_fluid': False,
                'placeholder': placeholder,
                'elements': elements,
            })
        return self.super(NavbarBrandImagePlugin, self).render(context, instance, placeholder)
 
        def render(self, context, instance, placeholder):
            context = super(NavbarBrandImagePlugin, self).render(context, instance, placeholder)
        return context

plugin_pool.register_plugin(NavbarBrandImagePlugin)

class  NavbarCollapsePlugin(BootstrapPluginBase):
    name = _("Nav Collapse")
    parent_classes = ['NavbarPlugin'] 
    alien_child_classes = True
    render_template = 'cascade/bootstrap4/navbar_collapse.html'
    default_css_class = 'navbar-nav'

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
        css_classes_without_default = obj.css_classes.replace( cls.default_css_class , '' )
        return format_html('<div style="font-size: smaller; white-space: pre-wrap;" >{0}{1}</div>',
        identifier, css_classes_without_default )
        
plugin_pool.register_plugin(NavbarNavListPlugin)



class  NavbarNavItemsMainMemuPlugin(BootstrapPluginBase):
#    fields = ('glossary', 'image_file',)
    name = _("Nav items main menu")
    parent_classes = ['NavbarNavListPlugin'] 
    alien_child_classes = True
    #model_mixins = (LinkElementMixin,)
    render_template = 'cascade/bootstrap4/navbar_nav_items_links.html'
    
plugin_pool.register_plugin(NavbarNavItemsMainMemuPlugin)

class  NavbarNavItemsPlugin(BootstrapPluginBase):

    name = _("Nav item")
    parent_classes = ['NavbarNavListPlugin'] 
    alien_child_classes = True
    render_template = 'cascade/bootstrap4/navbar_nav_items.html'

plugin_pool.register_plugin(NavbarNavItemsPlugin)



class  NavbarNavLinkPlugin(BootstrapPluginBase):

    name = _("Nav Link")
    parent_classes = ['NavbarNavItemsPlugin'] 
    alien_child_classes = True
    render_template = 'cascade/bootstrap4/navbar_nav_link.html'

plugin_pool.register_plugin(NavbarNavLinkPlugin)




class  MenubrandPlugin(BootstrapPluginBase, ImageAnnotationMixin, LinkPluginBase):

    name = _("menu_Contenu_brand")
    model_mixins = (ImagePropertyMixin,)
    form = NavbarPluginForm
    default_css_class = ''
    fields = ('glossary', 'image_file',)
    parent_classes = ['NavbarPlugin'] 
    alien_child_classes = True
    render_template = 'cascade/bootstrap4/navbar_brand.html'

    def get_form(self, request, obj=None, **kwargs):
        LINK_TYPE_CHOICES = [('none', _("No Link"))]
        LINK_TYPE_CHOICES.extend(t for t in getattr(LinkForm, 'LINK_TYPE_CHOICES') if t[0] != 'email')
        image_file = ModelChoiceField(queryset=Image.objects.all(), required=False, label=_("Image"))
        Form = type(str('ImageForm'), (ImageFormMixin, getattr(LinkForm, 'get_form_class')(),),
                    {'LINK_TYPE_CHOICES': LINK_TYPE_CHOICES, 'image_file': image_file})
        kwargs.update(form=Form)
        return super(MenubrandPlugin, self).get_form(request, obj, **kwargs)

    def render(self, context, instance, placeholder):
        # image shall be rendered in a responsive context using the ``<picture>`` element
        elements = get_picture_elements(instance)
        context.update({
            'elements': [e for e in elements if 'media' in e] if elements else [],
            'CSS_PREFIXES': app_settings.CSS_PREFIXES,
        })
        return self.super(MenubrandPlugin, self).render(context, instance, placeholder)
    """
    @classmethod
    def sanitize_model(cls, obj):
        sanitized = super(MenubrandPlugin, cls).sanitize_model(obj)
        complete_glossary = obj.get_complete_glossary()
        # fill all invalid heights for this container to a meaningful value
        max_height = max(obj.glossary['container_max_heights'].values())
        pattern = re.compile(r'^(\d+)px$')
        for bp in complete_glossary.get('breakpoints', ()):
            if not pattern.match(obj.glossary['container_max_heights'].get(bp, '')):
                obj.glossary['container_max_heights'][bp] = max_height

        return sanitized
    """
      
    @classmethod
    def get_identifier(cls, obj):
        identifier = super(MenubrandPlugin, cls).get_identifier(obj)
        try:
            content = obj.image.name or obj.image.original_filename
        except AttributeError:
            content = _("Without background image")
        return format_html('{0}{1}', identifier, content)

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = super(MenubrandPlugin, cls).sanitize_model(obj)
        resize_options = obj.get_parent_glossary().get('resize_options', [])
        if obj.glossary.get('resize_options') != resize_options:
            obj.glossary.update(resize_options=resize_options)
            sanitized = True
        parent = obj.parent
        while parent.plugin_type != 'BootstrapColumnPlugin':
            parent = parent.parent
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

plugin_pool.register_plugin(MenubrandPlugin)


class  NavbarToogler(BootstrapPluginBase):
    name = _("Nav toogler")
#    model_mixins = (ImagePropertyMixin,)
#    model_mixins = (CssBackgroundMixin,)
#    form = ImageForm  
    default_css_class = ''
    parent_classes = ['NavbarPlugin'] 
    render_template = 'cascade/bootstrap4/navbar_toogler.html'

plugin_pool.register_plugin(NavbarToogler)




