from cms.models import CMSPlugin
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

CLASS_NAMES = getattr(settings, "CMS_STYLE_NAMES", (
        ('info', _("info")),
        ('new', _("new")),
        ('hint', _("hint"))
    )
)

class Style(CMSPlugin):
    """
    A CSS Style Plugin
    """
    class_name = models.CharField(_("class name"), choices=CLASS_NAMES, default=CLASS_NAMES[0][0], max_length=50, blank=True, null=True)

    padding_left = models.SmallIntegerField(_("padding left"), blank=True, null=True)
    padding_right = models.SmallIntegerField(_("padding right"), blank=True, null=True)
    padding_top = models.SmallIntegerField(_("padding top"), blank=True, null=True)
    padding_bottom = models.SmallIntegerField(_("padding bottom"), blank=True, null=True)

    margin_left = models.SmallIntegerField(_("margin left"), blank=True, null=True)
    margin_right = models.SmallIntegerField(_("margin right"), blank=True, null=True)
    margin_top = models.SmallIntegerField(_("margin top"), blank=True, null=True)
    margin_bottom = models.SmallIntegerField(_("margin bottom"), blank=True, null=True)

    def __unicode__(self):
        return u"%s" % self.get_class_name_display()

