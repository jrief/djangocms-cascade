from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.urls import reverse
from cms.extensions.toolbar import ExtensionToolbar
from cms.toolbar_pool import toolbar_pool
from cms.toolbar.items import Break
from cms.toolbar_base import CMSToolbar
from cms.cms_toolbars import PAGE_MENU_SECOND_BREAK, ADMIN_MENU_IDENTIFIER, USER_SETTINGS_BREAK
from cmsplugin_cascade.models import CascadePage


@toolbar_pool.register
class CascadePageToolbar(ExtensionToolbar):
    model = CascadePage

    def populate(self):
        current_page_menu = self._setup_extension_toolbar()
        if current_page_menu:
            # retrieves the instance of the current extension (if any) and the toolbar item URL
            page_extension, url = self.get_page_extension_admin()
            if url:
                position = current_page_menu.find_first(Break, identifier=PAGE_MENU_SECOND_BREAK)
                disabled = not self.toolbar.edit_mode_active
                current_page_menu.add_modal_item(_("Extra Page Fields"), position=position, url=url, disabled=disabled)
        
        
@toolbar_pool.register
class CascadeToolbar(CMSToolbar):

    def populate(self):
        if getattr(settings, 'CASCADE_THEME', None):
            admin_menu = self.toolbar.get_or_create_menu(
                ADMIN_MENU_IDENTIFIER, _('Site'))
            position_user_set = admin_menu.find_first(Break, identifier=USER_SETTINGS_BREAK)
            position_theme = admin_menu.add_break('THEME', position_user_set)
            position_theme = admin_menu.find_first(Break, identifier=USER_SETTINGS_BREAK)

            admin_menu.add_modal_item(
                name='Theme',
                url="/theme/",
                position=position_theme,
                )
