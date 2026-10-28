from django.forms.fields import CharField
from django.utils.translation import gettext_lazy as _

from cmsplugin_cascade.models import CascadeElement

from formset.forms import ModelForm


class ManageChildrenFormMixin:
    """
    Classes derived from ``CascadePluginBase`` can optionally add this mixin class to their form,
    offering the input field ``num_children`` in their plugin editor. The content of this field is
    not persisted in the plugin's model.
    It allows the client to modify the number of children attached to this plugin.
    """
    class Meta:
        fields = ['num_children']
        fields_map = {'glossary': ['num_children']}

    def get_initial_for_field(self, field, field_name: str):
        if field_name == 'num_children':
            return self.instance.get_num_children()
        return super().get_initial_for_field(field, field_name)


class InternalTitleModelForm(ModelForm):
    title_attribute = CharField(
        label=_("Internal Title"),
        required=False,
        help_text=_("Internal title attribute to organize components in the structure editor."),
    )

    class Meta:
        model = CascadeElement
        exclude = ['shared_glossary']
        fields_map = {'glossary': ['title_attribute']}
