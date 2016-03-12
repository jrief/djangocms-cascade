# -*- coding: utf-8 -*-
from __future__ import unicode_literals
try:
    from django.contrib.sites.shortcuts import get_current_site
except ImportError:
    from django.contrib.sites.models import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps
from django.utils.encoding import python_2_unicode_compatible
from cms.utils.placeholder import get_placeholder_conf


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


class TransparentMixin(object):
    """
    Add this mixin class to other Cascade plugins, wishing to be added transparently between two
    plugins restricting parent-children relationships.
    For instance: A ColumnPlugin can only be added as a child to a RowPlugin. This means that no
    other wrapper can be added between those two plugins. By adding this mixin class we can allow
    any plugin to behave transparently, just as if it would not have be inserted into the DOM tree.
    When moving plugins in- and out of transparent wrapper plugins, always reload the page, so that
    the parent-children relationships can be updated.
    """
    def get_child_classes(self, slot, page):
        if not hasattr(self, '_cached_child_classes'):
            if self.cms_plugin_instance:
                if self.cms_plugin_instance.parent:
                    parent_plugin_instance, parent_plugin = self.cms_plugin_instance.parent.get_plugin_instance()
                    parent_plugin.cms_plugin_instance = parent_plugin_instance
                    child_classes = set(parent_plugin.get_child_classes(slot, page))
                else:  # SegmentPlugin is at the root level
                    template = page and page.get_template() or None
                    child_classes = set(get_placeholder_conf('plugins', slot, template, default=[]))
            else:
                child_classes = set()
            child_classes.update(super(TransparentMixin, self).get_child_classes(slot, page))
            self._cached_child_classes = tuple(child_classes)
        return self._cached_child_classes
