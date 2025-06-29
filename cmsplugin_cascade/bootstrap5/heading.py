from django.core.exceptions import ValidationError
from django.forms.models import ModelFormMetaclass
from django.forms.fields import CharField, ChoiceField, RegexField
from django.forms.widgets import TextInput
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.models import CascadeElement, CascadePageContent, PageContentAnchor

from formset.forms import ModelForm


def identifier_validator(value):
    if not value:
        return
    valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    for c in value:
        if c not in valid_chars:
            msg = _("The element ID '{}' contains invalid characters.")
            raise ValidationError(msg.format(value))


class BookmarkFormMixin(metaclass=ModelFormMetaclass):
    element_id = RegexField(
        r'^[0-9A-Za-z_.~-]+$',
        label=_("Id"),
        max_length=30,
        required=False,
        help_text=_(
            "A unique identifier for this element (please don't use any special characters, punctuations, etc.)"
            "May be used as anchor-link: #id."
        ),
        validators=[identifier_validator],
    )

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
            anchors = page_content.cascadepagecontent.anchors.all()
        except CascadePageContent.DoesNotExist:
            return
        else:
            for anchor in anchors:
                if anchor.cms_plugin.pk != instance.pk and anchor.identifier == element_id:
                    msg = _("The element ID '{}' is not unique for this page.")
                    raise ValidationError(msg.format(element_id))

    def save(self):
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


class HeadingForm(ModelForm):
    TAG_TYPES = [('h{}'.format(k), _("Heading {}").format(k)) for k in range(1, 7)]

    tag_type = ChoiceField(
        choices=TAG_TYPES,
        label=_("Structure Level"),
    )
    content = CharField(
        label=_("Content"),
        widget=TextInput(
            attrs={'style': 'width: 100%; box-sizing: border-box; font-weight: bold; font-size: 125%;'},  # TODO: move to media
        ),
    )

    class Meta:
        model = CascadeElement
        exclude = ['shared_glossary']
        fields_map = {
            'glossary': ['tag_type', 'content'],
        }


class HeadingPlugin(BookmarkPluginMixin, BootstrapPluginBase):  # TODO: inherit in CascadePluginBaseMetaclass.__new__()
    name = _("Heading")
    parent_classes = None
    allow_children = False
    form = HeadingForm
    render_template = 'cascade/generic/heading.html'

    @classmethod
    def get_identifier(cls, instance):
        tag_type = instance.glossary.get('tag_type')
        content = mark_safe(instance.glossary.get('content', ''))
        if tag_type:
            return format_html('<code>{0}</code>: {1}', tag_type, content)
        return content

    @classmethod
    def translate(cls, translator, instance, target_language, **extra_kwargs):
        if content := instance.glossary.get('content'):
            result = translator.translate_text(
                content,
                target_lang=target_language,
                **extra_kwargs,
            )
            instance.glossary['content'] = result.text
            instance.save(update_fields=['glossary'])

    def render(self, context, instance, placeholder):
        context = self.super(HeadingPlugin, self).render(context, instance, placeholder)
        context.update({'content': mark_safe(instance.glossary.get('content', ''))})
        return context

plugin_pool.register_plugin(HeadingPlugin)
