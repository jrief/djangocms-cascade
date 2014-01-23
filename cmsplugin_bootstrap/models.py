from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from jsonfield.fields import JSONField
from cms.models import CMSPlugin
from cms.plugin_pool import plugin_pool


class BootstrapElement(CMSPlugin):
    """
    The container to hold additional bootstrap elements.
    """
    cmsplugin_ptr = models.OneToOneField(CMSPlugin, related_name='+', parent_link=True)
    context = JSONField(null=True, blank=True)

    def __unicode__(self):
        cls = plugin_pool.get_plugin(self.plugin_type)
        return cls.get_identifier(self)

    @property
    def css_classes(self):
        return self.context or {}

        # remove me
        css_classes = self.class_name and [self.class_name] or []
        if isinstance(self.extra_classes, dict):
            css_classes.extend([ec for ec in self.extra_classes.values() if ec])
        if isinstance(self.tagged_classes, list):
            css_classes.extend([tc for tc in self.tagged_classes if tc])
        return u' '.join(css_classes)

    @property
    def inline_styles(self):
        try:
            inline_styles = self.context.get('inline_styles')
            return u' '.join(['{0}: {1};'.format(*s) for s in inline_styles.items() if s[1]])
        except (IndexError, AttributeError):
            pass
        return ''

    @property
    def data_options(self):
        try:
            return u' '.join(['data-{0}={1}'.format(*s) for s in self.options.items() if s[1]])
        except (IndexError, AttributeError):
            pass
        return ''

    def get_full_context(self):
        """
        Return the full data context, up to the root.
        """
        context = {}
        try:
            parent = BootstrapElement.objects.get(id=self.parent_id)
            context = parent.get_full_context()
            context.update(self.context or {})
        except ObjectDoesNotExist:
            pass
        return context

#     @property
#     def context(self):
#         try:
#             return u' '.join(['{0}: {1};'.format(*s) for s in self.get_context().items() if s[1]])
#         except (IndexError, AttributeError):
#             pass
#         return ''
