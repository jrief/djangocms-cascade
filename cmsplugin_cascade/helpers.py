from os import environ
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.utils import flatten_fieldsets
from django.forms import widgets
from cmsplugin_cascade import app_settings

used_compact_form = environ.get('COMPACT_FORM', False)

traductions_keys_to_title = { 
       'background_and_color': _( "Background and color" ),
    }

def fieldset_by_widget_attr( form, attr_data_name, traductions=traductions_keys_to_title):
    nested={}
    for key, field in form.declared_fields.items():
        if 'data_nested' in field.widget.attrs :
            data_entangled_value = field.widget.attrs[attr_data_name]
            if data_entangled_value == 'Colors':
               data_entangled_value = "background_and_color"
            nested.setdefault(data_entangled_value,[])
            nested[data_entangled_value].append(key)
    fieldsets=()
    for key_title, fields_lists_str in nested.items():
        if key_title in traductions:
             key_title = traductions[key_title]
        fieldsets +=( key_title, {'fields':(fields_lists_str),}),
    extra_fields = set(list(form.declared_fields.keys())) - set(flatten_fieldsets(fieldsets))
    fieldsets +=('extra_fields',{'fields':list(extra_fields)}),
    return fieldsets


def entangled_nested(*fields, data_nested=None,template_key=None):
   """
   The Fields are classed by groups key with widget attribute 'data_nested' and set widget template name.
   Used in Compact form mode.
   """
   for field in fields:
       if isinstance(field, dict):
           for field in field.values():
               field.widget.attrs['data_nested']=data_nested
       else:
           field.widget.attrs['data_nested']=data_nested
           if template_key == 'select_icon':
              field.widget.template_name = 'cascade/admin/widgets/selecticon.html'
