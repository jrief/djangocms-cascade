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
    class_name = models.CharField(_("class name"), choices=CLASS_NAMES, default=CLASS_NAMES[0][0], max_length=50)

    def __unicode__(self):
        return u"%s" % self.get_class_name_display()

