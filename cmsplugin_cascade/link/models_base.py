# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from cms.models import Page
from cmsplugin_cascade.models import CascadeModelBase


class LinkElementBase(CascadeModelBase):
    class Meta:
        abstract = True

    page_link = models.ForeignKey(Page, verbose_name=_("Internal Page"), blank=True, null=True,
                    help_text=_("An internal link for this site"), on_delete=models.SET_NULL)
    text_link = models.CharField(max_length=255, blank=True, null=True)
