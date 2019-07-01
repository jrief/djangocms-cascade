from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.encoding import force_text
from cms.extensions.toolbar import ExtensionToolbar
from cms.toolbar_pool import toolbar_pool
from cms.toolbar.items import Break
from cms.cms_toolbars import PAGE_MENU_SECOND_BREAK, ADMIN_MENU_IDENTIFIER, CLIPBOARD_BREAK 
from cmsplugin_cascade.models import CascadePage
from cms.toolbar_base import CMSToolbar
from cmsplugin_cascade.clipslib import views
from cms.toolbar.items import AjaxItem
from cms.utils.urlutils import admin_reverse
import json

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


class AjaxCustomLogicItem(AjaxItem):
    template = "cascade/admin/library_clips/item_ajax_cascade.html"
    

    def __init__(self, name, action, csrf_token, data=None, active=False,
                 disabled=False, extra_classes=None,
                 question=None, side='LEFT', on_success=None, method='POST',data_modal_style=None , name_func_js_filter=None , identifier=None):
        super(AjaxItem, self).__init__(side) 
        self.name = name
        self.action = action
        self.active = active
        self.disabled = disabled
        self.csrf_token = csrf_token
        self.data = data or {}
        self.extra_classes = extra_classes or []
        self.question = question
        self.on_success = on_success
        self.method = method

        self.identifier= identifier
        self.data_modal_style = data_modal_style
        self.name_func_js_filter = name_func_js_filter

    def __repr__(self):
        return '<AjaxItem:%s>' % force_text(self.name)

    def get_context(self):
        data = self.data.copy()

        if self.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            data['csrfmiddlewaretoken'] = self.csrf_token

        return {
            'action': self.action,
            'name': self.name,
            'active': self.active,
            'disabled': self.disabled,
            'extra_classes': self.extra_classes,
            'data': json.dumps(data),
            'question': self.question,
            'on_success': self.on_success,
            'method': self.method,
            'name_func_js_filter' : self.name_func_js_filter,
            'data_modal_style' : json.dumps(self.data_modal_style),
        }


@toolbar_pool.register
class CascadeToolbar(  CMSToolbar, ):
    clips_title = _("Clipboard Library")

    def populate(self):
        if getattr( settings, 'CASCADE_CLIPS_LIBRARY', None):
            admin_menu = self.toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER, _('Site'))
            self.admin_menu = self.toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER, _('Site'))
            position = admin_menu.find_first(Break, identifier=CLIPBOARD_BREAK )

            #admin_menu.add_link_item(_('Library Clips'), url='/cascade_libclips/1/', extra_classes=('cms-show-clipslib',), position=position )

            anon_can_access = True
            cliptree_navbars= False
            csrf_token=self.toolbar.csrf_token
            
            item = AjaxCustomLogicItem(identifier="clips",
              extra_classes=["extra_wrapper_classes"],
              name=self.clips_title, action="/cascade_clips/",
              name_func_js_filter="ClipsStorageLogic" , 
              method='POST', 
              csrf_token=csrf_token,
              data={ 'storage_logic': 'false'  },
              data_modal_style={ 'minWidth': '325px', 'minHeight': '100', 'height':'95%', 'width': '40%', 'left': '0px',  'top': '48px', 'margin': '0', 'z-index': '140' }
              )

            admin_menu.add_item(item, position) 
