# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from filer.fields.image import FilerImageField
from cmsplugin_cascade.link.models_base import LinkElementBase
from cmsplugin_cascade.common.models import SharedGlossary


class ImageElement(LinkElementBase):
    """
    A model class to refer to a Django-Filer image together with the cascade glossary and an optional Link.
    """
    class Meta:
        app_label = 'cmsplugin_cascade'

    image = FilerImageField(null=True, blank=True, default=None, verbose_name=_("Image"))
    shared_glossary = models.ForeignKey(SharedGlossary, blank=True, null=True, on_delete=models.SET_NULL)
