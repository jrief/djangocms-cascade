# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar
from cmsplugin_cascade import settings


@toolbar_pool.register
class SegmentationToolbar(CMSToolbar):
    def populate(self):
        menu = self.toolbar.get_or_create_menu('segmentation', _("Segmentation"))
        for sgm in settings.CMSPLUGIN_CASCADE['segmentation_mixins']:
            SegmentationMixin = import_string(sgm[1])
            populate_handler = getattr(SegmentationMixin, 'populate_toolbar', None)
            if callable(populate_handler):
                populate_handler(menu, self.request)
