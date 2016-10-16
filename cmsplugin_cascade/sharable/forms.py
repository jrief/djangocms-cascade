# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django import forms
from django.forms import fields
from django.apps import apps
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from cmsplugin_cascade.utils import resolve_dependencies
from cmsplugin_cascade.models import SharedGlossary, SharableCascadeElement


class SelectSharedGlossary(forms.Select):
    def render_option(self, selected_choices, option_value, option_label):
        if option_value:
            glossary = self.choices.queryset.get(pk=option_value).glossary
            self._enrich_link(glossary)
            data = format_html(' data-glossary="{0}"', json.dumps(glossary))
        else:
            data = mark_safe('')
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        return format_html('<option value="{0}"{1}{2}>{3}</option>',
                           option_value, selected_html, data, force_text(option_label))

    def _enrich_link(self, glossary):
        """
        Enrich the dict glossary['link'] with an identifier onto the model
        """
        try:
            Model = apps.get_model(*glossary['link']['model'].split('.'))
            obj = Model.objects.get(pk=glossary['link']['pk'])
            glossary['link'].update(identifier=str(obj))
        except (KeyError, ObjectDoesNotExist):
            pass


class SharableCascadeForm(forms.ModelForm):
    """
    The change editor of plugins marked as sharable, are enriched by three fields:
        - a select box named 'shared_glossary',
        - a checkbox named 'save_shared_glossary'
        - a text input field 'save_as_identifier'
    these additional form fields are added during runtime.
    """
    shared_glossary = forms.ModelChoiceField(
        label=_("Shared Settings"), required=False, queryset=SharedGlossary.objects.all(),
        widget=SelectSharedGlossary(), empty_label=_("Use individual settings"),
        help_text=_("Use settings shared with other plugins of this type"))
    save_shared_glossary = fields.BooleanField(label=_("Remember these settings as:"),
                                               required=False)
    save_as_identifier = fields.CharField(label='', required=False)

    def __init__(self, *args, **kwargs):
        try:
            self.base_fields['shared_glossary'].initial = kwargs['instance'].shared_glossary.pk
        except (AttributeError, KeyError):
            pass
        super(SharableCascadeForm, self).__init__(*args, **kwargs)

    def clean_save_as_identifier(self):
        identifier = self.cleaned_data['save_as_identifier']
        if SharedGlossary.objects.filter(identifier=identifier).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_("The identifier '{0}' has already been used, please choose another name.").format(identifier))
        return identifier

    def save(self, commit=False):
        self.instance.shared_glossary = self.cleaned_data['shared_glossary']
        return super(SharableCascadeForm, self).save(commit)


class SharableGlossaryMixin(object):
    """
    Add this mixin class to Plugin classes which refer to the model ``SharableCascadeElement`` or
    inherit from it. This class adds the appropriate methods to the plugin class in order to store
    an assortment of glossary values as a glossary reusable by other plugin instances.
    """
    class Media:
            js = resolve_dependencies('cascade/js/admin/sharableglossary.js')

    def get_form(self, request, obj=None, **kwargs):
        """
        Extend the form for the given plugin with the form SharableCascadeForm
        """
        form = type(str('ExtSharableForm'), (SharableCascadeForm, kwargs.pop('form', self.form)), {})
        form.base_fields['shared_glossary'].limit_choices_to = dict(plugin_type=self.__class__.__name__)
        kwargs.update(form=form)
        return super(SharableGlossaryMixin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        super(SharableGlossaryMixin, self).save_model(request, obj, form, change)
        # in case checkbox for `save_shared_glossary` is checked and an identifier for a shared
        # glossary is set, then we create a new entry in `models.SharedGlossary` transferring
        # the fields declared as sharable for this plugin
        identifier = form.cleaned_data['save_as_identifier']
        if form.cleaned_data['save_shared_glossary'] and identifier:
            # move data from form glossary to a SharedGlossary and refer to it
            shared_glossary, created = SharedGlossary.objects.get_or_create(
                plugin_type=self.__class__.__name__, identifier=identifier)
            assert created, "SharableCascadeForm.clean_save_as_identifier() erroneously validated identifier '%s' as unique".format(identifier)
            glry = form.cleaned_data['glossary']
            shared_glossary.glossary = dict((key, glry[key]) for key in self.sharable_fields if key in glry)
            shared_glossary.save()
            obj.shared_glossary = shared_glossary
            obj.save()

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # create a list of sharable fields, so that the JS class SharableGlossaryMixin
        # knows which ones to disable, whenever a Shared Setting is active
        form = context['adminform'].form
        share_fields = []
        for key in self.sharable_fields:
            glossary_field_map = getattr(self, 'glossary_field_map', {})
            if key in glossary_field_map:
                for basekey in glossary_field_map[key]:
                    share_fields.append(form[basekey].auto_id)
        for glossary_field in self.glossary_fields:
            if glossary_field.name in self.sharable_fields:
                share_fields.extend(glossary_field.get_element_ids(form['glossary'].auto_id))
        context.update(sharable_fields=mark_safe(json.dumps(share_fields)))
        return super(SharableGlossaryMixin, self).render_change_form(request, context, add, change, form_url, obj)

    def get_ring_bases(self):
        bases = super(SharableGlossaryMixin, self).get_ring_bases()
        bases.append('SharableGlossaryMixin')
        return bases
