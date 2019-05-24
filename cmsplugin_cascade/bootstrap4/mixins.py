from django.forms import MediaDefiningClass, widgets
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.bootstrap4.grid import Breakpoint


class BootstrapUtilitiesMixin(metaclass=MediaDefiningClass):
    """
    If a Cascade plugin is listed in ``settings.CMSPLUGIN_CASCADE['plugins_with_extra_mixins']``,
    then this ``BootstrapUtilsMixin`` class is added automatically to its plugin class in order to
    enrich it with utility classes offered by Bootstrap-4.
    """
    def __str__(self):
        return self.plugin_class.get_identifier(self)

    @classmethod
    def get_css_classes(cls, obj):
        """Enrich list of CSS classes with customized ones"""
        css_classes = super(BootstrapUtilitiesMixin, cls).get_css_classes(obj)
        for utility_field_name in cls.utility_field_names:
            css_classes.append(obj.glossary.get(utility_field_name))
        return css_classes


class BootstrapUtilities(type):
    """
    Factory for building a class ``BootstrapUtilitiesMixin``. This class then is used as a mixin to
    all sorts of Bootstrap-4 plugins. Various Bootstrap-4 plugins are shipped using this mixin class
    in different configurations. These configurations can be overridden through the project's
    settings using:
    ```
    CMSPLUGIN_CASCADE['plugins_with_extra_mixins'] = {
        'Bootstrap<ANY>Plugin': BootstrapUtilities(
            BootstrapUtilities.background_and_color,
            BootstrapUtilities.margins,
            BootstrapUtilities.paddings,
            …
        ),
        …
    }
    ```

    The class ``BootstrapUtilities`` offers a bunch of property methods which return a list of
    input fields and/or select boxes. They then can be added to the plugin's editor. This is
    specially useful to add CSS classes from the utilities section of Bootstrap-4, such as
    margins, borders, colors, etc.
    """
    def __new__(cls, *args):
        glossary_fields = []
        for arg in args:
            if isinstance(arg, property):
                arg = arg.fget(cls)
            if isinstance(arg, (list, tuple)):
                glossary_fields.extend([gf for gf in arg if isinstance(gf, GlossaryField)])
            elif isinstance(arg, GlossaryField):
                glossary_fields.append(arg)
        attrs = {'glossary_fields': glossary_fields, 'utility_field_names': [gf.name for gf in glossary_fields]}
        return type(BootstrapUtilitiesMixin.__name__, (BootstrapUtilitiesMixin,), attrs)

    @property
    def background_and_color(cls):
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
        return GlossaryField(
            widgets.Select(choices=choices),
            label=_("Background and color"),
            name='background_and_color',
            initial=''
        )

    @property
    def margins(cls):
        glossary_fields = []
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
        for bp in Breakpoint.range(Breakpoint.xs, Breakpoint.xl):
            if bp == Breakpoint.xs:
                choices = [(c.format('', s), format_lazy(l, s)) for c, l in choices_format for s in sizes]
                choices.insert(0, ('', _("No Margins")))
            else:
                choices = [(c.format(bp.name + '-', s), format_lazy(l, s)) for c, l in choices_format for s in sizes]
                choices.insert(0, ('', _("Inherit from above")))
            glossary_fields.append(GlossaryField(
                widgets.Select(choices=choices),
                label=format_lazy(_("Margins for {breakpoint}"), breakpoint=bp.label),
                name='margins_{}'.format(bp.name),
                initial=''
            ))
        return glossary_fields

    @property
    def paddings(cls):
        glossary_fields = []
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
        for bp in Breakpoint.range(Breakpoint.xs, Breakpoint.xl):
            if bp == Breakpoint.xs:
                choices = [(c.format('', s), format_lazy(l, s)) for c, l in choices_format for s in sizes]
                choices.insert(0, ('', _("No Padding")))
            else:
                choices = [(c.format(bp.name + '-', s), format_lazy(l, s)) for c, l in choices_format for s in sizes]
                choices.insert(0, ('', _("Inherit from above")))
            glossary_fields.append(GlossaryField(
                widgets.Select(choices=choices),
                label=format_lazy(_("Padding for {breakpoint}"), breakpoint=bp.label),
                name='padding_{}'.format(bp.name),
                initial=''
            ))
        return glossary_fields

    @property
    def flex_directions(cls):
        glossary_fields = []
        choices_format = [
            ('flex-{}row', _("horizontal")),
            ('flex-{}row-reverse', _("horizontal reverse")),
            ('flex-{}column', _("Vertical")),
            ('flex-{}column-reverse', _("Vertical reverse")),
        ]
        for bp in Breakpoint.range(Breakpoint.xs, Breakpoint.xl):
            if bp == Breakpoint.xs:
                choices = [(c.format(''),  l ) for c, l in choices_format]
                choices.insert(0, ('', _("No Flex Directions")))
            else:
                choices = [(c.format(bp.name + '-'), l) for c, l in choices_format ]
                choices.insert(0, ('', _("Inherit from above")))
            glossary_fields.append(GlossaryField(
                widgets.Select(choices=choices),
                label=format_lazy(_("Flex Directions for {breakpoint}"), breakpoint=bp.label),
                name='Flex_{}'.format(bp.name),
                initial=''
            ))
        return glossary_fields

    @property
    def display_propertys(cls):
        glossary_fields = []
        choices_format = [
            ('d-{}{}', _("horizontal")),
        ]
        notation = ['none', 'inline', 'inline-block', 'block', 'table', 'table-cell', 'table-row', 'flex', 'inline-flex']
        for bp in Breakpoint.range(Breakpoint.xs, Breakpoint.xl):
            if bp == Breakpoint.xs:
                choices = [(c.format('',  n), c.format('',  n)) for c, l in choices_format for n in notation]
                choices.insert(0, ('', _("No Flex Directions")))
            else:
                choices = [(c.format(bp.name + '-',  n), 
                   c.format('',  n)) for c, l in choices_format for n in notation]
                choices.insert(0, ('', _("Inherit from above")))
            glossary_fields.append(GlossaryField(
                widgets.Select(choices=choices),
                label=format_lazy(_("Flex Directions for {breakpoint}"), breakpoint=bp.label),
                name='Flex_{}'.format(bp.name),
            ))
        return glossary_fields

    @property
    def justify_content(cls):
        glossary_fields = []
        choices_format = [
            ('justify-content-{}{}', _("Justify Content")),
        ]
        notation = [ 'start', 'end', 'center', 'between', 'around']
        for bp in Breakpoint.range(Breakpoint.xs, Breakpoint.xl):
            if bp == Breakpoint.xs:
                choices = [(c.format('',  n), c.format('',  n)) for c, l in choices_format for n in notation]
                choices.insert(0, ('', _("No Justify content")))
            else:
                choices = [(c.format(bp.name + '-',  n), 
                   c.format(bp.name + '-',  n)) for c, l in choices_format for n in notation]
                choices.insert(0, ('', _("Inherit from above")))
            glossary_fields.append(GlossaryField(
                widgets.Select(choices=choices),
                label=format_lazy(_("Justify Content for {breakpoint}"), breakpoint=bp.label),
                name='Justify_content_{}'.format(bp.name),
            ))
        return glossary_fields

    def floats(cls):
        glossary_fields = []
        choices_format = [
            ('float-{}none', _("Do not float")),
            ('float-{}left', _("Float left")),
            ('float-{}right', _("Float right")),
        ]
        for bp in Breakpoint.range(Breakpoint.xs, Breakpoint.xl):
            if bp == Breakpoint.xs:
                choices = [(c.format(''), l) for c, l in choices_format]
                choices.insert(0, ('', _("Unset")))
            else:
                choices = [(c.format(bp.name + '-'), l) for c, l in choices_format]
                choices.insert(0, ('', _("Inherit from above")))
            glossary_fields.append(GlossaryField(
                widgets.Select(choices=choices),
                label=format_lazy(_("Floats for {breakpoint}"), breakpoint=bp.label),
                name='float_{}'.format(bp.name),
                initial=''
            ))
        return glossary_fields
