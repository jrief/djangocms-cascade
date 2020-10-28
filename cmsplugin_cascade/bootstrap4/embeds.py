import re
from urllib.parse import urlparse, urlunparse, ParseResult

from django.core.exceptions import ValidationError
from django.forms import widgets
from django.forms.fields import BooleanField, ChoiceField, URLField, Field
from django.utils.translation import gettext_lazy as _
from entangled.forms import EntangledModelFormMixin, EntangledField
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap4.plugin_base import BootstrapPluginBase


class YoutubeFormMixin(EntangledModelFormMixin):
    ASPECT_RATIO_CHOICES = [
        ('embed-responsive-21by9', _("Responsive 21:9")),
        ('embed-responsive-16by9', _("Responsive 16:9")),
        ('embed-responsive-4by3', _("Responsive 4:3")),
        ('embed-responsive-1by1', _("Responsive 1:1")),
    ]

    videoid = EntangledField()

    url = URLField(
        label=_("YouTube URL"),
        widget=widgets.URLInput(attrs={'size': 50}),
    )

    aspect_ratio = ChoiceField(
        label=_("Aspect Ratio"),
        choices=ASPECT_RATIO_CHOICES,
        widget=widgets.RadioSelect,
        initial=ASPECT_RATIO_CHOICES[1][0],
    )

    allow_fullscreen = BooleanField(
        label=_("Allow Fullscreen"),
        required=False,
        initial=True,
    )

    autoplay = BooleanField(
        label=_("Autoplay"),
        required=False,
    )

    controls = BooleanField(
        label=_("Display Controls"),
        required=False,
    )

    loop = BooleanField(
        label=_("Enable Looping"),
        required=False,
    )

    rel = BooleanField(
        label=_("Show related"),
        required=False,
    )

    class Meta:
        untangled_fields = ['url']
        entangled_fields = {'glossary': ['videoid', 'aspect_ratio', 'allow_fullscreen', 'autoplay',
                                         'controls', 'loop', 'rel']}

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            videoid = instance.glossary.get('videoid')
            if videoid:
                parts = ParseResult('https', 'youtu.be', videoid, '', '', '')
                initial = {'url': urlunparse(parts)}
                kwargs.update(initial=initial)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get('url')
        if url:
            parts = urlparse(url)
            match = re.search(r'^v=([^&]+)', parts.query)
            if match:
                cleaned_data['videoid'] = match.group(1)
                return cleaned_data
            match = re.search(r'([^/]+)$', parts.path)
            if match:
                cleaned_data['videoid'] = match.group(1)
                return cleaned_data
        raise ValidationError(_("Please enter a valid YouTube URL"))


class BootstrapYoutubePlugin(BootstrapPluginBase):
    """
    Use this plugin to display a YouTube video.
    """
    name = _("You Tube")
    require_parent = False
    parent_classes = ['BootstrapColumnPlugin']
    child_classes = None
    render_template = 'cascade/bootstrap4/youtube.html'
    form = YoutubeFormMixin

    def render(self, context, instance, placeholder):
        context = self.super(BootstrapYoutubePlugin, self).render(context, instance, placeholder)
        query_params = ['autoplay', 'controls', 'loop', 'rel']
        videoid = instance.glossary.get('videoid')
        if videoid:
            query = ['{}=1'.format(key) for key in query_params if instance.glossary.get(key)]
            parts = ParseResult('https', 'www.youtube.com', '/embed/' + videoid, '', '&'.join(query), '')
            context.update({
                'youtube_url': urlunparse(parts),
                'allowfullscreen': 'allowfullscreen' if instance.glossary.get('allow_fullscreen') else '',
            })
        return context

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapYoutubePlugin, cls).get_css_classes(obj)
        css_classes.append('embed-responsive')
        css_class = obj.glossary.get('aspect_ratio')
        if css_class:
            css_classes.append(css_class)
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        return obj.glossary.get('videoid', '')

plugin_pool.register_plugin(BootstrapYoutubePlugin)
