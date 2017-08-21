# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
    from django.contrib.sites.shortcuts import get_current_site
except ImportError:
    from django.contrib.sites.models import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps
from django.utils.encoding import python_2_unicode_compatible
from django.utils import six

from cmsplugin_cascade.models import InlineCascadeElement, SortableInlineCascadeElement


class CascadePluginMixin(object):
    """
    This is the common mixin class used for both, the :class:`cmsplugin_cascade.plugin_base.CascadePluginBase`
    and the :class:`cmsplugin_cascade.strides.StridePluginBase`.
    """

    @classmethod
    def get_tag_type(self, instance):
        """
        Return the tag_type used to render this plugin.
        """
        return instance.glossary.get('tag_type', getattr(self, 'tag_type', 'div'))

    @classmethod
    def get_css_classes(cls, instance):
        """
        Returns a list of CSS classes to be added as class="..." to the current HTML tag.
        """
        css_classes = []
        if hasattr(cls, 'default_css_class'):
            css_classes.append(cls.default_css_class)
        for attr in getattr(cls, 'default_css_attributes', []):
            css_class = instance.glossary.get(attr)
            if isinstance(css_class, six.string_types):
                css_classes.append(css_class)
            elif isinstance(css_class, list):
                css_classes.extend(css_class)
        return css_classes

    @classmethod
    def get_inline_styles(cls, instance):
        """
        Returns a dictionary of CSS attributes to be added as style="..." to the current HTML tag.
        """
        inline_styles = getattr(cls, 'default_inline_styles', {})
        css_style = instance.glossary.get('inline_styles')
        if css_style:
            inline_styles.update(css_style)
        return inline_styles

    @classmethod
    def get_html_tag_attributes(cls, instance):
        """
        Returns a dictionary of attributes, which shall be added to the current HTML tag.
        This method normally is called by the models's property method ``html_tag_ attributes``,
        which enriches the HTML tag with those attributes converted to a list as
        ``attr1="val1" attr2="val2" ...``.
        """
        attributes = getattr(cls, 'html_tag_attributes', {})
        return dict((attr, instance.glossary.get(key, '')) for key, attr in attributes.items())


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
        data = super(WithInlineElementsMixin, cls).get_data_representation(instance)
        data.update(inlines=[ie.glossary for ie in instance.inline_elements.all()])
        return data

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
        data = super(WithSortableInlineElementsMixin, cls).get_data_representation(instance)
        data.update(inlines=[ie.glossary for ie in instance.sortinline_elements.all()])
        return data

    @classmethod
    def add_inline_elements(cls, instance, inlines):
        for order, inline_glossary in enumerate(inlines, 1):
            SortableInlineCascadeElement.objects.create(
                cascade_element=instance, glossary=inline_glossary, order=order)
