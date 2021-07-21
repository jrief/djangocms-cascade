from django.contrib import admin
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.response import TemplateResponse
from django.urls import reverse, re_path
from django.utils.translation import gettext_lazy as _, ngettext
from django.utils.html import format_html

from cms.constants import REFRESH_PAGE


class SegmentPluginModelMixin:
    """
    TODO: whenever cmsplugin_cascade drops support for django-CMS < 3.4, this mixin class
    shall be added to the plugin rather than to the model
    """

    def get_context_override(self, request):
        """
        Return a dictionary to override the request context object during evaluation with
        alternative values. Normally this is an empty dict. However, when a staff user overrides
        the segmentation, then update the context with this returned dict.
        """
        return {}

    def render_plugin(self, context=None, placeholder=None, admin=False, processors=None):
        context.update(self.get_context_override(context['request']))
        content = super().render_plugin(context, placeholder, admin, processors)
        context.pop()
        return content


class EmulateUserModelMixin(SegmentPluginModelMixin):
    UserModel = get_user_model()

    def get_context_override(self, request):
        """
        Override the request object with an emulated user.
        """
        context_override = super().get_context_override(request)
        try:
            if request.user.is_staff:
                user = self.UserModel.objects.get(pk=request.session['emulate_user_id'])
                context_override.update(user=user)
        except (self.UserModel.DoesNotExist, KeyError):
            pass
        return context_override


class EmulateUserAdminMixin:
    UserModel = get_user_model()

    @staticmethod
    def populate_toolbar(segmentation_menu, request):
        active = 'emulate_user_id' in request.session
        segmentation_menu.add_sideframe_item(
            _("Emulate User"),
            url=reverse('admin:emulate-users'),
            active=active,
        )
        segmentation_menu.add_ajax_item(
            _("Clear emulations"),
            action=reverse('admin:clear-emulations'),
            on_success=REFRESH_PAGE,
            disabled=not active,
        )

    def get_urls(self):
        return [
            re_path(r'^emulate_users/$', self.admin_site.admin_view(self.emulate_users), name='emulate-users'),
            re_path(r'^emulate_user/(?P<user_id>\d+)/$', self.admin_site.admin_view(self.emulate_user), name='emulate-user'),
            re_path(r'^clear_emulations/$', self.admin_site.admin_view(self.clear_emulations), name='clear-emulations'),
        ] + super().get_urls()

    def emulate_user(self, request, user_id):
        try:
            request.session['emulate_user_id'] = int(user_id)
            return HttpResponse('OK')
        except TypeError as err:
            return HttpResponseBadRequest(err.message)

    def emulate_users(self, request):
        """
        The list view
        """
        def display_as_link(obj):
            try:
                identifier = getattr(user_model_admin, list_display_link)(obj)
            except AttributeError:
                identifier = admin.utils.lookup_field(list_display_link, obj, model_admin=self)[2]
            emulate_user_id = request.session.get('emulate_user_id')
            if emulate_user_id == obj.id:
                return format_html('<strong>{}</strong>', identifier)
            fmtargs = {
                'href': reverse('admin:emulate-user', kwargs={'user_id': obj.id}),
                'identifier': identifier,
            }
            return format_html('<a href="{href}" class="emulate-user">{identifier}</a>', **fmtargs)

        opts = self.UserModel._meta
        app_label = opts.app_label
        user_model_admin = self.admin_site._registry[self.UserModel]
        request._lookup_model = self.UserModel
        list_display_links = user_model_admin.get_list_display_links(request, user_model_admin.list_display)
        # replace first entry in list_display_links by customized method display_as_link
        list_display_link = list_display_links[0]
        try:
            list_display = list(user_model_admin.segmentation_list_display)
        except AttributeError:
            list_display = list(user_model_admin.list_display)
        list_display.remove(list_display_link)
        list_display.insert(0, 'display_as_link')
        display_as_link.allow_tags = True  # TODO: presumably not required anymore since Django-1.9
        try:
            display_as_link.short_description = user_model_admin.identifier.short_description
        except AttributeError:
            display_as_link.short_description = admin.utils.label_for_field(list_display_link, self.UserModel)
        self.display_as_link = display_as_link

        ChangeList = self.get_changelist(request)
        cl = ChangeList(request, self.UserModel, list_display,
            (None,),  # disable list_display_links in ChangeList, instead override that field
            user_model_admin.list_filter,
            user_model_admin.date_hierarchy, user_model_admin.search_fields,
            user_model_admin.list_select_related, user_model_admin.list_per_page,
            user_model_admin.list_max_show_all,
            (),  # disable list_editable
            self,
            None)
        cl.formset = None
        selection_note_all = ngettext('%(total_count)s selected',
            'All %(total_count)s selected', cl.result_count)

        context = {
            'module_name': str(opts.verbose_name_plural),
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
        ], context)

    def clear_emulations(self, request):
        request.session.pop('emulate_user_id', None)
        return HttpResponse('OK')
