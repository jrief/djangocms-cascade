# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from jsonfield.fields import JSONField
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
        unique_together = ('plugin_type', 'identifier')
        verbose_name_plural = verbose_name = _("Shared between Plugins")

    def __str__(self):
        return self.identifier


class CascadeElement(CascadeModelBase):
    """
    The concrete model class to store arbitrary data for plugins derived from CascadePluginBase.
    """
    class Meta:
        db_table = 'cmsplugin_cascade_element'

    def copy_relations(self, oldinstance):
        def init_element(inline_element):
            inline_element.pk = None
            inline_element.cascade_element = self
            inline_element.save()

        for inline_element in oldinstance.inline_elements.all():
            init_element(inline_element)
        for sortinline_element in oldinstance.sortinline_elements.all():
            init_element(sortinline_element)


class SharableCascadeElement(CascadeModelBase):
    """
    A model class with an additional foreign key to a shared glossary.
    """
    shared_glossary = models.ForeignKey(SharedGlossary, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'cmsplugin_cascade_sharableelement'

    def __getattribute__(self, name):
        """
        Update glossary with content from SharedGlossary model if that exists.
        """
        attribute = object.__getattribute__(self, name)
        if name == 'glossary' and self.shared_glossary:
            attribute.update(self.shared_glossary.glossary)
        return attribute

    def get_data_representation(self):
        # TODO: merge with shared_glossary
        return {'glossary': self.glossary}


class InlineCascadeElement(models.Model):
    cascade_element = models.ForeignKey(CascadeElement, related_name='inline_elements')
    glossary = JSONField(blank=True, default={})

    class Meta:
        db_table = 'cmsplugin_cascade_inline'


class SortableInlineCascadeElement(models.Model):
    cascade_element = models.ForeignKey(CascadeElement, related_name='sortinline_elements')
    glossary = JSONField(blank=True, default={})
    order = models.PositiveIntegerField(verbose_name=_("Sort by"), db_index=True)

    class Meta:
        db_table = 'cmsplugin_cascade_sortinline'
        ordering = ('order',)

    def __str__(self):
        return ""


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
        verbose_name = verbose_name_plural = _("Custom CSS classes and styles")
        unique_together = ('plugin_type', 'site')


class Segmentation(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = _("Segmentation")
        managed = False  # its a dummy model
        db_table = None


@python_2_unicode_compatible
class CascadeClipboard(models.Model):
    """
    A model class to persist, export and re-import the clipboard's content.
    """
    identifier = models.CharField(_("Identifier"), max_length=50, unique=True)
    data = JSONField(null=True, blank=True, default={})

    class Meta:
        verbose_name_plural = verbose_name = _("Persited Clipboard Content")

    def __str__(self):
        return self.identifier
