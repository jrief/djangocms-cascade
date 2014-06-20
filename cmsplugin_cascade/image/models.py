# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from filer.fields.image import FilerImageField
from cmsplugin_cascade.link.models_base import LinkElementBase


class ImageElement(LinkElementBase):
    """
    A model class to refer to a Django-Filer images, adding an optional Link and arbitrary context
    data.
    """
    class Meta:
        app_label = 'cmsplugin_cascade'

    image = FilerImageField(null=True, blank=True, default=None, verbose_name=_("Image"))
