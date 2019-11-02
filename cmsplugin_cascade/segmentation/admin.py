from django.forms import MediaDefiningClass
from django.contrib import admin
from django.utils.module_loading import import_string
from cmsplugin_cascade import app_settings
from cmsplugin_cascade.models import Segmentation


class SegmentationAdminMetaclass(MediaDefiningClass):
    def __new__(cls, name, bases, attrs):
        bases = tuple(import_string(sgm[1]) for sgm in app_settings.CMSPLUGIN_CASCADE['segmentation_mixins']) + bases
        new_class = super().__new__(cls, name, bases, attrs)
        return new_class


class SegmentationAdmin(admin.ModelAdmin, metaclass=SegmentationAdminMetaclass):
    class Media:
        js = ['admin/js/jquery.init.js', 'cascade/js/admin/segmentation.js']

    def get_model_perms(self, request):
        """
        Return empty perms dict to hide the model from admin index.
        """
        return {}

    def get_queryset(self, request):
        """
        Returns the QuerySet for `_lookup_model`, instead of dummy model `Segmentation`.
        """
        model = getattr(request, '_lookup_model', self.model)
        qs = model._default_manager.get_queryset()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

admin.site.register(Segmentation, SegmentationAdmin)
