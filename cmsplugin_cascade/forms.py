from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.models import ModelForm

from entangled.forms import EntangledModelFormMixin, EntangledModelForm


class ManageChildrenFormMixin:
    """
    Classes derived from ``CascadePluginBase`` can optionally add this mixin class to their form,
    offering the input field ``num_children`` in their plugin editor. The content of this field is
    not persisted in the plugin's model.
    It allows the client to modify the number of children attached to this plugin.
    """
    class Meta:
        fields = ['num_children']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = {'num_children': instance.get_num_children()}
            kwargs.update(initial=initial)
        super().__init__(*args, **kwargs)


class CascadeModelFormMixin(EntangledModelFormMixin):
    """
    Classes inheriting from InlineAdmin and defining their own `form` shall use this special
    variant of an `EntangledModelForm`, otherwise deletion of inlined elements does not work.
    """
    def _clean_form(self):
        internal_fields = ['cascade_element', 'id', DELETION_FIELD_NAME]
        internal_cleaned_data = {key: val for key, val in self.cleaned_data.items() if key in internal_fields}
        super()._clean_form()
        self.cleaned_data.update(internal_cleaned_data)


class CascadeModelForm(CascadeModelFormMixin, ModelForm):
    """
    A convenience class to create a ModelForms to be used with djangocms-cascade
    """
