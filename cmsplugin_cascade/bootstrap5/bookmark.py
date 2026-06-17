from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms.models import ModelFormMetaclass
from django.forms.fields import RegexField
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from cmsplugin_cascade import app_settings
from cmsplugin_cascade.models import PageAnchor


class BookmarkFormMixin(metaclass=ModelFormMetaclass):
    element_id = RegexField(
        r'^[0-9A-Za-z_~.\-]+$',
        label=_("Id"),
        min_length=3,
        max_length=30,
        required=False,
        help_text=_(
            "A unique identifier for this element (please don't use any special characters, punctuations, etc.)"
            "May be used as anchor-link: #id."
        ),
    )

    def clean_element_id(self):
        element_id = self.cleaned_data['element_id']
        self.check_unique_element_id(self.instance, element_id)
        return element_id

    @classmethod
    def check_unique_element_id(cls, instance, identifier):
        """
        Check for the uniqueness of the given identifier for the current page.
        """
        if not identifier:
            return
        page_content = instance.placeholder.content_type.get_object_for_this_type(pk=instance.placeholder.object_id)
        for placeholder in page_content.placeholders.all():
            for other in placeholder.get_plugins():
                other, plugin = other.get_plugin_instance()
                if isinstance(plugin, BookmarkPluginMixin):
                    if other.pk != instance.pk and other.glossary.get('element_id') == identifier:
                        msg = _("The element ID '{}' is not unique for this page.")
                        raise ValidationError(msg.format(identifier))

    def XXXsave(self):  # performed in BookmarkPluginMixin.save_model(…)
        super().save()
        placeholder = self.instance.placeholder
        page_content = placeholder.content_type.get_object_for_this_type(pk=placeholder.object_id)
        cascade_page_content = CascadePageContent.assure_relation(page_content)
        if element_id := self.instance.glossary.get('element_id'):
            PageContentAnchor.objects.update_or_create(
                content=cascade_page_content,
                cms_plugin=self.instance,
                defaults={'identifier': element_id},
            )
        return self.instance


class BookmarkPluginMixin:
    def get_model_form(self, form_class=None):
        if form_class is None:
            form_class = self.form
        Meta = type('Meta', (form_class.Meta,), {})
        Meta.fields_map['glossary'].append('element_id')
        form_class = type(form_class.__name__, (BookmarkFormMixin, form_class), {'Meta': Meta})
        form_class = super().get_model_form(form_class)
        return form_class

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
        page_content = obj.placeholder.content_type.get_object_for_this_type(pk=obj.placeholder.object_id)
        element_ids = []
        for placeholder in page_content.placeholders.all():
            for other in placeholder.get_plugins():
                other, plugin = other.get_plugin_instance()
                if isinstance(plugin, BookmarkPluginMixin):
                    if element_id := other.glossary.get('element_id'):
                        element_ids.append(element_id)
        page_url = page_content.page.get_url_obj(page_content.language)
        page_url.anchors.exclude(identifier__in=element_ids).delete()

        if element_id := obj.glossary['element_id']:
            PageAnchor.objects.update_or_create(
                page_url=page_url,
                identifier=element_id,
            )

        # if not change:
        #     # when adding a new element, `element_id` can not be validated for uniqueness in
        #     # BookmarkFormMixin.clean_element_id(), so we have to do it here
        #     postfix = 0
        #     while True:
        #         try:
        #             form.check_unique_element_id(obj, element_id)
        #         except ValidationError:
        #             # but since we can't raise a ValidationError while saving, we must invent a unique element_id
        #             postfix += 1
        #             element_id = '{element_id}_{0}'.format(postfix, **obj.glossary)
        #         else:
        #             break
        #     if postfix:
        #         obj.glossary['element_id'] = element_id
        #         obj.save()


        # cascade_page_content = CascadePageContent.assure_relation(page_content)
        # cascade_page_content.glossary.setdefault('element_ids', {})
        # cascade_page_content.glossary['element_ids'][str(obj.pk)] = element_id
        # cascade_page_content.save()


class BookmarkModelMixin:
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
            for element_id in element_ids.values():
                PageAnchor.objects.update_or_create(
                    content=cascade_page_content,
                    cms_plugin=self,
                    defaults={'identifier': element_id},
                )

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
