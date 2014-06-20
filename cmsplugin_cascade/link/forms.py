# -*- coding: utf-8 -*-
from django.forms import fields
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import LinkElement


class LinkForm(ModelForm):
    TYPE_CHOICES = (('int', _("Internal")), ('ext', _("External")), ('email', _("Mail To")),)
    link_type = fields.ChoiceField(choices=TYPE_CHOICES, initial='int')
    url = fields.URLField(required=False)
    email = fields.EmailField(required=False)

    class Meta:
        model = LinkElement
        fields = ('page_link', 'text_link', 'context',)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        mailto = 'mailto: '
        urlvalidator = URLValidator()
        initial = {}
        try:
            if instance.text_link.startswith(mailto):
                initial['link_type'] = 'email'
                initial['email'] = instance.text_link[len(mailto):]
            else:
                try:
                    urlvalidator(instance.text_link)
                    initial['link_type'] = 'ext'
                    initial['url'] = instance.text_link
                except ValidationError:
                    initial['link_type'] = 'int'
        except AttributeError:
            pass
        kwargs.update(initial=initial)
        super(LinkForm, self).__init__(*args, **kwargs)

    def full_clean(self):
        """
        Sanitize form fields, so that only one of page_link, url or email contains data.
        """
        link_type = self.data.get('link_type')
        if link_type == 'int':
            self.data.update({'url': '', 'email': ''})
        elif link_type == 'ext':
            self.data.update({'page_link': None, 'email': ''})
        elif link_type == 'email':
            self.data.update({'page_link': None, 'url': ''})
        super(LinkForm, self).full_clean()
