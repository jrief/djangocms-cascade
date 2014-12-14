# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.widgets import JSONMultiWidget
from .models import SharedGlossary, SharableCascadeElement


class SharedGlossaryAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'plugin_type', 'used_by',)
    list_filter = ('plugin_type',)

    def get_fieldsets(self, request, obj=None):
        """Return the fieldsets from associated plugin"""
        fieldsets = [(None, {'fields': ['identifier']})]
        try:
            sharable_fieldset = self.plugin_instance.sharable_fieldset
        except AttributeError:
            sharable_fieldset = {'fields': ('glossary',)}
        fieldsets.append((_("Shared Fields"), sharable_fieldset))
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        """
        Creates the form an identifier for the model field. Additionally it adds dynamic fields to
        edit the content inside the model field `glossary`. The layout and validation for these
        dynamic fields is borrowed from the corresponding plugin.
        """
        self.plugin_instance = plugin_pool.get_plugin(obj.plugin_type)
        sharable_fields = getattr(self.plugin_instance, 'sharable_fields', [])
        glossary_fields = [field for field in self.plugin_instance.glossary_fields if field.name in sharable_fields]
        kwargs.update(widgets={'glossary': JSONMultiWidget(glossary_fields)}, labels={'glossary': ''})
        try:
            kwargs.update(form=self.plugin_instance.form)  # TODO: this was self.plugin_instance.sharable_form
        except AttributeError:
            pass
        form = super(SharedGlossaryAdmin, self).get_form(request, obj, **kwargs)
        # help_text can not be cleared using an empty string in modelform_factory
        form.base_fields['glossary'].help_text = ''
        for field in glossary_fields:
            form.base_fields['glossary'].validators.append(field.run_validators)
        return form

    def has_add_permission(self, request):
        # always False, since a SharedGlossary can only be added by a plugin
        return False

    def change_view(self, request, object_id, form_url='', extra_context={}):
        obj = self.get_object(request, object_id)
        extra_context['title'] = _("Change %s") % force_text(str(obj.plugin_type))
        return super(SharedGlossaryAdmin, self).change_view(request, object_id,
            form_url, extra_context=extra_context)

    @property
    def media(self):
        media = super(SharedGlossaryAdmin, self).media
        media += forms.Media(css={'all': ('cascade/css/admin/partialfields.css', 'cascade/css/admin/editplugin.css',)})
        try:
            media += self.plugin_instance().media
        except AttributeError:
            pass
        return media

    def used_by(self, obj):
        """
        Returns the number of plugins using this shared glossary
        """
        return SharableCascadeElement.objects.filter(shared_glossary=obj).count()
    used_by.short_description = _("Used by plugins")

admin.site.register(SharedGlossary, SharedGlossaryAdmin)
