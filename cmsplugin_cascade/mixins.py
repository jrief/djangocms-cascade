# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.fields import PartialFormField


class ExtraFieldsMixin(object):
    """
    This mixin class shall be added to plugins which shall offer extra fields for customizes
    CSS classes and styles.
    """

    def __init__(self, model=None, admin_site=None, **kwargs):
        super(ExtraFieldsMixin, self).__init__(model=model, admin_site=admin_site, **kwargs)
        self.glossary_fields = list(self.glossary_fields)
        if model and admin_site:
            partial_form_field = self._get_css_extra_field(model)
            if partial_form_field:
                print len(self.glossary_fields), self.__class__.__name__, partial_form_field.name
                self.glossary_fields.append(partial_form_field)
        pass

    def _get_css_extra_field(self, model):
        from cmsplugin_cascade.models import PluginExtraFields
        try:
            site = Site.objects.get_current()
            extra_fields = PluginExtraFields.objects.select_related('css_class').get(plugin_type=self.__class__.__name__, site=site)
        except ObjectDoesNotExist:
            pass
        else:
            choices = tuple((c.css_class, c.css_class) for c in extra_fields.pluginextraclasses_set.all())
            if extra_fields.multiple_css:
                widget = widgets.SelectMultiple(choices=choices)
            else:
                widget = widgets.Select(choices=((None, _("Select CSS")),) + choices)
            return PartialFormField('custom_css_classes',
                widget,
                label=_("Customized CSS Classes"),
                help_text=_("Customized CSS classes to be added to this element.")
            )
