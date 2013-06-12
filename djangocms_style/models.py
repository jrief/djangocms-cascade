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
    cmsplugin_ptr = models.OneToOneField(CMSPlugin, related_name='+', parent_link=True)
    class_name = models.CharField(_("class name"), choices=CLASS_NAMES, default=CLASS_NAMES[0][0], max_length=50, blank=True, null=True)

    padding_left = models.SmallIntegerField(_("left"), blank=True, null=True)
    padding_right = models.SmallIntegerField(_("right"), blank=True, null=True)
    padding_top = models.SmallIntegerField(_("top"), blank=True, null=True)
    padding_bottom = models.SmallIntegerField(_("bottom"), blank=True, null=True)

    margin_left = models.SmallIntegerField(_("left"), blank=True, null=True)
    margin_right = models.SmallIntegerField(_("right"), blank=True, null=True)
    margin_top = models.SmallIntegerField(_("top"), blank=True, null=True)
    margin_bottom = models.SmallIntegerField(_("bottom"), blank=True, null=True)

    def __unicode__(self):
        return u"%s" % self.get_class_name_display()

    def inline_style(self):
        style = ""
        if self.padding_left:
            style += "padding-left: %dpx; " % self.padding_left
        if self.padding_right:
            style += "padding-right: %dpx; " % self.padding_right
        if self.padding_bottom:
            style += "padding-bottom: %dpx; " % self.padding_right
        if self.padding_top:
            style += "padding-top: %dpx; " % self.padding_top
        if self.margin_left:
            style += "margin-left: %dpx; " % self.margin_left
        if self.margin_right:
            style += "margin-right: %dpx; " % self.margin_right
        if self.margin_top:
            style += "margin-top: %dpx; " % self.margin_top
        if self.margin_bottom:
            style += "margin-bottom: %dpx; " % self.margin_bottom
        return style

