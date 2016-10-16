# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.forms import widgets, models
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.settings import CMSPLUGIN_CASCADE
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.models import CascadePage


class SectionForm(models.ModelForm):
    def clean_glossary(self):
        glossary = self.cleaned_data['glossary']
        if self.check_unique_element_id(self.instance, glossary['element_id']) is False:
            msg = _("The element ID `{element_id}` is not unique for this page.")
            raise ValidationError(msg.format(**glossary))
        return glossary

    @classmethod
    def check_unique_element_id(cls, instance, element_id):
        """
        Check for uniqueness of the given element_id for the current page.
        Return None if instance is not yet associated with a page.
        """
        try:
            element_ids = instance.page.cascadepage.glossary.get('element_ids', {})
        except (AttributeError, ObjectDoesNotExist):
            pass
        else:
            if element_id:
                element_ids[str(instance.pk)] = element_id
                return len(element_ids) == len(set(element_ids.values()))


class SectionModelMixin(object):
    def element_id(self):
        id_attr = self.glossary.get('element_id')
        if id_attr:
            return '{bookmark_prefix}{0}'.format(id_attr, **CMSPLUGIN_CASCADE)


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
        CascadePage.assure_relation(obj.page)
        element_id = obj.glossary['element_id']
        if not change:
            # when adding a new element, `element_id` can not be validated for uniqueness
            postfix = 0
            while form.check_unique_element_id(obj, element_id) is False:
                postfix += 1
                element_id = '{element_id}_{0}'.format(postfix, **obj.glossary)
            if postfix:
                obj.glossary['element_id'] = element_id
                obj.save()

        obj.page.cascadepage.glossary.setdefault('element_ids', {})
        obj.page.cascadepage.glossary['element_ids'][str(obj.pk)] = element_id
        obj.page.cascadepage.save()
