from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from jsonfield.fields import JSONField
from cms.models import CMSPlugin
from cms.plugin_pool import plugin_pool


class BootstrapElement(CMSPlugin):
    """
    The container to hold additional bootstrap elements.
    """
    cmsplugin_ptr = models.OneToOneField(CMSPlugin, related_name='+', parent_link=True)
    #tag_type = models.CharField(verbose_name=_('tag Type'), max_length=50)
    #class_name = models.CharField(_('class name'), max_length=50, blank=True, null=True)
    #extra_classes = JSONField(null=True, blank=True, help_text=_('Add extra CSS classes to this HTML element'))
    #tagged_classes = JSONField(null=True, blank=True, help_text=_('Tag special CSS classes to this HTML element'))
    #extra_styles = JSONField(null=True, blank=True, help_text=_('Add extra styles to this HTML element'))
    #options = JSONField(null=True, blank=True, help_text=_('Extra data options for this plugin'))
    extra_context = JSONField(null=True, blank=True)

    def __unicode__(self):
        cls = plugin_pool.get_plugin(self.plugin_type)
        return cls.get_identifier(self)

    @property
    def css_classes(self):
        return self.extra_context or {}

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
            inline_styles = self.extra_context.get('inline_styles')
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

    def get_context(self):
        context = {}
        try:
            context = BootstrapElement.objects.get(id=self.parent_id).get_context()
            context.update(self.extra_context or {})
        except ObjectDoesNotExist:
            pass
        return context

    @property
    def context(self):
        try:
            return u' '.join(['{0}: {1};'.format(*s) for s in self.get_context().items() if s[1]])
        except (IndexError, AttributeError):
            pass
        return ''
