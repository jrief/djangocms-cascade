from django.forms.fields import ChoiceField
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _
from entangled.forms import EntangledModelFormMixin
from cmsplugin_cascade.utils import CascadeUtilitiesMixin
from cmsplugin_cascade.bootstrap4.grid import Breakpoint
from cmsplugin_cascade.widget import SelectIconWidget
from django.contrib.admin.utils import flatten
from cmsplugin_cascade import app_settings

class GenericUtilities(type):
    """
    Factory for building a class ``GenericUtilitiesMixin``. This class then is used as a mixin to
    all sorts of generic plugins. Various plugins are shipped using this mixin class
    in different configurations. These configurations can be overridden through the project's
    settings using:
    ```
    CMSPLUGIN_CASCADE['plugins_with_extra_mixins'] = {
        'Bootstrap<ANY>Plugin': GenericUtilities(
            GenericUtilities.scroll_animate,
            …
        ),
        …
    }
    ```

    The class ``GenericUtilities`` offers a bunch of property methods which return a list of
    input fields and/or select boxes. They then can be added to the plugin's editor. 
    Specficed with attritbute in property methods 'attrs_type' with two possible values 'css_classes' or 'html_data_attrs'
    Html data attribute need some time anchors of current page.
    form_fields has reserved string '#anchors' used with choices='#anchors', after the form request anchor of element_ids
    are disponible in choicesfields.
    """
    def __new__(cls, *args):
        form_fields = {}
        form_fields_by_property_name = {}
        form_fields_by_attr_type = {}
        fields_choices_anchors = []

        for arg in args:
            if isinstance(arg, property):
                property_fields=arg.fget(cls)
                form_subfields = property_fields['form_fields']
                attrs_type = property_fields['attrs_type']
                property_name = property_fields['property_name']

                form_fields.update(form_subfields)
                form_fields_by_property_name[property_name]= property_fields['form_fields']
                form_fields_by_attr_type.setdefault(attrs_type, [])
                form_fields_by_attr_type[attrs_type ].extend(property_fields['form_fields'].keys())
                if 'anchors_fields' in  property_fields:
                    fields_choices_anchors.extend(property_fields['anchors_fields'])

        class Meta:
            entangled_fields = {'glossary': list(form_fields.keys())}

        utility_form_mixin = type('UtilitiesFormMixin', (EntangledModelFormMixin,), dict(form_fields, Meta=Meta) )
        return type('GenericUtilitiesMixin', (CascadeUtilitiesMixin,), {'utility_form_mixin': utility_form_mixin,
                     'attr_type': form_fields_by_attr_type , 'fields_with_choices_anchors': fields_choices_anchors })

    @property
    def scroll_animate(cls):
        form_fields = {}
        attrs_type = 'html_data_attrs'
        property_name = 'scroll_animate'

        choices_data_sal = [
            ('inherit', _("inherit")),
            ('fade', _("fade")),
            ('slide-up', _("slide-up")),
            ('slide-down', _("slide-down")),
            ('slide-left', _("slide-left")),
            ('slide-right', _("slide-right")),
            ('zoom-in', _("zoom-in")),
            ('zoom-out', _("zoom-out")),
            ('flip-up', _("flip-up")),
            ('flip-down', _("flip-down")),
            ('zoom-out', _("zoom-out")),
            ('flip-up', _("flip-up")),
            ('flip-right', _("flip-right")),
        ]

        choices_data_sal_delay= list((c, c) for c in ["inherit"] + [ i for i in range(0, 2100, 100)])
        choices_data_sal_easing= [
            ('ease', _("ease")),
            ('ease-in-out-back', _("ease-in-out-back")),
            ('ease-out-back', _("ease-out-back")),
            ('ease-in-out-sine', _("ease-in-out-sine")),
            ('ease-in-quad', _("ease-in-quad")),
        ]
        form_fields['data-sal'] = ChoiceField(
                        label=_("Scroll effects"),
                        choices=choices_data_sal,
                        required=False,
                        widget=SelectIconWidget(choices=get_widget_choices(choices_data_sal), attrs={'data_entangled':'Scroll_animate'}), 
                        initial='',
                    )
        form_fields['data-sal-delay'] = ChoiceField(
                        label=_("Delay effect"),
                        choices= choices_data_sal_delay,
                        required=False,
                        initial='',
                        help_text='Delay in milliseconde',
                    )
        attrs={'data_entangled':'Scroll_animate'}
        form_fields['data-sal-delay'].widget.attrs = {**attrs }
        form_fields['data-sal-easing'] = ChoiceField(
                        label=_("Animation type"),
                        choices=choices_data_sal_easing,
                        widget=SelectIconWidget(choices=get_widget_choices(choices_data_sal_easing), attrs={'data_entangled':'Scroll_animate'}), 
                        required=False,
                        initial='',
                    )
        return { 'form_fields':form_fields, 'attrs_type': attrs_type, 'property_name':property_name }
