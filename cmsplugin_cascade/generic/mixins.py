from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.forms.fields import CharField
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from entangled.forms import EntangledModelFormMixin
from cmsplugin_cascade import app_settings
from cmsplugin_cascade.models import CascadePage


class SectionFormMixin(EntangledModelFormMixin):
    element_id = CharField(
        label=_("Element ID"),
        max_length=15,
        required=False,
        help_text=_("A unique identifier for this element.")
    )

    class Meta:
        entangled_fields = {'glossary': ['element_id']}

    def clean_element_id(self):
        element_id = self.cleaned_data['element_id']
        self.check_unique_element_id(self.instance, element_id)
        return element_id

    @classmethod
    def check_unique_element_id(cls, instance, element_id):
        """
        Check for uniqueness of the given element_id for the current page.
        Return None if instance is not yet associated with a page.
        """
        try:
            element_ids = instance.placeholder.page.cascadepage.glossary.get('element_ids', {})
        except (AttributeError, ObjectDoesNotExist):
            pass
        else:
            if element_id:
                for key, value in element_ids.items():
                    if str(key) != str(instance.pk) and element_id == value:
                        msg = _("The element ID '{}' is not unique for this page.")
                        raise ValidationError(msg.format(element_id))


class SectionModelMixin(object):
    def element_id(self):
        id_attr = self.glossary.get('element_id')
        if id_attr:
            return '{bookmark_prefix}{0}'.format(id_attr, **app_settings.CMSPLUGIN_CASCADE)

    def delete(self, *args, **kwargs):
        try:
            self.placeholder.page.cascadepage.glossary['element_ids'].pop(str(self.pk))
        except (AttributeError, KeyError, ObjectDoesNotExist):
            pass
        else:
            self.placeholder.page.cascadepage.save()
        super().delete(*args, **kwargs)


class SectionMixin(object):
    def get_form(self, request, obj=None, **kwargs):
        form = kwargs.get('form', self.form)
        assert issubclass(form, EntangledModelFormMixin), "Form must inherit from EntangledModelFormMixin"
        kwargs['form'] = type(form.__name__, (SectionFormMixin, form), {})
        return super().get_form(request, obj, **kwargs)

    @classmethod
    def get_identifier(cls, instance):
        element_id = instance.glossary.get('element_id')
        if element_id:
            return format_html('<code>id="{0}"</code>', element_id)
        return super().get_identifier(instance)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        element_id = obj.glossary['element_id']
        if not change:
            # when adding a new element, `element_id` can not be validated for uniqueness
            postfix = 0
            # check if form simplewarpper has function check_unique_element_id
            if not 'check_unique_element_id' in dir(form):
                form_ = SectionFormMixin
            else:
                form_ = form
            while True:
                try:
                    form_.check_unique_element_id(obj, element_id)
                except ValidationError:
                    postfix += 1
                    element_id = '{element_id}_{0}'.format(postfix, **obj.glossary)
                else:
                    break
            if postfix:
                obj.glossary['element_id'] = element_id
                obj.save()

        cms_page = obj.placeholder.page
        if cms_page:
            # storing the element_id on a placholder only makes sense, if it is non-static
            CascadePage.assure_relation(cms_page)
            cms_page.cascadepage.glossary.setdefault('element_ids', {})
            cms_page.cascadepage.glossary['element_ids'][str(obj.pk)] = element_id
            cms_page.cascadepage.save()
