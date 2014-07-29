# -*- coding: utf-8 -*-
import six
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.plugin_base import CascadePluginBase


class LinkPluginBase(CascadePluginBase):
    require_parent = True
    glossary_fields = (
        PartialFormField('target',
            widgets.RadioSelect(choices=(('', _("Same Window")), ('_blank', _("New Window")),
                         ('_parent', _("Parent Window")), ('_top', _("Topmost Frame")),)),
            initial='',
            label=_('Link Target'),
            help_text=_("Open Link in other target.")
        ),
    )
    html_tag_attributes = {'target': 'target'}

    class Media:
        js = ['cms/js/libs/jquery.min.js']

    @classmethod
    def get_identifier(cls, model):
        """
        Returns the descriptive name for the current model
        """
        # TODO: return the line name
        return six.u('')
