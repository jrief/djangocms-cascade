from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.forms.fields import RegexField
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from entangled.forms import EntangledModelFormMixin
from cmsplugin_cascade import app_settings
from cmsplugin_cascade.models import CascadePageContent


def identifier_validator(value):
    if not value:
        return
    valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    for c in value:
        if c not in valid_chars:
            msg = _("The element ID '{}' contains invalid characters.")
            raise ValidationError(msg.format(value))


class SectionFormMixin(EntangledModelFormMixin):
    element_id = RegexField(
        r'^[0-9A-Za-z_.~-]+$',
        label=_("Id"),
        max_length=30,
        required=False,
        help_text=_("A unique identifier for this element (please don't use any special characters, punctuations, etc.) May be used as anchor-link: #id."),
        validators=[identifier_validator],
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
        if not element_id:
            return
        try:
            page_content = instance.placeholder.content_type.get_object_for_this_type(pk=instance.placeholder.object_id)
            element_ids = page_content.cascadepagecontent.glossary['element_ids']
        except (AttributeError, KeyError, CascadePageContent.DoesNotExist):
            return
        else:
            for key, value in element_ids.items():
                if str(key) != str(instance.pk) and element_id == value:
                    msg = _("The element ID '{}' is not unique for this page.")
                    raise ValidationError(msg.format(element_id))


class SectionModelMixin:
    def element_id(self):
        id_attr = self.glossary.get('element_id')
        if id_attr:
            return '{bookmark_prefix}{0}'.format(id_attr, **app_settings.CMSPLUGIN_CASCADE)

    def copy_relations(self, oldinstance):
        try:
            old_placeholder = oldinstance.placeholder
            old_page_content = old_placeholder.content_type.get_object_for_this_type(pk=old_placeholder.object_id)
            element_ids = old_page_content.cascadepagecontent.glossary['element_ids']
            page_content = self.placeholder.content_type.get_object_for_this_type(pk=self.placeholder.object_id)
            cascade_page_content = CascadePageContent.assure_relation(page_content)
            element_id = element_ids.pop(str(oldinstance.pk))
        except (AttributeError, KeyError, ObjectDoesNotExist):
            pass
        else:
            cascade_page_content.glossary.setdefault('element_ids', {})
            cascade_page_content.glossary['element_ids'][str(self.pk)] = element_id
            cascade_page_content.save()
        super().copy_relations(oldinstance)

    def delete(self, *args, **kwargs):
        try:
            page_content = self.placeholder.content_type.get_object_for_this_type(pk=self.placeholder.object_id)
            page_content.cascadepagecontent.glossary['element_ids'].pop(str(self.pk))
        except (AttributeError, KeyError, ObjectDoesNotExist):
            pass
        else:
            page_content.cascadepagecontent.save(update_fields=['glossary'])
        super().delete(*args, **kwargs)


class SectionMixin:
    def get_form(self, request, obj=None, **kwargs):
        form = kwargs.get('form', self.form)
        assert issubclass(form, EntangledModelFormMixin), "Form must inherit from EntangledModelFormMixin"
        kwargs['form'] = type(form.__name__, (SectionFormMixin, form), {})
        return super().get_form(request, obj, **kwargs)

    @classmethod
    def get_identifier(cls, instance):
        try:
            element_id = instance.glossary['element_id'][instance.language]
        except (KeyError, TypeError):
            pass
        else:
            if element_id:
                return format_html('<code>id="{0}"</code>', element_id)
        return super().get_identifier(instance)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        element_id = obj.glossary['element_id']
        if not change:
            # when adding a new element, `element_id` can not be validated for uniqueness in
            # SectionFormMixin.clean_element_id(), so we have to do it here
            postfix = 0
            # check if form simplewrapper has function check_unique_element_id
            if not 'check_unique_element_id' in dir(form):
                form_ = SectionFormMixin
            else:
                form_ = form
            while True:
                try:
                    form_.check_unique_element_id(obj, element_id)
                except ValidationError:
                    # but since we can't raise a ValidationError while saving, we must invent a unique element_id
                    postfix += 1
                    element_id = '{element_id}_{0}'.format(postfix, **obj.glossary)
                else:
                    break
            if postfix:
                obj.glossary['element_id'] = element_id
                obj.save()

        page_content = obj.placeholder.content_type.get_object_for_this_type(pk=obj.placeholder.object_id)
        cascade_page_content = CascadePageContent.assure_relation(page_content)
        cascade_page_content.glossary.setdefault('element_ids', {})
        cascade_page_content.glossary['element_ids'][str(obj.pk)] = element_id
        cascade_page_content.save()
