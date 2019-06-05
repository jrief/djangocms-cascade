from django.forms import ChoiceField
from django.utils.functional import cached_property
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import SizeField, ColorField, BorderChoiceField
from cmsplugin_cascade.link.config import LinkPluginBase, LinkElementMixin
from cmsplugin_cascade.icon.mixins import IconPluginMixin2
from entangled.forms import EntangledModelFormMixin, get_related_object


class SimpleIconPlugin(IconPluginMixin2, LinkPluginBase):
    name = _("Simple Icon")
    parent_classes = None
    require_parent = False
    allow_children = False
    render_template = 'cascade/plugins/simpleicon.html'
    model_mixins = (LinkElementMixin,)
    ring_plugin = 'IconPlugin'
    link_required = False

    # icon_font = GlossaryField(
    #     widgets.Select(),
    #     label=_("Font"),
    #     initial=get_default_icon_font,
    # )
    #
    # symbol = GlossaryField(
    #     widgets.HiddenInput(),
    #     label=_("Select Symbol"),
    # )

    class Media:
        js = ['cascade/js/admin/iconplugin.js']

    # glossary_field_order = ['icon_font', 'symbol']

    def Xget_form(self, request, obj=None, **kwargs):
        kwargs.update(form=VoluntaryLinkForm.get_form_class())
        return super(SimpleIconPlugin, self).get_form(request, obj, **kwargs)

    def Xrender(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        icon_font = self.get_icon_font(instance)
        symbol = instance.glossary.get('symbol')
        if icon_font and symbol:
            font_attr = 'class="{}{}"'.format(icon_font.config_data.get('css_prefix_text', 'icon-'), symbol)
            context['icon_font_attrs'] = mark_safe(font_attr)
        return context

plugin_pool.register_plugin(SimpleIconPlugin)


class FramedIconFormMixin(EntangledModelFormMixin):
    SIZE_CHOICES = [('{}em'.format(c), "{} em".format(c)) for c in range(1, 13)]

    RADIUS_CHOICES = [(None, _("Square"))] + \
        [('{}px'.format(r), "{} px".format(r)) for r in (1, 2, 3, 5, 7, 10, 15, 20)] + \
        [('50%', _("Circle"))]

    TEXT_ALIGN_CHOICES = [
        (None, _("Do not align")),
        ('text-left', _("Left")),
        ('text-center', _("Center")),
        ('text-right', _("Right"))
    ]

    font_size = SizeField(
        label=_("Icon size"),
        allowed_units=['px', 'em'],
        initial='1em',
    )

    color = ColorField(
        label=_("Icon color"),
    )

    background_color = ColorField(
        label=_("Background color"),
    )

    text_align = ChoiceField(
        choices=TEXT_ALIGN_CHOICES,
        label=_("Text alignment"),
        required=False,
        help_text=_("Align the icon inside the parent column.")
    )

    border = BorderChoiceField(
        label=_("Set border"),
    )

    border_radius = ChoiceField(
        choices=RADIUS_CHOICES,
        label=_("Border radius"),
        required=False,
    )

    class Meta:
        entangled_fields = {'glossary': ['font_size', 'color', 'background_color', 'text_align', 'border', 'border_radius']}


class FramedIconPlugin(IconPluginMixin2, LinkPluginBase):
    name = _("Icon with frame")
    parent_classes = None
    require_parent = False
    allow_children = False
    render_template = 'cascade/plugins/framedicon.html'
    model_mixins = (LinkElementMixin,)
    ring_plugin = 'FramedIconPlugin'
    link_required = False

    # icon_font = GlossaryField(
    #     widgets.Select(),
    #     label=_("Font"),
    #     initial=get_default_icon_font,
    # )
    #
    # symbol = GlossaryField(
    #     widgets.HiddenInput(),
    #     label=_("Select Symbol"),
    # )

    #glossary_field_order = ['icon_font', 'symbol', 'text_align', 'font_size', 'color', 'background_color',
    #                        'border', 'border_radius']

    class Media:
        js = ['cascade/js/admin/framediconplugin.js']

    @classmethod
    def get_tag_type(self, instance):
        if instance.glossary.get('text_align') or instance.glossary.get('font_size'):
            return 'div'

    @classmethod
    def get_css_classes(cls, instance):
        css_classes = cls.super(FramedIconPlugin, cls).get_css_classes(instance)
        text_align = instance.glossary.get('text_align')
        if text_align:
            css_classes.append(text_align)
        return css_classes

    @classmethod
    def get_inline_styles(cls, instance):
        inline_styles = cls.super(FramedIconPlugin, cls).get_inline_styles(instance)
        inline_styles['font-size'] = instance.glossary.get('font_size', '1em')
        return inline_styles

    def get_form(self, request, obj=None, **kwargs):
        kwargs.setdefault('form', FramedIconFormMixin)
        return super().get_form(request, obj, **kwargs)

    def render(self, context, instance, placeholder):
        context = self.super(FramedIconPlugin, self).render(context, instance, placeholder)
        icon_font = get_related_object(instance.glossary, 'icon_font')
        symbol = instance.glossary.get('symbol')
        attrs = []
        if icon_font and symbol:
            attrs.append(mark_safe('class="{}{}"'.format(icon_font.config_data.get('css_prefix_text', 'icon-'), symbol)))
        styles = {'display': 'inline-block'}
        inherit, color = instance.glossary.get('color', (True, '#000'))
        if not inherit:
            styles['color'] = color
        inherit, background_color = instance.glossary.get('background_color', (True, '#fff'))
        if not inherit:
            styles['background-color'] = background_color
        border = instance.glossary.get('border')
        if isinstance(border, list) and border[0] and border[1] != 'none':
            styles.update(border='{0} {1} {2}'.format(*border))
            radius = instance.glossary.get('border_radius')
            if radius:
                styles['border-radius'] = radius
        attrs.append(format_html('style="{}"', format_html_join('', '{0}:{1};', [(k, v) for k, v in styles.items()])))
        context['icon_font_attrs'] = mark_safe(' '.join(attrs))
        return context

plugin_pool.register_plugin(FramedIconPlugin)


class TextIconModelMixin(object):
    @cached_property
    def icon_font_class(self):
        icon_font = self.plugin_class.get_icon_font(self)
        symbol = self.glossary.get('symbol')
        if icon_font and symbol:
            return mark_safe('class="{}{}"'.format(icon_font.config_data.get('css_prefix_text', 'icon-'), symbol))
        return ''


class TextIconPlugin(IconPluginMixin2, LinkPluginBase):
    """
    This plugin is intended to be used inside the django-CMS-CKEditor.
    """
    name = _("Icon in text")
    text_enabled = True
    render_template = 'cascade/plugins/texticon.html'
    ring_plugin = 'IconPlugin'
    parent_classes = ['TextPlugin']
    model_mixins = (TextIconModelMixin, LinkElementMixin,)
    allow_children = False
    require_parent = False

    # icon_font = GlossaryField(
    #     widgets.Select(),
    #     label=_("Font"),
    #     initial=get_default_icon_font,
    # )
    #
    # symbol = GlossaryField(
    #     widgets.HiddenInput(),
    #     label=_("Select Symbol"),
    # )

    # color = GlossaryField(
    #     ColorPickerWidget(),
    #     label=_("Icon color"),
    # )

    glossary_field_order = ['icon_font', 'symbol', 'color']

    class Media:
        js = ['cascade/js/admin/iconplugin.js']

    @classmethod
    def requires_parent_plugin(cls, slot, page):
        return False

    def get_form(self, request, obj=None, **kwargs):
        kwargs.update(form=VoluntaryLinkForm.get_form_class())
        return super(TextIconPlugin, self).get_form(request, obj, **kwargs)

    @classmethod
    def get_inline_styles(cls, instance):
        inline_styles = cls.super(TextIconPlugin, cls).get_inline_styles(instance)
        color = instance.glossary.get('color')
        if isinstance(color, list) and len(color) == 2 and not color[0]:
            inline_styles['color'] = color[1]
        return inline_styles

plugin_pool.register_plugin(TextIconPlugin)
