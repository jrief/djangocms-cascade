# -*- coding: utf-8 -*-
import json
from django import forms
from django.forms import fields
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from .models import SharedGlossary


class SelectSharedGlossary(forms.Select):
    def render_option(self, selected_choices, option_value, option_label):
        if option_value:
            glossary = self.choices.queryset.get(pk=option_value).glossary
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


class SharableCascadeForm(forms.ModelForm):
    save_shared_glossary = fields.BooleanField(required=False, label=_("Remember these settings as:"))
    save_as_identifier = fields.CharField(required=False, label='')

    def clean_save_as_identifier(self):
        identifier = self.cleaned_data['save_as_identifier']
        if SharedGlossary.objects.filter(identifier=identifier).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_("The identifier '{0}' has already been used, please choose another name.").format(identifier))
        return identifier


class SharableGlossaryMixin(object):
    """
    Add this mixin class to Plugin classes which refer to the model ``SharableCascadeElement`` or
    inherit from it. This class adds the appropriate methods to the plugin class in order to store
    an assortment of glossary values as a glossary reusable by other plugin instances.
    """
    def get_form(self, request, obj=None, **kwargs):
        form = kwargs.pop('form', self.form)
        shared_glossary = forms.ModelChoiceField(required=False,
            label=_("Shared Settings"),
            queryset=SharedGlossary.objects.filter(plugin_type=self.__class__.__name__),
            widget=SelectSharedGlossary(),
            empty_label=_("Use individual settings"),
            help_text=_("Use settings shared with other plugins of this type"))
        ExtSharableForm = type('ExtSharableForm', (form, SharableCascadeForm), {'shared_glossary': shared_glossary})
        kwargs.update(form=ExtSharableForm)
        return super(SharableGlossaryMixin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        super(SharableGlossaryMixin, self).save_model(request, obj, form, change)
        # in case checkbox for ``save_shared_glossary`` was set, create an entry in ``SharedGlossary``
        identifier = form.cleaned_data['save_as_identifier']
        if form.cleaned_data['save_shared_glossary'] and identifier:
            # move data from form glossary to a SharedGlossary and refer to it
            shared_glossary, created = SharedGlossary.objects.get_or_create(plugin_type=self.__class__.__name__, identifier=identifier)
            if not created:
                raise RuntimeError("SharableCascadeForm.clean_save_as_identifier() erroneously validated identifier '%s' as unique".format(identifier))
            glry = form.cleaned_data['glossary']
            shared_glossary.glossary = dict((key, glry[key]) for key in self.sharable_fields if key in glry)
            shared_glossary.save()
            obj.shared_glossary = shared_glossary
            obj.save()
