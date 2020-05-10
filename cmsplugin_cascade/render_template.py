from django.forms import MediaDefiningClass
from django.forms.fields import ChoiceField
from django.utils.translation import gettext_lazy as _
from django.template.loader import get_template, TemplateDoesNotExist
from entangled.forms import EntangledModelFormMixin
from cmsplugin_cascade import app_settings


class RenderTemplateFormMixin(EntangledModelFormMixin):
    render_template = ChoiceField(
        label=_("Render template"),
        help_text=_("Use alternative template for rendering this plugin."),
        required=False,
    )

    class Meta:
        entangled_fields = {'glossary': ['render_template']}


class RenderTemplateMixin(metaclass=MediaDefiningClass):
    """
    If a Cascade plugin is listed in ``settings.CMSPLUGIN_CASCADE['plugins_with_extra_render_templates']``,
    then this ``RenderTemplateMixin`` class is added automatically to its plugin class in order
    to add an additional select box used for choosing an alternative render template.
    """
    @classmethod
    def get_template_choices(cls):
        return app_settings.CMSPLUGIN_CASCADE['plugins_with_extra_render_templates'][cls.__name__]

    def get_form(self, request, obj=None, **kwargs):
        form = kwargs.get('form', self.form)
        assert issubclass(form, EntangledModelFormMixin), "Form must inherit from EntangledModelFormMixin"
        choices = self.get_template_choices()
        if isinstance(choices, (list, tuple)):
            form = type(form.__name__, (RenderTemplateFormMixin, form), {})
            form.base_fields['render_template'].choices = choices
            kwargs['form'] = form
        return super().get_form(request, obj, **kwargs)

    def get_render_template(self, context, instance, placeholder):
        try:
            template = instance.glossary.get('render_template', self.get_template_choices()[0][0])
            get_template(template)  # check if template exists
        except (KeyError, IndexError, TemplateDoesNotExist, TypeError):
            template = self.render_template
        return template
