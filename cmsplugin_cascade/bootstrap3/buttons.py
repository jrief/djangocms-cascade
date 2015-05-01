# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.forms.widgets import RadioFieldRenderer
from django.utils.html import format_html, format_html_join
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.link.forms import TextLinkForm
from cmsplugin_cascade.link.plugin_base import LinkPluginBase, LinkElementMixin
from cmsplugin_cascade.utils import resolve_dependencies


class ButtonTypeRenderer(RadioFieldRenderer):
    """
    Render sample buttons in different colors in the button's backend editor.
    """
    BUTTON_TYPES = SortedDict((('btn-default', _('Default')), ('btn-primary', _('Primary')),
        ('btn-success', _('Success')), ('btn-info', _('Info')), ('btn-warning', _('Warning')),
        ('btn-danger', _('Danger')), ('btn-link', _('Link')),))

    @classmethod
    def get_widget(cls):
        choices = tuple((k, v) for k, v in cls.BUTTON_TYPES.items())
        return widgets.RadioSelect(choices=choices, renderer=cls)

    def render(self):
        return format_html('<div class="form-row">{}</div>',
            format_html_join('\n', '<div class="field-box">'
                             '<span class="btn {1}">{2}</span>'
                             '<div class="label">{0}</div></div>',
                ((force_text(w), w.choice_value, force_text(self.BUTTON_TYPES[w.choice_value])) for w in self)
            ))


class ButtonSizeRenderer(RadioFieldRenderer):
    """
    Render sample buttons in different sizes in the button's backend editor.
    """
    BUTTON_SIZES = SortedDict((('btn-lg', _('Large')), ('', _('Default')), ('btn-sm', _('Small')),
        ('btn-xs', _('Extra small')),))

    @classmethod
    def get_widget(cls):
        choices = tuple((k, v) for k, v in cls.BUTTON_SIZES.items())
        return widgets.RadioSelect(choices=choices, renderer=cls)

    def render(self):
        return format_html('<div class="form-row">{}</div>',
            format_html_join('\n',
                '<div class="field-box"><div class="button-samples">'
                    '<span class="btn btn-primary {1}">{2}</span>'
                    '<span class="btn btn-default {1}">{2}</span></div>'
                    '<div class="label">{0}</div>'
                '</div>',
                ((force_text(w), w.choice_value, force_text(self.BUTTON_SIZES[w.choice_value])) for w in self)
            ))


class ButtonIconRenderer(RadioFieldRenderer):
    """
    This render has been prepared to prefix and append icons to the button.
    Currently one has to enter text into the fields `icon-left` and `icon-right`.
    """
    GLYPH_ICONS = (
        '', 'asterisk', 'plus', 'euro', 'eur', 'minus', 'cloud', 'envelope', 'pencil', 'glass', 'music',
        'search', 'heart', 'star', 'star-empty', 'user', 'film', 'th-large', 'th', 'th-list', 'ok',
        'remove', 'zoom-in', 'zoom-out', 'off', 'signal', 'cog', 'trash', 'home', 'file', 'time',
        'road', 'download-alt', 'download', 'upload', 'inbox', 'play-circle', 'repeat', 'refresh',
        'list-alt', 'lock', 'flag', 'headphones', 'volume-off', 'volume-down', 'volume-up', 'qrcode',
        'barcode', 'tag', 'tags', 'book', 'bookmark', 'print', 'camera', 'font', 'bold', 'italic',
        'text-height', 'text-width', 'align-left', 'align-center', 'align-right', 'align-justify',
        'list', 'indent-left', 'indent-right', 'facetime-video', 'picture', 'map-marker', 'adjust',
        'tint', 'edit', 'share', 'check', 'move', 'step-backward', 'fast-backward', 'backward',
        'play', 'pause', 'stop', 'forward', 'fast-forward', 'step-forward', 'eject', 'chevron-left',
        'chevron-right', 'plus-sign', 'minus-sign', 'remove-sign', 'ok-sign', 'question-sign',
        'info-sign', 'screenshot', 'remove-circle', 'ok-circle', 'ban-circle', 'arrow-left',
        'arrow-right', 'arrow-up', 'arrow-down', 'share-alt', 'resize-full', 'resize-small',
        'exclamation-sign', 'gift', 'leaf', 'fire', 'eye-open', 'eye-close', 'warning-sign', 'plane',
        'calendar', 'random', 'comment', 'magnet', 'chevron-up', 'chevron-down', 'retweet',
        'shopping-cart', 'folder-close', 'folder-open', 'resize-vertical', 'resize-horizontal', 'hdd',
        'bullhorn', 'bell', 'certificate', 'thumbs-up', 'thumbs-down', 'hand-right', 'hand-left',
        'hand-up', 'hand-down', 'circle-arrow-right', 'circle-arrow-left', 'circle-arrow-up',
        'circle-arrow-down', 'globe', 'wrench', 'tasks', 'filter', 'briefcase', 'fullscreen',
        'dashboard', 'paperclip', 'heart-empty', 'link', 'phone', 'pushpin', 'usd', 'gbp', 'sort',
        'sort-by-alphabet', 'sort-by-alphabet-alt', 'sort-by-order', 'sort-by-order-alt',
        'sort-by-attributes', 'sort-by-attributes-alt', 'unchecked', 'expand', 'collapse-down',
        'collapse-up', 'log-in', 'flash', 'log-out', 'new-window', 'record', 'save', 'open', 'saved',
        'import', 'export', 'send', 'floppy-disk', 'floppy-saved', 'floppy-remove', 'floppy-save',
        'floppy-open', 'credit-card', 'transfer', 'cutlery', 'header', 'compressed', 'earphone',
        'phone-alt', 'tower', 'stats', 'sd-video', 'hd-video', 'subtitles', 'sound-stereo',
        'sound-dolby', 'copyright-mark', 'registration-mark', 'cloud-download', 'cloud-upload',
        'tree-conifer', 'tree-deciduous', 'cd', 'save-file', 'open-file', 'level-up', 'copy', 'paste',
        'alert', 'equalizer', 'king', 'queen', 'pawn', 'bishop', 'knight', 'baby-formula', 'tent',
        'blackboard', 'bed', 'apple', 'erase', 'hourglass', 'lamp', 'duplicate', 'piggy-bank',
        'scissors', 'bitcoin', 'btc', 'xbt', 'yen', 'jpy', 'ruble', 'rub', 'scale', 'ice-lolly',
        'ice-lolly-tasted', 'education', 'option-horizontal', 'option-vertical', 'menu-hamburger',
        'modal-window', 'oil', 'grain', 'sunglasses', 'text-size', 'text-color', 'text-background',
        'object-align-top', 'object-align-bottom', 'object-align-horizontal', 'object-align-left',
        'object-align-vertical', 'object-align-right', 'triangle-right', 'triangle-left',
        'triangle-bottom', 'triangle-top', 'console', 'superscript', 'subscript', 'menu-left',
        'menu-right', 'menu-down', 'menu-up',
    )

    @classmethod
    def get_widget(cls):
        choices = tuple((k, k) for k in cls.GLYPH_ICONS)
        return widgets.RadioSelect(choices=choices, renderer=cls)

    def render(self):
        return format_html(
            '<div class="form-row">'
            '<div class="field-box"><div class="label" title="No icon">{0}'
            '<span class="glyphicon glyphicon-minus" style="color: transparent;"></span>'
            '</div></div>{1}</div>',
            self[0].tag(),
            format_html_join('\n',
                '<div class="field-box">'
                    '<div class="label" title="{1}">{0}<span class="glyphicon glyphicon-{1}"></span></div>'
                '</div>',
                [(w.tag(), w.choice_value,) for w in self][1:]
            ))


class BootstrapButtonMixin(object):
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    render_template = 'cascade/bootstrap3/button.html'
    allow_children = False
    text_enabled = True
    tag_type = None
    default_css_class = 'btn'
    default_css_attributes = ('button-type', 'button-size', 'button-options', 'quick-float',)

    glossary_fields = (
        PartialFormField('button-type',
            ButtonTypeRenderer.get_widget(),
            label=_("Button Type"),
            initial='btn-default',
            help_text=_("Display Link using this Button Style")
        ),
        PartialFormField('button-size',
            ButtonSizeRenderer.get_widget(),
            label=_("Button Size"),
            initial='',
            help_text=_("Display Link using this Button Size")
        ),
        PartialFormField('button-options',
            widgets.CheckboxSelectMultiple(choices=(('btn-block', _('Block level')), ('disabled', _('Disabled')),)),
            label=_("Button Options"),
        ),
        PartialFormField('quick-float',
            widgets.RadioSelect(choices=(('', _("Do not float")), ('pull-left', _("Pull left")), ('pull-right', _("Pull right")),)),
            label=_("Quick Float"),
            initial='',
            help_text=_("Float the button to the left or right.")
        ),
        PartialFormField('icon-left',
            ButtonIconRenderer.get_widget(),
            label=_("Prepend icon"),
            initial='',
            help_text=_("Prepend a Glyphicon before the content.")
        ),
        PartialFormField('icon-right',
            ButtonIconRenderer.get_widget(),
            label=_("Append icon"),
            initial='',
            help_text=_("Append a Glyphicon after the content.")
        ),
    )

    def render(self, context, instance, placeholder):
        context = super(BootstrapButtonMixin, self).render(context, instance, placeholder)
        mini_template = '<span class="glyphicon glyphicon-{}" aria-hidden="true"></span>&nbsp;'
        icon_left = instance.glossary.get('icon-left')
        if icon_left:
            context['icon_left'] = format_html(mini_template, icon_left)
        icon_right = instance.glossary.get('icon-right')
        if icon_right:
            context['icon_right'] = format_html(mini_template, icon_right)
        return context


class BootstrapButtonPlugin(BootstrapButtonMixin, LinkPluginBase):
    module = 'Bootstrap'
    name = _("Button")
    form = TextLinkForm
    model_mixins = (LinkElementMixin,)
    fields = ('link_content', ('link_type', 'cms_page', 'ext_url', 'mail_to'), 'glossary',)
    glossary_fields = BootstrapButtonMixin.glossary_fields + LinkPluginBase.glossary_fields

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css', 'cascade/css/admin/bootstrap-theme.min.css',)}
        js = resolve_dependencies('cascade/js/admin/linkplugin.js')

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapButtonPlugin, cls).get_identifier(obj)
        content = obj.glossary.get('link_content')
        if not content:
            try:
                content = force_text(ButtonTypeRenderer.BUTTON_TYPES[obj.glossary['button-type']])
            except KeyError:
                content = _("Empty")
        return format_html('{}{}', identifier, content)

plugin_pool.register_plugin(BootstrapButtonPlugin)
