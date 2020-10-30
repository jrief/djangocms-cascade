from django.conf import settings
from django.utils.translation import gettext_lazy as _
from cms.extensions.toolbar import ExtensionToolbar
from cms.toolbar_pool import toolbar_pool
from cms.toolbar.items import Break
from cms.cms_toolbars import PAGE_MENU_SECOND_BREAK
from cmsplugin_cascade.models import CascadePage


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

if settings.CMSPLUGIN_CASCADE['register_page_editor']:
    toolbar_pool.register(CascadePageToolbar)
