import json
from django import forms
from django.forms import fields
from django.apps import apps
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from entangled.forms import EntangledModelFormMixin
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.models import SharedGlossary


class SelectSharedGlossary(forms.Select):
    option_inherits_attrs = True

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        if value:
            attrs = {'data-glossary': json.dumps(self._get_data_glossary(value))}
        else:
            attrs = {}
        return super(SelectSharedGlossary, self).create_option(name, value, label, selected, index, subindex, attrs)

    def _get_data_glossary(self, option_value):
        shared_instance = self.choices.queryset.get(pk=option_value)
        plugin_instance = plugin_pool.get_plugin(shared_instance.plugin_type)
        # use the saved glossary and filter it by fields marked as sharable
        glossary = dict((key, value) for key, value in shared_instance.glossary.items()
                        if key in plugin_instance.sharable_fields)
        self._enrich_link(glossary)
        return glossary

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


class SharableFormMixin(EntangledModelFormMixin):
    """
    The change editor of plugins marked as sharable, are enriched by three fields:
        - a select box named 'shared_glossary',
        - a checkbox named 'save_shared_glossary'
        - a text input field 'save_as_identifier'
    these additional form fields are added during runtime.
    """
    shared_glossary = forms.ModelChoiceField(
        label=_("Shared Settings"),
        required=False,
        queryset=SharedGlossary.objects.all(),
        # widget=SelectSharedGlossary(),
        empty_label=_("Use individual settings"),
        help_text=_("Use settings shared with other plugins of this type"),
    )

    save_shared_glossary = fields.BooleanField(
        label=_("Remember these settings as:"),
        required=False,
    )

    save_as_identifier = fields.CharField(
        label='',
        required=False,
    )

    class Meta:
        untangled_fields = ['save_shared_glossary', 'save_as_identifier', 'shared_glossary']

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data['save_as_identifier']
        if cleaned_data['save_shared_glossary'] and not identifier:
            msg = _("An identifier is required to remember these settings.")
            raise ValidationError(msg)
        if SharedGlossary.objects.filter(identifier=identifier).exclude(pk=self.instance.pk).exists():
            msg = _("The identifier '{}' has already been used, please choose another name.")
            raise ValidationError(msg.format(identifier))
        return cleaned_data


class SharableGlossaryMixin(metaclass=forms.MediaDefiningClass):
    """
    Every plugin class of type ``CascadePluginBase`` additionally inherits from this mixin,
    if the plugin is marked as sharable.
    This class adds the appropriate methods to the plugin class in order to store
    an assortment of glossary values as a glossary reusable by other plugin instances.
    """
    ring_plugin = 'SharableGlossaryMixin'

    class Media:
        js = ['cascade/js/admin/sharableglossary.js']

    def get_form(self, request, obj=None, **kwargs):
        base_form = kwargs.pop('form', self.form)
        assert issubclass(base_form, EntangledModelFormMixin), "The Form class must inherit from EntangledModelFormMixin"
        kwargs['form'] = type(base_form.__name__, (SharableFormMixin, base_form), {})
        kwargs['form'].base_fields['shared_glossary'].limit_choices_to = dict(plugin_type=self.__class__.__name__)
        try:
            shared_glossary = SharedGlossary.objects.get(id=request.GET.get('glossary'))
        except ValueError:
            shared_glossary = None
        except SharedGlossary.DoesNotExist:
            shared_glossary = obj.shared_glossary if obj else None
        for field_name in self.sharable_fields:
            if obj and shared_glossary:
                obj.glossary[field_name] = shared_glossary.glossary.get(field_name, '')
            kwargs['form'].base_fields[field_name].disabled = bool(shared_glossary)
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # in case checkbox for `save_shared_glossary` is checked and an identifier for a shared
        # glossary is set, then we create a new entry in `models.SharedGlossary` transferring
        # the fields declared as sharable for this plugin
        identifier = form.cleaned_data['save_as_identifier']
        if form.cleaned_data['save_shared_glossary'] and identifier:
            # move data from form glossary to a SharedGlossary and refer to it
            shared_glossary, created = SharedGlossary.objects.get_or_create(
                plugin_type=self.__class__.__name__, identifier=identifier)
            assert created, "SharableCascadeForm.clean_save_as_identifier() erroneously validated identifier '{}' " \
                            "as unique".format(identifier)
            glry = form.cleaned_data['glossary']
            shared_glossary.glossary = dict((key, glry[key]) for key in self.sharable_fields if key in glry)
            shared_glossary.save()
            obj.shared_glossary = shared_glossary
            obj.save()

    @classmethod
    def get_data_representation(cls, instance):
        data = super().get_data_representation(instance)
        if instance.shared_glossary:
            data.setdefault('glossary', {})
            data['glossary'].update(instance.shared_glossary.glossary)
            data.update(shared_glossary=instance.shared_glossary.identifier)
        return data

    @classmethod
    def add_shared_reference(cls, instance, shared_glossary_identifier):
        try:
            shared_glossary = SharedGlossary.objects.get(plugin_type=instance.plugin_type,
                                                         identifier=shared_glossary_identifier)
        except SharedGlossary.DoesNotExist:
            pass
        else:
            instance.shared_glossary = shared_glossary
            instance.save(update_fields=['shared_glossary'])
