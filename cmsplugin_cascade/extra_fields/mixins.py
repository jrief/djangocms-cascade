from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.forms import MediaDefiningClass, widgets
from django.forms.fields import CharField, ChoiceField, MultipleChoiceField
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from entangled.forms import EntangledModelFormMixin
from cmsplugin_cascade import app_settings
from cmsplugin_cascade.fields import SizeField


class ExtraFieldsMixin(metaclass=MediaDefiningClass):
    """
    If a Cascade plugin is listed in ``settings.CMSPLUGIN_CASCADE['plugins_with_extra_fields']``,
    then this ``ExtraFieldsMixin`` class is added automatically to its plugin class in order to
    offer extra fields for customizing CSS classes and styles.
    """

    def __str__(self):
        return self.plugin_class.get_identifier(self)

    def get_form(self, request, obj=None, **kwargs):
        from cmsplugin_cascade.models import PluginExtraFields
        from .config import PluginExtraFieldsConfig

        clsname = self.__class__.__name__
        try:
            site = get_current_site(request)
            extra_fields = PluginExtraFields.objects.get(plugin_type=clsname, site=site)
        except ObjectDoesNotExist:
            extra_fields = app_settings.CMSPLUGIN_CASCADE['plugins_with_extra_fields'].get(clsname)

        if isinstance(extra_fields, (PluginExtraFields, PluginExtraFieldsConfig)):
            form_fields = {}

            # add a text input field to let the user name an ID tag for this HTML element
            if extra_fields.allow_id_tag:
                form_fields['extra_element_id'] = CharField(
                    label=_("Named Element ID"),
                )

            # add a select box to let the user choose one or more CSS classes
            class_names, choices = extra_fields.css_classes.get('class_names'), None
            if isinstance(class_names, (list, tuple)):
                choices = [(clsname, clsname) for clsname in class_names]
            elif isinstance(class_names, str):
                choices = [(clsname, clsname) for clsname in class_names.replace(' ', ',').split(',') if clsname]
            if choices:
                if extra_fields.css_classes.get('multiple'):
                    form_fields['extra_css_classes'] = MultipleChoiceField(
                        label=_("Customized CSS Classes"),
                        choices=choices,
                        required=False,
                        widget=widgets.CheckboxSelectMultiple,
                        help_text=_("Customized CSS classes to be added to this element."),
                    )
                else:
                    choices.insert(0, (None, _("Select CSS")))
                    form_fields['extra_css_classes'] = ChoiceField(
                        label=_("Customized CSS Class"),
                        choices=choices,
                        required=False,
                        help_text=_("Customized CSS class to be added to this element."),
                    )

            # add input fields to let the user enter styling information
            for style, choices_list in app_settings.CMSPLUGIN_CASCADE['extra_inline_styles'].items():
                inline_styles = extra_fields.inline_styles.get('extra_fields:{0}'.format(style))
                if not inline_styles:
                    continue
                Field = choices_list[1]
                for inline_style in inline_styles:
                    key = 'extra_inline_styles:{0}'.format(inline_style)
                    field_kwargs = {
                        'label': '{0}: {1}'.format(style, inline_style),
                        'required': False,
                    }
                    if issubclass(Field, SizeField):
                        field_kwargs['allowed_units'] = extra_fields.inline_styles.get('extra_units:{0}'.format(style)).split(',')
                    form_fields[key] = Field(**field_kwargs)

            # extend the form with some extra fields
            base_form = kwargs.pop('form', self.form)
            assert issubclass(base_form, EntangledModelFormMixin), "Form must inherit from EntangledModelFormMixin"
            class Meta:
                entangled_fields = {'glossary': list(form_fields.keys())}
            form_fields['Meta'] = Meta
            kwargs['form'] = type(base_form.__name__, (base_form,), form_fields)
        return super().get_form(request, obj, **kwargs)

    @classmethod
    def get_css_classes(cls, obj):
        """Enrich list of CSS classes with customized ones"""
        css_classes = super().get_css_classes(obj)
        extra_css_classes = obj.glossary.get('extra_css_classes')
        if extra_css_classes:
            if isinstance(extra_css_classes, str):
                css_classes.append(extra_css_classes)
            elif isinstance(extra_css_classes, (list, tuple)):
                css_classes.extend(extra_css_classes)
        return css_classes

    @classmethod
    def get_inline_styles(cls, obj):
        """Enrich inline CSS styles with customized ones"""
        inline_styles = super().get_inline_styles(obj)
        extra_inline_styles = app_settings.CMSPLUGIN_CASCADE['extra_inline_styles']
        for key, eis in obj.glossary.items():
            if key.startswith('extra_inline_styles:'):
                _, prop = key.split(':')
                if isinstance(eis, dict):
                    # a multi value field, storing values as dict
                    inline_styles.update(dict((k, v) for k, v in eis.items() if v))
                elif isinstance(eis, (list, tuple)):
                    # a multi value field, storing values as list
                    for props, field_class in extra_inline_styles.values():
                        if prop in props:
                            inline_styles.update({prop: field_class.css_value(eis)})
                            break
                elif isinstance(eis, str):
                    inline_styles.update({prop: eis})
        return inline_styles

    @classmethod
    def get_html_tag_attributes(cls, obj):
        attributes = super().get_html_tag_attributes(obj)
        extra_element_id = obj.glossary.get('extra_element_id')
        if extra_element_id:
            attributes.update(id=extra_element_id)
        return attributes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super().get_identifier(obj)
        extra_element_id = obj.glossary and obj.glossary.get('extra_element_id')
        if extra_element_id:
            return format_html('{0}<em>{1}:</em> ', identifier, extra_element_id)
        return identifier
