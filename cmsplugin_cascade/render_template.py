from django.forms import MediaDefiningClass
from django.forms.fields import ChoiceField
from django.utils.six import with_metaclass
from django.utils.translation import ugettext_lazy as _
from django.template.loader import get_template, TemplateDoesNotExist
from entangled.forms import EntangledModelFormMixin
from cmsplugin_cascade import app_settings


class RenderTemplateFormMixin(EntangledModelFormMixin):
    render_template = ChoiceField(
        label=_("Render template"),
        help_text=_("Use alternative template for rendering this plugin."),
    )

    class Meta:
        entangled_fields = {'glossary': ['render_template']}


class RenderTemplateMixin(with_metaclass(MediaDefiningClass)):
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
        kwargs['form'] = type(form.__name__, (RenderTemplateFormMixin, form), {})
        kwargs['form'].base_fields['render_template'].choices = self.get_template_choices()
        return super().get_form(request, obj, **kwargs)

    def get_render_template(self, context, instance, placeholder):
        try:
            template = instance.glossary.get('render_template', self.get_template_choices()[0][0])
            get_template(template)  # check if template exists
        except (KeyError, IndexError, TemplateDoesNotExist):
            template = super().get_render_template(context, instance, placeholder)
        return template
