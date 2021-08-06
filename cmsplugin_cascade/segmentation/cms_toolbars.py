from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar
from cmsplugin_cascade import app_settings


@toolbar_pool.register
class SegmentationToolbar(CMSToolbar):
    def populate(self):
        if not self.request.user.has_perm('cmsplugin_cascade.view_segmentation'):
            return
        menu = self.toolbar.get_or_create_menu('segmentation', _("Segmentation"))
        if not self.request.user.has_perms(['cmsplugin_cascade.add_segmentation',
            'cmsplugin_cascade.change_segmentation', 'cmsplugin_cascade.delete_segmentation']):
            menu.disabled = True
        for sgm in app_settings.CMSPLUGIN_CASCADE['segmentation_mixins']:
            SegmentationMixin = import_string(sgm[1])
            populate_handler = getattr(SegmentationMixin, 'populate_toolbar', None)
            if callable(populate_handler):
                populate_handler(menu, self.request)
