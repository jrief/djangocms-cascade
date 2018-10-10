# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar
from cms.toolbar.items import Break
from cms.cms_toolbars import PAGE_MENU_IDENTIFIER, PAGE_MENU_SECOND_BREAK
from cmsplugin_cascade.models import CascadePage


@toolbar_pool.register
class IconFontToolbar(CMSToolbar):
    def populate(self):
        page_menu = self.toolbar.get_or_create_menu(PAGE_MENU_IDENTIFIER, _("Page"))
        position = page_menu.find_first(Break, identifier=PAGE_MENU_SECOND_BREAK)
        CascadePage.assure_relation(self.request.current_page)
        extendedpage_id = self.request.current_page.cascadepage.id
        url = reverse('admin:cmsplugin_cascade_cascadepage_change', args=(extendedpage_id,))
        page_menu.add_modal_item(_("Choose Icon Font"), position=position, url=url)
