import json
from copy import deepcopy
from django import forms
from django.contrib.admin.helpers import AdminForm
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from entangled.forms import EntangledModelFormMixin
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.models import SharedGlossary, CascadeElement
from .fields import SharedSettingsField


class SelectSharedGlossary(forms.Select):
    option_inherits_attrs = True

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        if value:
            attrs = {'data-glossary': json.dumps(self._get_data_glossary(value))}
        else:
            attrs = {}
        return super().create_option(name, value, label, selected, index, subindex, attrs)

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


class SharedFormMixin(EntangledModelFormMixin):
    """
    The change editor of plugins marked as sharable, are enriched by three fields:
        - a select box named 'shared_glossary',
        - a checkbox and a text input field
    these additional form fields are added during runtime.
    """
    shared_glossary = forms.ModelChoiceField(
        label=_("Shared Settings"),
        required=False,
        queryset=SharedGlossary.objects.all(),
        empty_label=_("Use individual settings"),
        help_text=_("Use settings shared with other plugins of this type"),
    )

    class Meta:
        untangled_fields = ['shared_glossary']


class SharableFormMixin(SharedFormMixin):
    save_settings_as = SharedSettingsField(
        label=_("Remember these settings as"),
    )

    class Meta:
        untangled_fields = ['save_settings_as']

    def clean_save_settings_as(self):
        identifier = self.cleaned_data['save_settings_as']
        if SharedGlossary.objects.filter(identifier=identifier).exclude(pk=self.instance.pk).exists():
            msg = _("The identifier '{}' has already been used, please choose another name.")
            raise ValidationError(msg.format(identifier))
        return identifier



class SharableGlossaryMixin(metaclass=forms.MediaDefiningClass):
    """
    Every plugin class of type ``CascadePluginBase`` additionally inherits from this mixin,
    if the plugin is marked as sharable.
    This class adds the appropriate methods to the plugin class in order to store
    an assortment of glossary values as a glossary reusable by other plugin instances.
    """
    ring_plugin = 'SharableGlossaryMixin'

    class Media:
        js = ['admin/js/jquery.init.js', 'cascade/js/admin/sharableglossary.js']

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if request.method == 'GET' and request.GET.get('glossary'):
            # Reached after the user changed the shared settings select field.
            # This recreates a form for the given plugin using the selected shared fields
            # as values for a faked object.
            extra_context = dict(extra_context or {})
            sharable_fields = {}
            try:
                shared_glossary = SharedGlossary.objects.get(id=request.GET.get('glossary'))
            except (ValueError, SharedGlossary.DoesNotExist):
                pass
            else:
                for field_name in self.sharable_fields:
                    shared_val = shared_glossary.glossary.get(field_name)
                    if shared_val:
                        sharable_fields[field_name] = shared_val

            if object_id:
                obj = self.get_object(request, object_id)
                glossary = deepcopy(obj.glossary)
                glossary.update(sharable_fields)
                # create fake object using values from shared fields to mimic the expected behaviour
                fake_obj = CascadeElement(glossary=glossary)
                ModelForm = self.get_form(request, fake_obj)
                form = ModelForm(instance=fake_obj)
            else:
                ModelForm = self.get_form(request)
                initial = self.get_changeform_initial_data(request)
                initial.update(sharable_fields)
                form = ModelForm(initial=initial)

            extra_context['adminform'] = AdminForm(
                form,
                list(self.get_fieldsets(request, obj)),
                {},
                [],
                model_admin=self)

        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_form(self, request, obj=None, **kwargs):
        base_form = kwargs.pop('form', self.form)
        assert issubclass(base_form, EntangledModelFormMixin), "The Form class must inherit from EntangledModelFormMixin"
        if request.method == 'GET' and 'glossary' in request.GET:
            FormMixin = SharedFormMixin if request.GET['glossary'] else SharableFormMixin
        else:
            FormMixin = SharedFormMixin if obj and obj.shared_glossary else SharableFormMixin
        kwargs['form'] = type(base_form.__name__, (FormMixin, base_form), {})
        kwargs['form'].base_fields['shared_glossary'].limit_choices_to = dict(plugin_type=self.__class__.__name__)
        try:
            shared_glossary = SharedGlossary.objects.get(id=request.GET.get('glossary'))
        except ValueError:
            shared_glossary = None
        except SharedGlossary.DoesNotExist:
            shared_glossary = obj.shared_glossary if obj else None
        for field_name in self.sharable_fields:
            kwargs['form'].base_fields[field_name].disabled = bool(shared_glossary)
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # in case checkbox for `save_settings_as` is checked, then we create a new entry in `models.SharedGlossary`
        # transferring the fields declared as sharable from this this plugin to that newly created object
        save_settings_as = form.cleaned_data.get('save_settings_as')
        if save_settings_as:
            # move data from form glossary to a SharedGlossary and refer to it
            shared_glossary, created = SharedGlossary.objects.get_or_create(
                plugin_type=self.__class__.__name__,
                identifier=save_settings_as,
            )
            assert created, "SharableCascadeForm.clean_save_settings_as() erroneously validated identifier '{}' " \
                            "as unique".format(save_settings_as)
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
