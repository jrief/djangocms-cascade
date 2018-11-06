# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.forms import widgets, models
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade import app_settings
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.models import CascadePage


class SectionForm(models.ModelForm):
    def clean_glossary(self):
        glossary = self.cleaned_data['glossary']
        self.check_unique_element_id(self.instance, glossary['element_id'])
        return glossary

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
        super(SectionModelMixin, self).delete(*args, **kwargs)


class SectionMixin(object):
    def get_form(self, request, obj=None, **kwargs):
        glossary_fields = list(kwargs.pop('glossary_fields', self.glossary_fields))
        glossary_fields.append(GlossaryField(
            widgets.TextInput(),
            label=_("Element ID"),
            name='element_id',
            help_text=_("A unique identifier for this element.")
        ))
        kwargs.update(form=SectionForm, glossary_fields=glossary_fields)
        return super(SectionMixin, self).get_form(request, obj, **kwargs)

    @classmethod
    def get_identifier(cls, instance):
        identifier = super(SectionMixin, cls).get_identifier(instance)
        element_id = instance.glossary.get('element_id')
        if element_id:
            return format_html('<code>id="{0}"</code> {1}', element_id, identifier)
        return identifier

    def save_model(self, request, obj, form, change):
        super(SectionMixin, self).save_model(request, obj, form, change)
        element_id = obj.glossary['element_id']
        if not change:
            # when adding a new element, `element_id` can not be validated for uniqueness
            postfix = 0
            while True:
                try:
                    form.check_unique_element_id(obj, element_id)
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
