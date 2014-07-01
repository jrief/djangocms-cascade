# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from cms.models import Page
from cmsplugin_cascade.models import CascadeModelBase


class LinkElementBase(CascadeModelBase):
    class Meta:
        abstract = True

    page_link = models.ForeignKey(Page, blank=True, null=True, on_delete=models.SET_NULL,
                    help_text=_("An internal link for this site"))
    text_link = models.CharField(max_length=255, blank=True, null=True)

    @property
    def link(self):
        if self.page_link:
            return self.page_link.get_absolute_url()
        else:
            return self.text_link

    @property
    def name(self):
        return self.glossary.get('link_content', '')
