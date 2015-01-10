# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django import forms
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.widgets import JSONMultiWidget
from cmsplugin_cascade.models import SharedGlossary, SharableCascadeElement


class SharedGlossaryAdmin(admin.ModelAdmin):
    change_form_template = 'cascade/admin/change_form.html'
    list_display = ('identifier', 'plugin_type', 'used_by',)
    list_filter = ('plugin_type',)

    def get_fieldsets(self, request, obj=None):
        """Return the fieldsets from associated plugin"""
        fields = []
        for key in self.plugin_instance.sharable_fields:
            try:
                fields.append(self.plugin_instance.glossary_field_map[key])
            except KeyError:
                continue
            except AttributeError:
                break
        fields.append('glossary')
        return [(None, {'fields': ['identifier']}), (_("Shared Fields"), {'fields': fields})]

    def get_form(self, request, obj=None, **kwargs):
        """
        Creates a temporary form with an identifier and the fields declared as sharables for the
        corresponding plugin model. Additionally it adds dynamic fields to edit the content inside
        the model field `glossary`. The layout, validation and media files for these dynamic fields
        are borrowed from the corresponding plugin.
        """
        self.plugin_instance = plugin_pool.get_plugin(obj.plugin_type)
        sharable_fields = getattr(self.plugin_instance, 'sharable_fields', [])
        glossary_fields = [f for f in self.plugin_instance.glossary_fields if f.name in sharable_fields]
        kwargs.update(widgets={'glossary': JSONMultiWidget(glossary_fields)}, labels={'glossary': ''})
        try:
            kwargs.update(form=self.plugin_instance.form)
        except AttributeError:
            pass
        ModelForm = super(SharedGlossaryAdmin, self).get_form(request, obj, **kwargs)
        if callable(getattr(ModelForm, 'unset_required_for', None)):
            ModelForm.unset_required_for(sharable_fields)
        # help_text can not be cleared using an empty string in modelform_factory
        ModelForm.base_fields['glossary'].help_text = ''
        for field in glossary_fields:
            ModelForm.base_fields['glossary'].validators.append(field.run_validators)
        return ModelForm

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

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        bases = self.plugin_instance().get_ring_bases()
        # since the Sharable Admin reuses the JavaScript plugins, remove the one, regarding shareability itself
        bases.remove('SharableGlossaryMixin')
        context['base_plugins'] = ['django.cascade.{0}'.format(b) for b in bases]
        return super(SharedGlossaryAdmin, self).render_change_form(request, context, add, change, form_url, obj)

admin.site.register(SharedGlossary, SharedGlossaryAdmin)
