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
            self.glossary_fields.append(PartialFormField('custom_css_classes',
                widget,
                label=_("Customized CSS Classes"),
                help_text=_("Customized CSS classes to be added to this element.")
            ))
            # add input fields to let the user enter styling information
            for style in ('margin', 'padding',):
                inline_styles = extra_fields.inline_styles.get('{0}-fields'.format(style))
                if inline_styles:
                    allowed_units = extra_fields.inline_styles.get('{0}-units'.format(style)).split(',')
                    widget = MultipleCascadingSizeWidget(inline_styles, allowed_units=allowed_units)
                    self.glossary_fields.append(PartialFormField(style, widget, label=style.capitalize()))
