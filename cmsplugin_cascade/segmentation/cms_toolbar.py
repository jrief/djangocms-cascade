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
        active = 'emulate_user_id' in self.request.session
        menu.add_sideframe_item(_("Emulate User"), url=reverse('admin:emulate-users'), active=active)
        menu.add_ajax_item(_("Clear emulations"), action=reverse('admin:clear-emulations'),
                           on_success=self.toolbar.REFRESH_PAGE)
