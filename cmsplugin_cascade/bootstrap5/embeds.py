import random
import re
import string
from urllib.parse import urlparse, urlunparse, ParseResult

from django.core.exceptions import ValidationError
from django.forms import widgets
from django.forms.fields import BooleanField, ChoiceField, URLField, CharField
from django.utils.translation import gettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap5.mixins import VerticalMarginsMixin
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.models import CascadeElement

from formset.forms import ModelForm


class YoutubeForm(ModelForm):
    ASPECT_RATIO_CHOICES = [
        ('ratio-21x9', _("Responsive 21:9")),
        ('ratio-16x9', _("Responsive 16:9")),
        ('ratio-4x3', _("Responsive 4:3")),
        ('ratio-1x1', _("Responsive 1:1")),
    ]

    videoid = CharField(
        required=False,
        widget=widgets.HiddenInput(),
    )
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
        help_text=_("Show videos suggested by YouTube at the end."),
    )
    field_order = ['url', 'aspect_ratio', 'autoplay', 'controls', 'loop', 'rel']

    class Meta:
        model = CascadeElement
        exclude = ['shared_glossary']
        fields_map = {'glossary': [
            'videoid', 'aspect_ratio', 'allow_fullscreen', 'autoplay', 'controls', 'loop', 'rel'
        ]}

    def get_initial_for_field(self, field, field_name):
        if field_name == 'url':
            videoid = self.instance.glossary.get('videoid', 'X')
            return urlunparse(ParseResult('https', 'youtu.be', videoid, '', '', ''))
        return super().get_initial_for_field(field, field_name)

    def clean(self):
        cleaned_data = super().clean()
        if url := cleaned_data.get('url'):
            parts = urlparse(url)
            if match := re.search(r'^v=([^&]+)', parts.query):
                cleaned_data['videoid'] = match.group(1)
                return cleaned_data
            if match := re.search(r'([^/]+)$', parts.path):
                cleaned_data['videoid'] = match.group(1)
                return cleaned_data
        raise ValidationError(_("Please enter a valid YouTube URL"))


class BootstrapYoutubePlugin(VerticalMarginsMixin, BootstrapPluginBase):
    """
    Use this plugin to embed a YouTube video into a Bootstrap column.
    """

    name = "YouTube"
    parent_classes = ['BootstrapColumnPlugin']
    render_template = 'cascade/bootstrap5/youtube.html'
    form = YoutubeForm

    def render(self, context, instance, placeholder):
        context = self.super(BootstrapYoutubePlugin, self).render(context, instance, placeholder)
        query_params = ['autoplay', 'controls', 'loop', 'rel']
        if videoid := instance.glossary.get('videoid'):
            tracking_id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
            parts = ParseResult('https', 'www.youtube.com', '/embed/' + videoid, '', f'si={tracking_id}', '')
            context.update({
                'youtube_url': urlunparse(parts),
                'allow': '; '.join(key for key in query_params if instance.glossary.get(key)),
                'allowfullscreen': 'allowfullscreen' if instance.glossary.get('allow_fullscreen') else '',
            })
        return context

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapYoutubePlugin, cls).get_css_classes(obj)
        css_classes.append('ratio')
        css_class = obj.glossary.get('aspect_ratio')
        if css_class:
            css_classes.append(css_class)
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        return obj.glossary.get('videoid', '')


plugin_pool.register_plugin(BootstrapYoutubePlugin)
