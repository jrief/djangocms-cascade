from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.utils import flatten_fieldsets

traductions_keys_to_title = { 
       'background_and_color': _( "Background and color" ),
    }

def fieldset_by_widget_attr( form, attr_data_name, traductions=traductions_keys_to_title):
    nested={}
    for key, field in form.declared_fields.items():
        if 'data_entangled' in field.widget.attrs :
            data_entangled_value = field.widget.attrs[attr_data_name]
            if data_entangled_value == 'Colors':
               data_entangled_value = "background_and_color"
            nested.setdefault(data_entangled_value,[])
            nested[data_entangled_value].append(key)
    fieldsets=()
    for key_title, fields_lists_str in nested.items():
        if key_title in traductions:
             key_title = traductions[key_title]
        fieldsets +=( key_title, {'fields':((fields_lists_str),),}),
    extra_fields = set(list(form.declared_fields.keys())) - set(flatten_fieldsets(fieldsets))
    fieldsets +=('extra_fields',{'fields':list(extra_fields)}),
    return fieldsets
