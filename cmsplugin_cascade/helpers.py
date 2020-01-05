from os import environ
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.utils import flatten_fieldsets
from django.forms import widgets
from cmsplugin_cascade import app_settings
from django.forms import Media

    
from django.forms.widgets  import media_property

used_compact_form = True if environ.get('COMPACT_FORM', False) == 'True' else False

traductions_keys_to_title = {
       'background_and_color': _( "Background and color" ),
    }


def fieldset_by_widget_attr( form, attr_data_name, cls_media, traductions=traductions_keys_to_title , change_form_template=None):
    """Filter and classed fields with or not group attribute 'data_nested' and create fieldset."""
    nested={}
    css_appended = [  'cascade/css/admin/compact_forms/main_compact_form.css', 'cascade/css/admin/cascade_box.css' ]
    for key, field in form.declared_fields.items():

        if 'data_nested' in field.widget.attrs :
            data_entangled_value = field.widget.attrs[attr_data_name]
            if data_entangled_value == 'background_and_color':
                css_appended.append('cascade/css/admin/compact_forms/bootstrap4-colors.css')
            """
            if data_entangled_value == 'Colors':
                data_entangled_value = "background_and_color"
            if data_entangled_value == 'Margins':
                data_entangled_value = "margins"
            if data_entangled_value == 'Paddings':
                data_entangled_value = "paddings"
            if data_entangled_value == 'Border Radius':
                data_entangled_value = "Border"
            if data_entangled_value == 'button':
            """
            nested.setdefault(data_entangled_value,[])
            if len(key) > 1:
                nested[data_entangled_value].append(key)
            else:
                nested[data_entangled_value].extend(key)

    if hasattr(cls_media, 'css'):
        cls_media.css['all'].extend(css_appended)
    else:
        cls_media.css = {
        'all': css_appended
        }

    fieldsets = ()
    
    for key_title, fields_lists_str in nested.items():
        icon=""
        if key_title in 'column':
            icon = 'col-title'
        elif key_title in 'reorder':
            icon = 'order-title'
        elif 'responsive' in key_title:
            icon = 'visible'
        elif 'background_and_color' in key_title:
            icon = 'bg-title'
        elif 'floats' in key_title:
            icon = 'float-title'
        elif 'margins' in key_title:
            icon = 'm-title'
        elif 'paddings' in key_title:
            icon = 'p-title'
        else:
            icon = '{0}-title'.format(key_title)
        if key_title in traductions:
            key_title = traductions[key_title]

        if 'link_type' in  fields_lists_str or 'icon_font' in  fields_lists_str or 'button' in  fields_lists_str:
            fieldsets +=( None, {'fields':(fields_lists_str,), 'description':  '<div ><b>{1}</b><br><i class="icon_desc icon-{0}"></i></div>'.format(icon , key_title )}),
        else:
            fieldsets +=( None, {'fields':((fields_lists_str),), 'description': '<div ><b>{1}</b><br><i class="icon_desc icon-{0}"></i></div>'.format(icon, key_title )}),
    extra_fields = set(list(form.declared_fields.keys())) - set(flatten_fieldsets(fieldsets))
    if not nested:
        fieldsets +=(None, {'fields':list(extra_fields)}),
    else:
        fieldsets +=('extra_fields',{'fields':list(extra_fields)}),
    return  fieldsets, cls_media


def apply_widgets_tpl( field,template_key):
       if template_key == 'select_icon':
          field.widget.template_name = 'cascade/admin/widgets/select_icon.html'
       if template_key == 'button_type':
          field.widget.template_name = 'cascade/admin/compact_forms/widgets/select_icon_button_types.html'
       if template_key == 'width':
          field.widget.template_name = 'cascade/admin/compact_forms/widgets/select_icon_button_types.html'
       if template_key == 'column' or template_key == 'paddings' or template_key == 'margins'   or template_key == 'floats' :
          field.widget.template_name = 'cascade/admin/compact_forms/widgets/select_icon_columns.html'
       if template_key == 'background_and_color':
          field.widget.template_name = 'cascade/admin/compact_forms/widgets/select_icon_colors.html'


def entangled_nested(*fields, data_nested=None,template_key=None):
   """
   The Fields are classed by groups key with widget attribute 'data_nested' and set widget template name.
   Used in Compact form mode.
   """
   for index, field in enumerate(fields):
       if isinstance(field, dict):
           for index_sub, field in enumerate(field.values()):
               field.widget.attrs['data_nested'] = data_nested
               field.widget.attrs['pk'] = index
               apply_widgets_tpl(field, template_key)
               index += 1
       else:
           field.widget.attrs['data_nested'] = data_nested
           field.widget.attrs['pk'] = index
           apply_widgets_tpl(field, template_key)
