from django.forms import widgets
from django.forms.fields import BooleanField, CharField, ChoiceField, MultipleChoiceField
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from entangled.forms import EntangledModelFormMixin
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.icon.plugin_base import IconPluginMixin
from cmsplugin_cascade.icon.forms import IconFormMixin
from cmsplugin_cascade.link.config import LinkPluginBase, LinkFormMixin
from cmsplugin_cascade.link.plugin_base import LinkElementMixin


class ButtonTypeWidget(widgets.RadioSelect):
    """
    Render sample buttons in different colors in the button's backend editor.
    """
    template_name = 'cascade/admin/widgets/button_types.html'


class ButtonSizeWidget(widgets.RadioSelect):
    """
    Render sample buttons in different sizes in the button's backend editor.
    """
    template_name = 'cascade/admin/widgets/button_sizes.html'


class ButtonFormMixin(EntangledModelFormMixin):
    BUTTON_TYPES = [
        ('btn-primary', _("Primary")),
        ('btn-secondary', _("Secondary")),
        ('btn-success', _("Success")),
        ('btn-danger', _("Danger")),
        ('btn-warning', _("Warning")),
        ('btn-info', _("Info")),
        ('btn-light', _("Light")),
        ('btn-dark', _("Dark")),
        ('btn-link', _("Link")),
        ('btn-outline-primary', _("Primary")),
        ('btn-outline-secondary', _("Secondary")),
        ('btn-outline-success', _("Success")),
        ('btn-outline-danger', _("Danger")),
        ('btn-outline-warning', _("Warning")),
        ('btn-outline-info', _("Info")),
        ('btn-outline-light', _("Light")),
        ('btn-outline-dark', _("Dark")),
        ('btn-outline-link', _("Link")),
    ]

    BUTTON_SIZES = [
        ('btn-lg', _("Large button")),
        ('', _("Default button")),
        ('btn-sm', _("Small button")),
    ]

    link_content = CharField(
        required=False,
        label=_("Button Content"),
        widget=widgets.TextInput(attrs={'size': 50}),
    )

    button_type = ChoiceField(
        label=_("Button Type"),
        widget=ButtonTypeWidget(choices=BUTTON_TYPES),
        choices=BUTTON_TYPES,
        initial='btn-primary',
        help_text=_("Display Link using this Button Style")
    )

    button_size = ChoiceField(
        label=_("Button Size"),
        widget=ButtonSizeWidget(choices=BUTTON_SIZES),
        choices=BUTTON_SIZES,
        initial='',
        required=False,
        help_text=_("Display Link using this Button Size")
    )

    button_options = MultipleChoiceField(
        label=_("Button Options"),
        choices=[
            ('btn-block', _('Block level')),
            ('disabled', _('Disabled')),
        ],
        required=False,
        widget=widgets.CheckboxSelectMultiple,
    )

    stretched_link = BooleanField(
        label=_("Stretched link"),
        required=False,
        help_text=_("Stretched-link utility to make any anchor the size of it’s nearest position: " \
                    "relative parent, perfect for entirely clickable cards!")
    )

    icon_align = ChoiceField(
        label=_("Icon alignment"),
        choices=[
            ('icon-left', _("Icon placed left")),
            ('icon-right', _("Icon placed right")),
        ],
        widget=widgets.RadioSelect,
        initial='icon-right',
        help_text=_("Add an Icon before or after the button content."),
    )

    class Meta:
        entangled_fields = {'glossary': ['link_content', 'button_type', 'button_size', 'button_options', 'icon_align',
                                         'stretched_link']}


class BootstrapButtonMixin(IconPluginMixin):
    require_parent = True
    parent_classes = ['BootstrapColumnPlugin', 'SimpleWrapperPlugin']
    render_template = 'cascade/bootstrap4/button.html'
    allow_children = False
    default_css_class = 'btn'
    default_css_attributes = ['button_type', 'button_size', 'button_options', 'stretched_link']
    ring_plugin = 'ButtonMixin'

    class Media:
        css = {'all': ['cascade/css/admin/bootstrap4-buttons.css', 'cascade/css/admin/iconplugin.css']}
        js = ['admin/js/jquery.init.js', 'cascade/js/admin/buttonmixin.js']

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        if 'icon_font_class' in context:
            mini_template = '{0}<i class="{1} {2}" aria-hidden="true"></i>{3}'
            icon_align = instance.glossary.get('icon_align')
            if icon_align == 'icon-left':
                context['icon_left'] = format_html(mini_template, '', context['icon_font_class'], 'cascade-icon-left',
                                                   ' ')
            elif icon_align == 'icon-right':
                context['icon_right'] = format_html(mini_template, ' ', context['icon_font_class'],
                                                    'cascade-icon-right', '')
        return context


class BootstrapButtonFormMixin(LinkFormMixin, IconFormMixin, ButtonFormMixin):
    require_link = False
    require_icon = False


class BootstrapButtonPlugin(BootstrapButtonMixin, LinkPluginBase):
    module = 'Bootstrap'
    name = _("Button")
    model_mixins = (LinkElementMixin,)
    form = BootstrapButtonFormMixin
    ring_plugin = 'ButtonPlugin'
    DEFAULT_BUTTON_ATTRIBUTES = {'role': 'button'}

    class Media:
        js = ['admin/js/jquery.init.js', 'cascade/js/admin/buttonplugin.js']

    @classmethod
    def get_identifier(cls, instance):
        content = instance.glossary.get('link_content')
        if not content:
            try:
                button_types = dict(ButtonFormMixin.BUTTON_TYPES)
                content = str(button_types[instance.glossary['button_type']])
            except KeyError:
                content = _("Empty")
        return content

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapButtonPlugin, cls).get_css_classes(obj)
        if obj.glossary.get('stretched_link'):
            css_classes.append('stretched_link')
        return css_classes

    @classmethod
    def get_html_tag_attributes(cls, obj):
        attributes = cls.super(BootstrapButtonPlugin, cls).get_html_tag_attributes(obj)
        attributes.update(cls.DEFAULT_BUTTON_ATTRIBUTES)
        return attributes

    def render(self, context, instance, placeholder):
        context = self.super(BootstrapButtonPlugin, self).render(context, instance, placeholder)
        return context

plugin_pool.register_plugin(BootstrapButtonPlugin)
