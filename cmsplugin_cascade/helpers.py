from os import environ
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.utils import flatten_fieldsets
from django.forms import widgets
from cmsplugin_cascade import app_settings
from django.forms import Media
from collections import OrderedDict
    
from django.forms.widgets  import media_property

used_compact_form = True if environ.get('COMPACT_FORM', False) == 'True' else False

traductions_keys_to_title = {
       'background_and_color': _( "Background and color" ),
       'scroll_animate': _( "Scroll Animate" ),
       'custom_css_classes':  _( "Custom css classes" ),
    }

def fieldset_by_widget_attr( form, attr_data_name, cls_media, traductions=traductions_keys_to_title , change_form_template=None):

    """Filter and classed fields with or not group attribute 'data_nested' and create fieldset."""
    nested = {}
    css_appended = [ 'cascade/css/admin/compact_forms/main_compact_form.css', 'cascade/css/admin/cascade_box.css' ]
    fieldsets = ()
    for key, field in form.declared_fields.items():
        if 'data_nested' in field.widget.attrs :
            data_entangled_value = field.widget.attrs[attr_data_name]
            if data_entangled_value == 'background_and_color':
                css_appended.append('cascade/css/admin/compact_forms/bootstrap4-colors.css')

            nested.setdefault(data_entangled_value,[])
            if len(key) > 1:
                nested[data_entangled_value].append(key)
            else:
                nested[data_entangled_value].extend(key)

    if hasattr(cls_media, 'css'):
        if not css_appended[0] in cls_media.css['all']:
            cls_media.css['all'].extend(css_appended)
    else:
        cls_media.css = {
        'all': css_appended
        }
    
    for key_title, fields_lists_str in nested.items():

        if key_title in traductions:
            key_title_trad = traductions[key_title]
        else:
            key_title_trad = key_title

        icon = '{0}-title'.format(key_title)

        if 'link_type' in  fields_lists_str or 'icon_font' in  fields_lists_str or 'button' in  fields_lists_str:
            fieldsets +=( None, {'classes': ('cascade_box',),'fields':((fields_lists_str),), 'description': 
            '<div ><b>{1}</b><br><i class="icon_desc icon-{0}"></i>\
            <br><label><input type="checkbox" id="help" name="help"> Help</label></div>'.format(icon , key_title )}),
        if key_title in ['background_and_color', 'column', 'offset', 'reorder',\
         'responsive', 'floats', 'paddings','margins', 'buttons', 'vertical_margins', 'container']:
            fieldsets +=( None, { 'classes': ['cascade_box', 'nested'], 'fields':((fields_lists_str),),
             'description': '<div class="collapse_help"><b>{1}</b>\
             <br><i class="icon_desc icon-{0}"></i></div>'.format(icon, key_title_trad )}),
       # else:
        if not key_title in ['background_and_color', 'column', 'offset', 'reorder',\
         'responsive', 'floats', 'paddings','margins', 'buttons', 'vertical_margins', 'container']:
            fieldsets +=( None ,{'classes': ['cascade_box_classic',],  'fields':fields_lists_str }),

    extra_fields = OrderedDict.fromkeys(x for x in list(form.declared_fields.keys()) if x not in  flatten_fieldsets(fieldsets))
    if not nested:
        fieldsets +=(None, {'fields':list(extra_fields)}),
    else:
       # fieldsets +=('extra_fields',{'fields':list(extra_fields)}),
        fieldsets +=(None ,{'fields':list(extra_fields)}),
    return  fieldsets, cls_media


def apply_widgets_tpl( field,template_key):
       if template_key == 'select_icon':
          field.widget.template_name = 'cascade/admin/widgets/select_icon.html'
       if template_key == 'button_type':
          field.widget.template_name = 'cascade/admin/compact_forms/widgets/select_icon_button_types.html'
       if template_key == 'width':
          field.widget.template_name = 'cascade/admin/compact_forms/widgets/select_icon_button_types.html'
       if template_key == 'column' or template_key == 'paddings' or template_key == 'margins'   or template_key == 'floats'   or template_key == 'vertical_margins' :
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
