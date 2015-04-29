# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.utils.module_loading import import_by_path
from django.utils.six import with_metaclass
from cmsplugin_cascade.models import Segmentation
from cmsplugin_cascade import settings


class SegmentationAdminMetaclass(admin.options.RenameBaseModelAdminMethods):
    def __new__(cls, name, bases, attrs):
        bases = tuple(import_by_path(sgm) for sgm in settings.CASCADE_SEGMENTATION_MIXINS) + bases
        new_class = super(SegmentationAdminMetaclass, cls).__new__(cls, name, bases, attrs)
        return new_class


class SegmentationAdmin(with_metaclass(SegmentationAdminMetaclass, admin.ModelAdmin)):
    class Media:
        js = ('cascade/js/admin/segmentation.js',)

    def has_add_permission(self, request):
        # always False, since we don't have a model
        return False

    def has_change_permission(self, request, obj=None):
        # always False, since we don't have a model
        return False

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
