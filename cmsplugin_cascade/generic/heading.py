from django.forms import widgets, CharField, ChoiceField
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from cms.plugin_pool import plugin_pool
from entangled.forms import EntangledModelFormMixin

from cmsplugin_cascade.plugin_base import CascadePluginBase


class HeadingFormMixin(EntangledModelFormMixin):
    TAG_TYPES = [('h{}'.format(k), _("Heading {}").format(k)) for k in range(1, 7)]

    tag_type = ChoiceField(
        choices=TAG_TYPES,
        label=_("Structure Level"),
    )

    content = CharField(
        label=_("Content"),
        widget=widgets.TextInput(attrs={'style': 'width: calc(100% - 12em); padding-right: 0; font-weight: bold; font-size: 125%;'}),
    )

    class Meta:
        entangled_fields = {'glossary': ['tag_type', 'content']}


class HeadingPlugin(CascadePluginBase):
    name = _("Heading")
    parent_classes = None
    allow_children = False
    form = HeadingFormMixin
    render_template = 'cascade/generic/heading.html'

    @classmethod
    def get_identifier(cls, instance):
        tag_type = instance.glossary.get('tag_type')
        content = mark_safe(instance.glossary.get('content', ''))
        if tag_type:
            return format_html('<code>{0}</code>: {1}', tag_type, content)
        return content

    @classmethod
    def translate(cls, translator, instance, target_language, source_language=None):
        if content := instance.glossary.get('content'):
            result = translator.translate_text(
                content,
                source_lang=source_language,
                target_lang=target_language,
            )
            instance.glossary['content'] = result.text
            instance.save(update_fields=['glossary'])

    def render(self, context, instance, placeholder):
        context = self.super(HeadingPlugin, self).render(context, instance, placeholder)
        context.update({'content': mark_safe(instance.glossary.get('content', ''))})
        return context

plugin_pool.register_plugin(HeadingPlugin)
