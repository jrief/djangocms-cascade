# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from types import MethodType
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.conf.urls import url
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _, ungettext
from django.utils.encoding import force_text
from django.utils.html import format_html
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
        Returns the QuerySet for `_lookup_model`, instead of dummy model `Segmentation`.
        """
        model = getattr(request, '_lookup_model', self.model)
        qs = model._default_manager.get_queryset()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def emulate_users(self, request):
        def display_as_link(self, obj):
            return format_html('<a href="#">{0}</a>', obj.identifier())

        lookup_model = get_user_model()
        opts = lookup_model._meta
        app_label = opts.app_label
        user_model_admin = self.admin_site._registry[lookup_model]
        request._lookup_model = lookup_model
        list_display_links = user_model_admin.get_list_display_links(request, user_model_admin.list_display)
        # replace first entry in list_display_links by customized method display_as_link
        list_display_link = list_display_links[0]
        list_display = list(user_model_admin.list_display)
        list_display.remove(list_display_link)
        list_display.insert(0, 'display_as_link')
        display_as_link.allow_tags = True
        display_as_link.short_description = admin.util.label_for_field(list_display_link, lookup_model)
        self.display_as_link = MethodType(display_as_link, self, SegmentationAdmin)

        ChangeList = self.get_changelist(request)
        cl = ChangeList(request, lookup_model, list_display,
            ('display_as_link',),  # disable list_display_links in ChangeList, instead override that field
            user_model_admin.list_filter,
            user_model_admin.date_hierarchy, user_model_admin.search_fields,
            user_model_admin.list_select_related, user_model_admin.list_per_page,
            user_model_admin.list_max_show_all,
            (),  # disable list_editable
            self)
        cl.formset = None
        selection_note_all = ungettext('%(total_count)s selected',
            'All %(total_count)s selected', cl.result_count)

        context = {
            'module_name': force_text(opts.verbose_name_plural),
            'selection_note': _('0 of %(cnt)s selected') % {'cnt': len(cl.result_list)},
            'selection_note_all': selection_note_all % {'total_count': cl.result_count},
            'title': _("Select %(user_model)s to emulate") % {'user_model': opts.verbose_name},
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
