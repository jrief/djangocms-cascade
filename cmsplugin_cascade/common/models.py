# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield.fields import JSONField


class SharedGlossary(models.Model):
    """
    A model class to hold glossary data shared among different plugins.
    """
    class Meta:
        app_label = 'cmsplugin_cascade'

    plugin_type = models.CharField('plugin_name', max_length=50, db_index=True, editable=False)
    identifier = models.CharField(_("Identifier"), max_length=50, unique=True)
    glossary = JSONField(null=True, blank=True, default={})

    def __str__(self):
        return self.identifier
