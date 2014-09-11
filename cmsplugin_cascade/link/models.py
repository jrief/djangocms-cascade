# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from cmsplugin_cascade.sharable.models import SharableCascadeElement
from cmsplugin_cascade.models import CascadeElement


@python_2_unicode_compatible
class LinkElementMixin(object):
    """
    A proxy model for the ``<a>`` element.
    """
    def __str__(self):
        return self.content

    @property
    def link(self):
        return self.plugin_class.get_link(self)

    @property
    def content(self):
        return self.glossary.get('link_content', '')


class SimpleLinkElement(LinkElementMixin, CascadeElement):
    class Meta:
        proxy = True


class SharableLinkElement(LinkElementMixin, SharableCascadeElement):
    class Meta:
        proxy = True

    @property
    def link(self):
        # TODO: fetch from shared glossary, if that exists
        return super(SharableLinkElement, self).link
