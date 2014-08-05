# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import get_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import python_2_unicode_compatible
from cmsplugin_cascade.sharable.models import SharableCascadeElement


@python_2_unicode_compatible
class LinkElement(SharableCascadeElement):
    """
    A proxy model for the ``<a>`` element.
    """
    class Meta:
        proxy = True

    def __str__(self):
        return self.content

    @property
    def link(self):
        link = self.glossary.get('link', {})
        if link.get('type') == 'cmspage':
            if not hasattr(self, '_link_model'):
                Model = get_model(*link['model'].split('.'))
                try:
                    self._link_model = Model.objects.get(pk=link['pk'])
                except ObjectDoesNotExist:
                    self._link_model = None
            if self._link_model:
                return self._link_model.get_absolute_url()
        if link.get('type') == 'exturl':
            return link['url']
        if link.get('type') == 'email':
            return 'mailto:{email}'.format(**link)

    @property
    def content(self):
        return self.glossary.get('link_content', '')
