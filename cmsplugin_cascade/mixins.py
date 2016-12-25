# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
    from django.contrib.sites.shortcuts import get_current_site
except ImportError:
    from django.contrib.sites.models import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps
from django.utils.encoding import python_2_unicode_compatible

from cmsplugin_cascade.models import InlineCascadeElement, SortableInlineCascadeElement


@python_2_unicode_compatible
class ImagePropertyMixin(object):
    """
    A mixin class to convert a CascadeElement into a proxy model for rendering an image element.
    """
    def __str__(self):
        try:
            return self.plugin_class.get_identifier(self)
        except AttributeError:
            return str(self.image)

    @property
    def image(self):
        if not hasattr(self, '_image_model'):
            try:
                Model = apps.get_model(*self.glossary['image']['model'].split('.'))
                self._image_model = Model.objects.get(pk=self.glossary['image']['pk'])
            except (KeyError, ObjectDoesNotExist):
                self._image_model = None
        return self._image_model


class WithInlineElementsMixin(object):
    """
    Plugins wishing to allow child elements as inlines, shall inherit from this
    mixin class, in order to override the serialize and deserialize methods.
    """
    @classmethod
    def get_data_representation(cls, instance):
        inlines = [ie.glossary for ie in instance.inline_elements.all()]
        return {'glossary': instance.glossary, 'inlines': inlines}

    @classmethod
    def add_inline_elements(cls, instance, inlines):
        for inline_glossary in inlines:
            InlineCascadeElement.objects.create(
                cascade_element=instance, glossary=inline_glossary)


class WithSortableInlineElementsMixin(object):
    """
    Plugins wishing to allow child elements as sortable inlines, shall inherit from this
    mixin class, in order to override the serialize and deserialize methods.
    """
    @classmethod
    def get_data_representation(cls, instance):
        inlines = [ie.glossary for ie in instance.sortinline_elements.all()]
        return {'glossary': instance.glossary, 'inlines': inlines}

    @classmethod
    def add_inline_elements(cls, instance, inlines):
        for order, inline_glossary in enumerate(inlines, 1):
            SortableInlineCascadeElement.objects.create(
                cascade_element=instance, glossary=inline_glossary, order=order)
