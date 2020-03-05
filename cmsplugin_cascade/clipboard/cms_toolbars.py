from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool


@toolbar_pool.register
class CascadeClipboardToolbar(CMSToolbar):
    class Media:
        css = {
            'all': ['cascade/css/admin/clipboard.css']
        }
