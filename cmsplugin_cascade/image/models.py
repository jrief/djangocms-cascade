# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from filer.fields.image import FilerImageField
from cmsplugin_cascade.link.models_base import LinkElementBase


class ImageElement(LinkElementBase):
    """
    A model class to refer to a Django-Filer image together with the cascade glossary and an optional Link.
    """
    class Meta:
        app_label = 'cmsplugin_cascade'

    image = FilerImageField(null=True, blank=True, default=None, verbose_name=_("Image"))

    def save(self, *args, **kwargs):
        self.plugin_class.resize_image(self)
        super(ImageElement, self).save(*args, **kwargs)

    def refresh_children(self):
        self.save(no_signals=True)
        super(ImageElement, self).refresh_children()
