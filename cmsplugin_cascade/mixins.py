# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.fields import PartialFormField
from .widgets import MultipleCascadingSizeWidget


class ExtraFieldsMixin(object):
    """
    This mixin class shall be added to plugins which shall offer extra fields for customizes
    CSS classes and styles.
    """
    EXTRA_INLINE_STYLES = ('margin', 'padding', 'width', 'height',)

    def __init__(self, model=None, admin_site=None, **kwargs):
        from cmsplugin_cascade.models import PluginExtraFields

        super(ExtraFieldsMixin, self).__init__(model=model, admin_site=admin_site, **kwargs)
        self.glossary_fields = list(self.glossary_fields)
        try:
            site = Site.objects.get_current()
            extra_fields = PluginExtraFields.objects.get(plugin_type=self.__class__.__name__, site=site)
        except ObjectDoesNotExist:
            pass
        else:
            # add a select box to let the user choose one or more CSS classes
            choices = [(clsname, clsname) for clsname in extra_fields.css_classes.get('class_names', '').replace(' ', '').split(',')]
            if extra_fields.css_classes.get('multiple'):
                widget = widgets.SelectMultiple(choices=choices)
            else:
                widget = widgets.Select(choices=((None, _("Select CSS")),) + choices)
            self.glossary_fields.append(PartialFormField('extra_css_classes',
                widget,
                label=_("Customized CSS Classes"),
                help_text=_("Customized CSS classes to be added to this element.")
            ))
            # add input fields to let the user enter styling information
            for style in self.EXTRA_INLINE_STYLES:
                inline_styles = extra_fields.inline_styles.get('extra_fields:{0}'.format(style))
                if inline_styles:
                    allowed_units = extra_fields.inline_styles.get('extra_units:{0}'.format(style)).split(',')
                    widget = MultipleCascadingSizeWidget(inline_styles, allowed_units=allowed_units, required=False)
                    key = 'extra_inline_styles:{0}'.format(style)
                    label = style.capitalize()
                    self.glossary_fields.append(PartialFormField(key, widget, label=label))

    @classmethod
    def get_css_classes(cls, obj):
        """Enrich list of CSS classes with customized ones"""
        css_classes = super(ExtraFieldsMixin, cls).get_css_classes(obj)
        css_classes.extend(obj.glossary.get('extra_css_classes', []))
        return css_classes

    @classmethod
    def get_inline_styles(cls, obj):
        """Enrich inline CSS styles with customized ones"""
        inline_styles = super(ExtraFieldsMixin, cls).get_inline_styles(obj)
        for key, eis in obj.glossary.items():
            if key.startswith('extra_inline_styles:'):
                inline_styles.update(dict((k, v) for k, v in eis.items() if v))
        return inline_styles
