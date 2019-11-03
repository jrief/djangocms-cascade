from django.forms import widgets, CharField, ChoiceField, MultipleChoiceField
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from entangled.forms import EntangledModelFormMixin
from cmsplugin_cascade import app_settings
from cmsplugin_cascade.fields import SizeField
from cmsplugin_cascade.image import ImageFormMixin, ImagePropertyMixin
from cmsplugin_cascade.link.config import LinkPluginBase, LinkFormMixin
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.plugin_base import CascadePluginBase, TransparentContainer
from cmsplugin_cascade.utils import compute_aspect_ratio


class SimpleWrapperFormMixin(EntangledModelFormMixin):
    TAG_CHOICES = [(cls, _("<{}> – Element").format(cls)) for cls in ['div', 'span', 'section', 'article']] + \
                  [('naked', _("Naked Wrapper"))]

    tag_type = ChoiceField(
        choices=TAG_CHOICES,
        label=_("HTML element tag"),
        help_text=_('Choose a tag type for this HTML element.')
    )

    class Meta:
        entangled_fields = {'glossary': ['tag_type']}


class SimpleWrapperPlugin(TransparentContainer, CascadePluginBase):
    name = _("Simple Wrapper")
    parent_classes = None
    require_parent = False
    form = SimpleWrapperFormMixin
    allow_children = True
    alien_child_classes = True

    @classmethod
    def get_identifier(cls, instance):
        identifier = super().get_identifier(instance)
        tag_name = dict(SimpleWrapperFormMixin.TAG_CHOICES).get(instance.glossary.get('tag_type'))
        if tag_name:
            return format_html('{0} {1}', tag_name, identifier)
        return identifier

    def get_render_template(self, context, instance, placeholder):
        if instance.glossary.get('tag_type') == 'naked':
            return 'cascade/generic/naked.html'
        return 'cascade/generic/wrapper.html'

plugin_pool.register_plugin(SimpleWrapperPlugin)


class HorizontalRulePlugin(CascadePluginBase):
    name = _("Horizontal Rule")
    parent_classes = None
    allow_children = False
    tag_type = 'hr'
    render_template = 'cascade/generic/single.html'

plugin_pool.register_plugin(HorizontalRulePlugin)


class HeadingFormMixin(EntangledModelFormMixin):
    TAG_TYPES = [('h{}'.format(k), _("Heading {}").format(k)) for k in range(1, 7)]

    tag_type = ChoiceField(
        choices=TAG_TYPES,
        label=_("HTML element tag"),
        help_text=_('Choose a tag type for this HTML element.')
    )

    content = CharField(
        label=_("Heading content"),
        widget=widgets.TextInput(attrs={'style': 'width: 100%; padding-right: 0; font-weight: bold; font-size: 125%;'}),
    )

    class Meta:
        entangled_fields = {'glossary': ['tag_type', 'content']}


class HeadingPlugin(CascadePluginBase):
    name = _("Heading")
    parent_classes = None
    allow_children = False
    form = HeadingFormMixin
    render_template = 'cascade/generic/heading.html'

    @classmethod
    def get_identifier(cls, instance):
        tag_type = instance.glossary.get('tag_type')
        content = mark_safe(instance.glossary.get('content', ''))
        if tag_type:
            return format_html('<code>{0}</code>: {1}', tag_type, content)
        return content

    def render(self, context, instance, placeholder):
        context = self.super(HeadingPlugin, self).render(context, instance, placeholder)
        context.update({'content': mark_safe(instance.glossary.get('content', ''))})
        return context

plugin_pool.register_plugin(HeadingPlugin)


class CustomSnippetPlugin(TransparentContainer, CascadePluginBase):
    """
    Allows to add a customized template anywhere. This plugins will be registered only if the
    project added a template using the configuration setting 'plugins_with_extra_render_templates'.
    """
    name = _("Custom Snippet")
    require_parent = False
    allow_children = True
    alien_child_classes = True
    render_template_choices = dict(app_settings.CMSPLUGIN_CASCADE['plugins_with_extra_render_templates'].get('CustomSnippetPlugin', ()))
    render_template = 'cascade/generic/does_not_exist.html'  # default in case the template could not be found

    @classmethod
    def get_identifier(cls, instance):
        render_template = instance.glossary.get('render_template')
        if render_template:
            return format_html('{}', cls.render_template_choices.get(render_template))


if CustomSnippetPlugin.render_template_choices:
    # register only, if at least one template has been defined
    plugin_pool.register_plugin(CustomSnippetPlugin)


class TextImageFormMixin(ImageFormMixin):
    RESIZE_OPTIONS = [
        ('upscale', _("Upscale image")),
        ('crop', _("Crop image")),
        ('subject_location', _("With subject location")),
        ('high_resolution', _("Optimized for Retina")),
    ]

    image_width = SizeField(
        label=_("Image Width"),
        allowed_units=['px'],
        required=True,
        help_text=_("Set the image width in pixels."),
    )

    image_height = SizeField(
        label=_("Image Height"),
        allowed_units=['px'],
        required=False,
        help_text=_("Set the image height in pixels."),
    )

    resize_options = MultipleChoiceField(
        label=_("Resize Options"),
        choices = RESIZE_OPTIONS,
        required=False,
        widget=widgets.CheckboxSelectMultiple,
        help_text=_("Options to use when resizing the image."),
        initial=['subject_location', 'high_resolution']
    )

    alignement = ChoiceField(
        label=_("Alignement"),
        choices=[('', _("Not aligned")), ('left', _("Left")), ('right', _("Right"))],
        required=False,
        widget=widgets.RadioSelect,
        initial='',
    )

    class Meta:
        entangled_fields = {'glossary': ['image_width', 'image_height', 'resize_options', 'alignement']}


class TextImagePlugin(LinkPluginBase):
    name = _("Image in text")
    text_enabled = True
    ring_plugin = 'TextImagePlugin'
    render_template = 'cascade/plugins/textimage.html'
    parent_classes = ['TextPlugin']
    model_mixins = (ImagePropertyMixin, LinkElementMixin)
    allow_children = False
    require_parent = False
    form = type('TextImageForm', (LinkFormMixin, TextImageFormMixin), {'require_link': False})
    html_tag_attributes = {'image_title': 'title', 'alt_tag': 'tag'}
    html_tag_attributes.update(LinkPluginBase.html_tag_attributes)

    class Media:
        js = ['admin/js/jquery.init.js', 'cascade/js/admin/textimageplugin.js']

    @classmethod
    def requires_parent_plugin(cls, slot, page):
        """
        Workaround for `PluginPool.get_all_plugins()`, otherwise TextImagePlugin is not allowed
        as a child of a `TextPlugin`.
        """
        return False

    @classmethod
    def get_inline_styles(cls, instance):
        inline_styles = cls.super(TextImagePlugin, cls).get_inline_styles(instance)
        alignement = instance.glossary.get('alignement')
        if alignement:
            inline_styles['float'] = alignement
        return inline_styles

    def render(self, context, instance, placeholder):
        context = self.super(TextImagePlugin, self).render(context, instance, placeholder)
        try:
            aspect_ratio = compute_aspect_ratio(instance.image)
        except Exception:
            # if accessing the image file fails, abort here
            return context
        resize_options = instance.glossary.get('resize_options', {})
        crop = 'crop' in resize_options
        upscale = 'upscale' in resize_options
        subject_location = instance.image.subject_location if 'subject_location' in resize_options else False
        high_resolution = 'high_resolution' in resize_options
        image_width = instance.glossary.get('image_width', '')
        if not image_width.endswith('px'):
            return context
        image_width = int(image_width.rstrip('px'))
        image_height = instance.glossary.get('image_height', '')
        if image_height.endswith('px'):
            image_height = int(image_height.rstrip('px'))
        else:
            image_height = int(round(image_width * aspect_ratio))
        context['src'] = {
            'size': (image_width, image_height),
            'size2x': (image_width * 2, image_height * 2),
            'crop': crop,
            'upscale': upscale,
            'subject_location': subject_location,
            'high_resolution': high_resolution,
        }
        link_attributes = LinkPluginBase.get_html_tag_attributes(instance)
        context['link_html_tag_attributes'] = format_html_join(' ', '{0}="{1}"',
            [(attr, val) for attr, val in link_attributes.items() if val]
        )
        return context

plugin_pool.register_plugin(TextImagePlugin)
