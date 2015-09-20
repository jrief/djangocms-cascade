# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.forms.widgets import RadioFieldRenderer
from django.utils.html import format_html, format_html_join


class GlyphiconRenderer(RadioFieldRenderer):
    """
    This render has been prepared to prefix and append icons to the button.
    Currently one has to enter text into the fields `icon-left` and `icon-right`.
    """
    GLYPHICONS = (
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
        choices = tuple((k, k) for k in cls.GLYPHICONS)
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
