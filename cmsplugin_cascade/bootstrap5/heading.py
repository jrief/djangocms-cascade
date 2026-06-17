from django.forms.fields import CharField, ChoiceField
from django.forms.widgets import TextInput
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap5.bookmark import BookmarkModelMixin, BookmarkPluginMixin
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.models import CascadeElement

from formset.forms import ModelForm


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
    parent_classes = ['BootstrapColumnPlugin']
    form = HeadingForm
    model_mixins = (BookmarkModelMixin,)
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
