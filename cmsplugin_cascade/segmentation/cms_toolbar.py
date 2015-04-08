# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar


@toolbar_pool.register
class SegmentationToolbar(CMSToolbar):
    def populate(self):
        menu = self.toolbar.get_or_create_menu('segmentation', _("Segmentation"))
        url = reverse('admin:emulate-users')
        menu.add_sideframe_item(_("Emulate Users"), url=url)
