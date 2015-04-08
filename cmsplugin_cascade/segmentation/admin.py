# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.conf.urls import url
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _, ungettext
from django.utils.encoding import force_text
from cmsplugin_cascade.models import Segmentation


class SegmentationAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # always False, since we don't have a model
        return False

    def has_change_permission(self, request, obj=None):
        # always False, since we don't have a model
        return False

    def get_urls(self):
        return [
            url(r'^emulate_users/$', self.admin_site.admin_view(self.emulate_users), name='emulate-users'),
        ] + super(SegmentationAdmin, self).get_urls()

    def get_queryset(self, request):
        """
        Returns a the QuerySet for the lookup model, not dummy model `Segmentation`.
        """
        model = getattr(request, '_lookup_model', self.model)
        qs = model._default_manager.get_queryset()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def emulate_users(self, request):
        lookup_model = get_user_model()
        opts = lookup_model._meta
        app_label = opts.app_label

        list_display = ['username', 'email', 'salutation', 'first_name', 'last_name', 'is_staff']
        list_display_links = ['username']
        list_filter = self.get_list_filter(request)
        request._lookup_model = lookup_model

        ChangeList = self.get_changelist(request)
        cl = ChangeList(request, lookup_model, list_display,
            list_display_links, list_filter, self.date_hierarchy,
            self.search_fields, self.list_select_related,
            self.list_per_page, self.list_max_show_all, self.list_editable,
            self)
        cl.formset = None
        selection_note_all = ungettext('%(total_count)s selected',
            'All %(total_count)s selected', cl.result_count)

        context = {
            'module_name': force_text(opts.verbose_name_plural),
            'selection_note': _('0 of %(cnt)s selected') % {'cnt': len(cl.result_list)},
            'selection_note_all': selection_note_all % {'total_count': cl.result_count},
            'title': _("Select {} to emulate").format(opts.verbose_name),
            'is_popup': cl.is_popup,
            'cl': cl,
            'media': self.media,
            'has_add_permission': False,
            'opts': cl.opts,
            'app_label': app_label,
            'actions_on_top': self.actions_on_top,
            'actions_on_bottom': self.actions_on_bottom,
            'actions_selection_counter': self.actions_selection_counter,
            'preserved_filters': self.get_preserved_filters(request),
        }
        return TemplateResponse(request, self.change_list_template or [
            'admin/%s/%s/change_list.html' % (app_label, opts.model_name),
            'admin/%s/change_list.html' % app_label,
            'admin/change_list.html'
        ], context, current_app=self.admin_site.name)

admin.site.register(Segmentation, SegmentationAdmin)
