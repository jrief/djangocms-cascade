from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.text import Truncator
from jsonfield.fields import JSONField
from cms.models import CMSPlugin


class BootstrapElement(CMSPlugin):
    """
    The container to hold additional bootstrap elements.
    """
    cmsplugin_ptr = models.OneToOneField(CMSPlugin, related_name='+', parent_link=True)
    tag_type = models.CharField(verbose_name=_('tag Type'), max_length=50)
    class_name = models.CharField(_("class name"), max_length=50, blank=True, null=True)
    extra_classes = JSONField(null=True, blank=True, help_text='Add extra CSS classes to this HTML element')
    tagged_classes = JSONField(null=True, blank=True, help_text='Tag special CSS classes to this HTML element')
    extra_styles = JSONField(null=True, blank=True, help_text='Add extra styles to this HTML element')
    options = JSONField(null=True, blank=True, help_text='Extra data options for this plugin')

    def __unicode__(self):
        value = self.css_classes
        if value:
            return unicode(Truncator(value).words(3, truncate=' ...'))
        return u''

    @property
    def css_classes(self):
        css_classes = self.class_name and [self.class_name] or []
        if isinstance(self.extra_classes, dict):
            css_classes.extend([ec for ec in self.extra_classes.values() if ec])
        if isinstance(self.tagged_classes, list):
            css_classes.extend([tc for tc in self.tagged_classes if tc])
        return u' '.join(css_classes)

    @property
    def inline_styles(self):
        if isinstance(self.extra_styles, dict):
            try:
                return u' '.join(['{0}: {1};'.format(*s) for s in self.extra_styles.items() if s[1] is not None])
            except IndexError:
                pass
        return ''

    @property
    def data_options(self):
        if isinstance(self.options, dict):
            try:
                return u' '.join(['data-{0}={1}'.format(*s) for s in self.options.items() if s[1] is not None])
            except IndexError:
                pass
        return ''
