from django.forms import ChoiceField
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from cms.plugin_pool import plugin_pool
from entangled.forms import EntangledModelFormMixin

from cmsplugin_cascade.plugin_base import CascadePluginBase, TransparentContainer


class SimpleWrapperFormMixin(EntangledModelFormMixin):
    TAG_CHOICES = [(cls, _("<{}> – Element").format(cls)) for cls in ['div', 'span', 'section', 'article']] + \
                  [('naked', _("Naked Wrapper"))]

    tag_type = ChoiceField(
        choices=TAG_CHOICES,
        label=_("HTML element tag"),
        help_text=_('Choose a tag type for this HTML element.')
    )

    class Meta:
        entangled_fields = {'glossary': ['tag_type']}


class SimpleWrapperPlugin(TransparentContainer, CascadePluginBase):
    name = _("Simple Wrapper")
    parent_classes = None
    require_parent = False
    form = SimpleWrapperFormMixin
    allow_children = True
    alien_child_classes = True

    @classmethod
    def get_identifier(cls, instance):
        identifier = super().get_identifier(instance)
        tag_name = dict(SimpleWrapperFormMixin.TAG_CHOICES).get(instance.glossary.get('tag_type'))
        if tag_name:
            return format_html('{0} {1}', tag_name, identifier)
        return identifier

    def get_render_template(self, context, instance, placeholder):
        if instance.glossary.get('tag_type') == 'naked':
            return 'cascade/generic/naked.html'
        return 'cascade/generic/wrapper.html'

plugin_pool.register_plugin(SimpleWrapperPlugin)
