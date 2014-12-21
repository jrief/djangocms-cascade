# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.utils.encoding import force_text
from jsonfield.fields import JSONField
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.sharable.models import SharedGlossary
from .models_base import CascadeModelBase
from .mixins import ExtraFieldsMixin


class CascadeElement(CascadeModelBase):
    class Meta:
        app_label = 'cmsplugin_cascade'
        db_table = 'cmsplugin_cascade_element'


class SharableCascadeElement(CascadeModelBase):
    """
    A model class with an additional foreign key to a shared glossary.
    """
    class Meta:
        app_label = 'cmsplugin_cascade'
        db_table = 'cmsplugin_cascade_sharableelement'

    shared_glossary = models.ForeignKey(SharedGlossary, blank=True, null=True, on_delete=models.SET_NULL)

    def __getattribute__(self, name):
        """
        Update glossary with content from SharedGlossary model if that exists.
        """
        attribute = object.__getattribute__(self, name)
        if name == 'glossary' and self.shared_glossary:
            attribute.update(self.shared_glossary.glossary)
        return attribute


def _plugins_for_site():
    cascade_plugins = set([p for p in plugin_pool.get_all_plugins() if issubclass(p, ExtraFieldsMixin)])
    return [(p.__name__, '{0} {1}'.format(force_text(p.module), force_text(p.name))) for p in cascade_plugins]


class PluginExtraFields(models.Model):
    class Meta:
        app_label = 'cmsplugin_cascade'
        verbose_name = verbose_name_plural = _("Custom CSS classes and styles")
        unique_together = ('plugin_type', 'site')

    CUSTOMIZABLE_PLUGINS = _plugins_for_site()
    plugin_type = models.CharField(_("Plugin Name"), max_length=50, db_index=True, choices=CUSTOMIZABLE_PLUGINS)
    site = models.ForeignKey(Site, verbose_name=_("Site"))
    allow_id_tag = models.BooleanField(default=False)
    css_classes = JSONField(null=True, blank=True, default={})
    inline_styles = JSONField(null=True, blank=True, default={})
