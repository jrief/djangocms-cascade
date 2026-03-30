from django.forms.fields import ChoiceField
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from cms.models.pluginmodel import CMSPlugin
from cmsplugin_cascade.bootstrap5.breakpoint import Breakpoint
from cmsplugin_cascade.bootstrap5.plugin_base import CascadePluginMetaclass
from cmsplugin_cascade.bootstrap5.fields import AspectRatioChoiceField


class BootstrapUtilities(CascadePluginMetaclass):
    """
    Factory for building a class ``BootstrapUtilitiesMixin``. This class then is used as a mixin to
    all sorts of Bootstrap-5 plugins. Add this utility class to any plugin class by inheriting from
    BootstrapUtilities(…) while declaring the plugin class.
    """

    def __new__(cls, *args):
        class BootstrapUtilitiesMixin:
            def get_model_form(self, **kwargs):
                class Meta(self.form.Meta):
                    fields_map = {
                        **self.form.Meta.fields_map,
                        'glossary': [*self.form.Meta.fields_map['glossary'], *form_fields.keys()],
                    }

                kwargs['form_class'] = type(self.form.__name__, (self.form,), {**form_fields, 'Meta': Meta})
                return super().get_model_form(**kwargs)

            @classmethod
            def get_css_classes(cls, instance):
                css_classes = super().get_css_classes(instance)
                for key in form_fields.keys():
                    if value := instance.glossary.get(key):
                        css_classes.append(value)
                return css_classes

        form_fields = {k: v for arg in args if isinstance(arg, property) for k, v in arg.fget(cls).items()}
        return BootstrapUtilitiesMixin

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
        return {'background_and_color': ChoiceField(
            label=_("Background and color"),
            choices=choices,
            required=False,
            initial='',
        )}

    @property
    def margins(cls):
        form_fields = {}
        choices_format = [
            ('m-{}{}', _("4 sided margins ({})")),
            ('mx-{}{}', _("Horizontal margins ({})")),
            ('my-{}{}', _("Vertical margins ({})")),
            ('mt-{}{}', _("Top margin ({})")),
            ('me-{}{}', _("Right margin ({})")),
            ('mb-{}{}', _("Bottom margin ({})")),
            ('ms-{}{}', _("Left margin ({})")),
        ]
        sizes = list(range(0, 6)) + ['auto']
        previous_label = ''
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
        return form_fields

    @property
    def vertical_margins(cls):
        form_fields = {}
        choices_format = [
            ('my-{}{}', _("Vertical margins ({})")),
            ('mt-{}{}', _("Top margin ({})")),
            ('mb-{}{}', _("Bottom margin ({})")),
        ]
        sizes = list(range(0, 6)) + ['auto']
        previous_label = ''
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
        return form_fields

    @property
    def paddings(cls):
        form_fields = {}
        choices_format = [
            ('p-{}{}', _("4 sided padding ({})")),
            ('px-{}{}', _("Horizontal padding ({})")),
            ('py-{}{}', _("Vertical padding ({})")),
            ('pt-{}{}', _("Top padding ({})")),
            ('pe-{}{}', _("Right padding ({})")),
            ('pb-{}{}', _("Bottom padding ({})")),
            ('ps-{}{}', _("Left padding ({})")),
        ]
        sizes = range(0, 6)
        previous_label = ''
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
        return form_fields

    @property
    def floats(cls):
        form_fields = {}
        choices_format = [
            ('float-{}none', _("Do not float")),
            ('float-{}start', _("Float left")),
            ('float-{}end', _("Float right")),
        ]
        previous_label = ''
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
        return form_fields


class AspectRatioChoicesMixin:
    """
    A mixin class to be added to a plugin inheriting from ``BootstrapPluginBase``. It extends the plugin's editor
    form with aspect ratio choices for each breakpoint defined in the plugin's glossary.
    """

    def get_model_form(self, **kwargs):
        if self.object:
            breakpoints = self.get_breakpoints(self.object)
        elif 'plugin_parent' in self.request.GET:
            breakpoints = self.get_breakpoints(CMSPlugin.objects.get(pk=self.request.GET['plugin_parent']))
        else:
            breakpoints = []
        if 'xs' in breakpoints:
            breakpoints.remove('xs')

        model_form = super().get_model_form(**kwargs)
        glossary_fields = list(model_form.Meta.fields_map['glossary'])
        attrs, prev_bp = {}, 'xs'
        for index, bp in enumerate(breakpoints, glossary_fields.index('aspect_ratio') + 1):
            if bp == 'xs':
                continue
            field_name = f'aspect_ratio_{bp}'
            attrs[field_name] = AspectRatioChoiceField(
                Breakpoint[bp],
                required=False,
                add_original=model_form.base_fields['aspect_ratio'].add_original,
                empty_label=_("Inherit from “Aspect Ratio for ‘{}’”").format(Breakpoint[prev_bp].label),
            )
            glossary_fields.insert(index, field_name)

        attrs['Meta'] = type('Meta', (model_form.Meta,), {
            'fields_map': {'glossary': glossary_fields},
        })
        model_form = type(model_form.__name__, model_form.__mro__, attrs)
        return model_form


VerticalMarginsMixin = BootstrapUtilities(BootstrapUtilities.vertical_margins)
