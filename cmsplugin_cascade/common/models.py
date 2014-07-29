# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from jsonfield.fields import JSONField
from cmsplugin_cascade.models_base import CascadeModelBase


@python_2_unicode_compatible
class SharedGlossary(models.Model):
    """
    A model class to hold glossary data shared among different plugins.
    """
    class Meta:
        app_label = 'cmsplugin_cascade'
        unique_together = ('plugin_type', 'identifier')

    plugin_type = models.CharField('plugin_name', max_length=50, db_index=True, editable=False)
    identifier = models.CharField(_("Identifier"), max_length=50, unique=True)
    glossary = JSONField(null=True, blank=True, default={})

    def __str__(self):
        return self.identifier


class SharableCascadeElement(CascadeModelBase):
    """
    A model class to refer to a Django-Filer image together with the cascade glossary and an optional Link.
    """
    class Meta:
        app_label = 'cmsplugin_cascade'

    shared_glossary = models.ForeignKey(SharedGlossary, blank=True, null=True, on_delete=models.SET_NULL)
