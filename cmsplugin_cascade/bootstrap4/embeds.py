# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from django.core.exceptions import ValidationError
from django.forms import widgets, URLField
from django.forms.models import ModelForm
from django.utils.html import format_html
from django.utils.six.moves.urllib.parse import urlparse, urlunparse, ParseResult
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.bootstrap4.plugin_base import BootstrapPluginBase


ASPECT_RATIO_CHOICES = [
    ('embed-responsive-21by9', _("Responsive 21:9")),
    ('embed-responsive-16by9', _("Responsive 16:9")),
    ('embed-responsive-4by3', _("Responsive 4:3")),
    ('embed-responsive-1by1', _("Responsive 1:1")),
]


class BootstrapYoutubeForm(ModelForm):
    url = URLField(
        label=_("YouTube URL"),
        widget=widgets.URLInput(attrs={'size': 50}),
    )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            videoid = instance.glossary.get('videoid')
            if videoid:
                parts = ParseResult('https', 'youtu.be', videoid, '', '', '')
                initial = {'url': urlunparse(parts)}
                kwargs.update(initial=initial)
        super(BootstrapYoutubeForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(BootstrapYoutubeForm, self).clean()
        url = cleaned_data.pop('url', None)
        if url:
            parts = urlparse(url)
            match = re.search(r'([^/]+)$', parts.path)
            if match:
                cleaned_data['glossary']['videoid'] = match.group(0)
                return cleaned_data
        raise ValidationError(_("Please enter a valid YouTube URL"))


class BootstrapYoutubePlugin(BootstrapPluginBase):
    """
    Use this plugin to display a YouTube video.
    """
    name = _("Youtube")
    require_parent = False
    parent_classes = ['BootstrapColumnPlugin']
    child_classes = None
    form = BootstrapYoutubeForm
    render_template = 'cascade/bootstrap4/youtube.html'
    fields = ['url', 'glossary']

    aspect_ratio = GlossaryField(
        widgets.RadioSelect(choices=ASPECT_RATIO_CHOICES),
        label=_("Aspect Ratio"),
        initial=ASPECT_RATIO_CHOICES[1][0],
    )

    allow_fullscreen = GlossaryField(
        widgets.CheckboxInput(),
        label=_("Allow Fullscreen"),
        initial='on',
    )

    autoplay = GlossaryField(
        widgets.CheckboxInput(),
        label=_("Autoplay"),
    )

    controls = GlossaryField(
        widgets.CheckboxInput(),
        label=_("Display Controls"),
    )

    loop = GlossaryField(
        widgets.CheckboxInput(),
        label=_("Enable Looping"),
    )

    rel = GlossaryField(
        widgets.CheckboxInput(),
        label=_("Show related"),
    )

    def render(self, context, instance, placeholder):
        query_params = ['autoplay', 'controls', 'loop', 'rel']
        videoid = instance.glossary.get('videoid')
        if videoid:
            query = ['{}=1'.format(key) for key in query_params if instance.glossary.get(key)]
            parts = ParseResult('https', 'www.youtube.com', '/embed/' + videoid, '', '&'.join(query), '')
            context.update({
                'instance': instance,
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
        identifier = super(BootstrapYoutubePlugin, cls).get_identifier(obj)
        videoid = obj.glossary.get('videoid', '')
        return format_html('{0}/{1}', identifier, videoid)

plugin_pool.register_plugin(BootstrapYoutubePlugin)
