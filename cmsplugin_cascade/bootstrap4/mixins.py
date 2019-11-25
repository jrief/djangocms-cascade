from django.forms.fields import ChoiceField
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _
from entangled.forms import EntangledModelFormMixin
from cmsplugin_cascade.utils import CascadeUtilitiesMixin
from cmsplugin_cascade.bootstrap4.grid import Breakpoint


class BootstrapUtilities(type):
    """
    The class ``BootstrapUtilities`` offers a bunch of property methods which return a list of
    input fields and/or select boxes. They then can be added to the plugin's editor. This is
    specially useful to add CSS classes or HTML data attributes from the utilities section of Bootstrap-4, such as
    margins, borders, colors, etc.
    The 'property_name' attritbute in property methods is needed because python property methods don't have name
    attributes without using inspect module or others things. 
    The 'attrs_type' attritbute in property methods can have two possiblity values 'css_classes' or 'html_data_attrs'.
    The 'anchors_fields' in the property_fields attributes can add choices id elements of the current page, theses choices are realy set
    when the request is available.
    """
    def __new__(cls, *args,):
        form_fields = {}
        form_fields_by_property_name = {}
        form_fields_by_attr_type = {}
        fields_choices_anchors = []

        for arg in args:
            if isinstance(arg, property):
                property_fields=arg.fget(cls)
                form_subfields = property_fields['form_fields']
                attrs_type  = property_fields['attrs_type']
                property_name = property_fields['property_name']
 
                form_fields_by_attr_type.setdefault(attrs_type, [])
                form_fields_by_property_name.setdefault(property_name, [])
                
                form_fields.update(form_subfields)
                form_fields_by_property_name[property_name].extend(property_fields['form_fields'].keys())
                form_fields_by_attr_type[attrs_type ].extend(property_fields['form_fields'].keys())
                if 'anchors_fields' in  property_fields:
                    fields_choices_anchors.extend(property_fields['anchors_fields'])
        class Meta:
            entangled_fields = {'glossary': [values for values in form_fields_by_property_name.values()] }

        utility_form_mixin = type('UtilitiesFormMixin', (EntangledModelFormMixin,), dict(form_fields, Meta=Meta) )
        return type('HtmlAttrsUtilitiesMixin', (CascadeUtilities2Mixin,), {'utility_form_mixin': utility_form_mixin, 'attr_type': form_fields_by_attr_type , 'fields_with_choices_anchors': fields_choices_anchors })

    @property
    def background_and_color(cls):
        attrs_type = 'css_classes'
        property_name = 'background_and_color'
        choices = [
            ('', _("Default")),
            ('bg-primary text-white', _("Primary with white text")),
            ('bg-secondary text-white', _("Secondary with white text")),
            ('bg-success text-white', _("Success with white text")),
            ('bg-danger text-white', _("Danger with white text")),
            ('bg-warning text-white', _("Warning with white text")),
            ('bg-info text-white', _("Info with white text")),
            ('bg-light text-dark', _("Light with dark text")),
            ('bg-dark text-white', _("Dark with white text")),
            ('bg-white text-dark', _("White with dark text")),
            ('bg-transparent text-dark', _("Transparent with dark text")),
            ('bg-transparent text-white', _("Transparent with white text")),
        ]
        form_fields = {'background_and_color': ChoiceField(
            label=_("Background and color"),
            choices=choices,
            required=False,
            initial='',
        )}
        property_fields = { 'form_fields':form_fields, 'attrs_type': attrs_type, 'property_name':property_name }
        return property_fields 

    @property
    def margins(cls):
        attrs_type = 'css_classes'
        property_name = 'margins'
        form_fields = {}
        choices_format = [
            ('m-{}{}', _("4 sided margins ({})")),
            ('mx-{}{}', _("Horizontal margins ({})")),
            ('my-{}{}', _("Vertical margins ({})")),
            ('mt-{}{}', _("Top margin ({})")),
            ('mr-{}{}', _("Right margin ({})")),
            ('mb-{}{}', _("Bottom margin ({})")),
            ('ml-{}{}', _("Left margin ({})")),
        ]
        sizes = list(range(0, 6)) + ['auto']
        for bp in Breakpoint:
            if bp == Breakpoint.xs:
                choices = [(c.format('', s), format_lazy(l, s)) for c, l in choices_format for s in sizes]
                choices.insert(0, ('', _("No Margins")))
            else:
                choices = [(c.format(bp.name + '-', s), format_lazy(l, s)) for c, l in choices_format for s in sizes]
                choices.insert(0, ('', format_lazy(_("Inherit margin from {}"), previous_label)))
            previous_label = bp.label
            form_fields['margins_{}'.format(bp.name)] = ChoiceField(
                label=format_lazy(_("Margins for {breakpoint}"), breakpoint=bp.label),
                choices=choices,
                required=False,
                initial='',
            )
        property_fields = { 'form_fields':form_fields, 'attrs_type': attrs_type, 'property_name':property_name }
        return property_fields 

    @property
    def vertical_margins(cls):
        attrs_type = 'css_classes'
        property_name = 'vertical_margins'
        form_fields = {}
        choices_format = [
            ('my-{}{}', _("Vertical margins ({})")),
            ('mt-{}{}', _("Top margin ({})")),
            ('mb-{}{}', _("Bottom margin ({})")),
        ]
        sizes = list(range(0, 6)) + ['auto']
        for bp in Breakpoint:
            if bp == Breakpoint.xs:
                choices = [(c.format('', s), format_lazy(l, s)) for c, l in choices_format for s in sizes]
                choices.insert(0, ('', _("No Margins")))
            else:
                choices = [(c.format(bp.name + '-', s), format_lazy(l, s)) for c, l in choices_format for s in sizes]
                choices.insert(0, ('', format_lazy(_("Inherit margin from {}"), previous_label)))
            previous_label = bp.label
            form_fields['margins_{}'.format(bp.name)] = ChoiceField(
                label=format_lazy(_("Margins for {breakpoint}"), breakpoint=bp.label),
                choices=choices,
                required=False,
                initial='',
            )
        property_fields = { 'form_fields':form_fields, 'attrs_type': attrs_type, 'property_name':property_name }
        return property_fields 

    @property
    def paddings(cls):
        attrs_type = 'css_classes'
        property_name = 'paddings'
        form_fields = {}
        choices_format = [
            ('p-{}{}', _("4 sided padding ({})")),
            ('px-{}{}', _("Horizontal padding ({})")),
            ('py-{}{}', _("Vertical padding ({})")),
            ('pt-{}{}', _("Top padding ({})")),
            ('pr-{}{}', _("Right padding ({})")),
            ('pb-{}{}', _("Bottom padding ({})")),
            ('pl-{}{}', _("Left padding ({})")),
        ]
        sizes = range(0, 6)
        for bp in Breakpoint:
            if bp == Breakpoint.xs:
                choices = [(c.format('', s), format_lazy(l, s)) for c, l in choices_format for s in sizes]
                choices.insert(0, ('', _("No Padding")))
            else:
                choices = [(c.format(bp.name + '-', s), format_lazy(l, s)) for c, l in choices_format for s in sizes]
                choices.insert(0, ('', format_lazy(_("Inherit padding from {}"), previous_label)))
            previous_label = bp.label
            form_fields['padding_{}'.format(bp.name)] = ChoiceField(
                label=format_lazy(_("Padding for {breakpoint}"), breakpoint=bp.label),
                choices=choices,
                required=False,
                initial='',
            )
        property_fields = { 'form_fields':form_fields, 'attrs_type': attrs_type, 'property_name':property_name }
        return property_fields 

    @property
    def floats(cls):
        form_fields = {}
        attrs_type = 'css_classes'
        property_name = 'floats'
        choices_format = [
            ('float-{}none', _("Do not float")),
            ('float-{}left', _("Float left")),
            ('float-{}right', _("Float right")),
        ]
        for bp in Breakpoint:
            if bp == Breakpoint.xs:
                choices = [(c.format(''), l) for c, l in choices_format]
                choices.insert(0, ('', _("Unset")))
            else:
                choices = [(c.format(bp.name + '-'), l) for c, l in choices_format]
                choices.insert(0, ('', format_lazy(_("Inherit float from {}"), previous_label)))
            previous_label = bp.label
            form_fields['float_{}'.format(bp.name)] = ChoiceField(
                label=format_lazy(_("Floats for {breakpoint}"), breakpoint=bp.label),
                choices=choices,
                required=False,
                initial='',
            )
        property_fields = { 'form_fields':form_fields, 'attrs_type': attrs_type, 'property_name':property_name }
        return property_fields 
