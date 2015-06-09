# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from jsonfield.fields import JSONField
from cms.utils.compat.dj import python_2_unicode_compatible
from .models_base import CascadeModelBase


@python_2_unicode_compatible
class SharedGlossary(models.Model):
    """
    A model class to hold glossary data shared among different plugins.
    """
    plugin_type = models.CharField(_("Plugin Name"), max_length=50, db_index=True, editable=False)
    identifier = models.CharField(_("Identifier"), max_length=50, unique=True)
    glossary = JSONField(null=True, blank=True, default={})

    class Meta:
        app_label = 'cmsplugin_cascade'
        unique_together = ('plugin_type', 'identifier')
        verbose_name_plural = verbose_name = _("Shared between Plugins")

    def __str__(self):
        return self.identifier


class CascadeElement(CascadeModelBase):
    """
    The concrete model class to store arbitrary data for plugins derived from CascadePluginBase.
    """
    class Meta:
        app_label = 'cmsplugin_cascade'
        db_table = 'cmsplugin_cascade_element'

    def copy_relations(self, oldinstance):
        for inline_element in oldinstance.inline_elements.all():
            inline_element.pk = None
            inline_element.cascade_element = self
            inline_element.save()


class SharableCascadeElement(CascadeModelBase):
    """
    A model class with an additional foreign key to a shared glossary.
    """
    shared_glossary = models.ForeignKey(SharedGlossary, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'cmsplugin_cascade'
        db_table = 'cmsplugin_cascade_sharableelement'

    def __getattribute__(self, name):
        """
        Update glossary with content from SharedGlossary model if that exists.
        """
        attribute = object.__getattribute__(self, name)
        if name == 'glossary' and self.shared_glossary:
            attribute.update(self.shared_glossary.glossary)
        return attribute


class InlineCascadeElement(models.Model):
    """
    A model class to store an inline model for a CascadeElement.
    """
    cascade_element = models.ForeignKey(CascadeElement, related_name='inline_elements')
    glossary = JSONField(blank=True, default={})

    class Meta:
        app_label = 'cmsplugin_cascade'
        db_table = 'cmsplugin_cascade_inline'


class PluginExtraFields(models.Model):
    """
    Store a set of allowed extra CSS classes and inline styles to be used for Cascade plugins
    inheriting from `ExtraFieldsMixin`. Also store if individual ``id=""`` tags are allowed.
    """
    plugin_type = models.CharField(_("Plugin Name"), max_length=50, db_index=True)
    site = models.ForeignKey(Site, verbose_name=_("Site"))
    allow_id_tag = models.BooleanField(default=False)
    css_classes = JSONField(null=True, blank=True, default={})
    inline_styles = JSONField(null=True, blank=True, default={})

    class Meta:
        app_label = 'cmsplugin_cascade'
        verbose_name = verbose_name_plural = _("Custom CSS classes and styles")
        unique_together = ('plugin_type', 'site')


class Segmentation(models.Model):
    class Meta:
        app_label = 'cmsplugin_cascade'
        verbose_name = verbose_name_plural = _("Segmentation")
        managed = False  # its a dummy model
