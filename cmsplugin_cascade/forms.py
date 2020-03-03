
class ManageChildrenFormMixin(object):
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


class ManageNestedFormMixin(object):
    """
    Classes derived from ``CascadePluginBase`` can optionally add this mixin class to their form,
    offering initial data (instance.glossary) of form nested.
    """
    def __init__(self, *args, **kwargs,):
        instance = kwargs.get('instance')
        if instance:
           for field_name, field in self.base_fields.items():
               if len(field_name.split('.')) == 2:
                   tenant_nested, field_nested = field_name.split('.')
                   if tenant_nested in instance.glossary and field_nested in instance.glossary[tenant_nested]:
                       field.initial = instance.glossary[tenant_nested][field_nested]
        super().__init__(*args, **kwargs)

