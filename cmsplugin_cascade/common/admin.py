# -*- coding: utf-8 -*-
from django.contrib import admin
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.widgets import JSONMultiWidget
from .models import SharedGlossary


class SharedGlossaryAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'plugin_type',)

    class Media:
        css = {'all': ('admin/css/djangocms-cascade.css',)}

    def get_form(self, request, obj=None, **kwargs):
        """
        Creates the form an identifier for the model field. Additionally it adds dynamic fields to
        edit the content inside the model field `glossary`. The layout and validation for these
        dynamic fields is borrowed from the corresponding plugin.
        """
        try:
            shared_glossary_fields = plugin_pool.get_plugin(obj.plugin_type).shared_glossary_fields
        except AttributeError:
            shared_glossary_fields = ()
        else:
            kwargs.update(widgets={'glossary': JSONMultiWidget(shared_glossary_fields)}, labels={'glossary': ''})
        form = super(SharedGlossaryAdmin, self).get_form(request, obj, **kwargs)
        # help_text can not be cleared using an empty string in modelform_factory
        form.base_fields['glossary'].help_text = ''
        for field in shared_glossary_fields:
            form.base_fields['glossary'].validators.append(field.run_validators)
        setattr(form, 'shared_glossary_fields', shared_glossary_fields)
        return form

    def has_add_permission(self, request):
        # always False, since a SharedGlossary can only be added by a plugin
        return False

admin.site.register(SharedGlossary, SharedGlossaryAdmin)
