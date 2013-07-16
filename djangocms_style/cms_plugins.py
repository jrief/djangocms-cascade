from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from django.utils.translation import ugettext_lazy as _
from cms.models import CMSPlugin
from djangocms_style.models import Style

class StylePlugin(CMSPluginBase):
    model = Style
    name = _("Style")
    render_template = "cms/plugins/style.html"
    allow_children = True

    fieldsets = (
        (None, {
            'fields': ('class_name',)
        }),
        (_('Advanced Settings'), {
            'classes': ('collapse',),
            'fields': (
                'tag_type',
                'additional_classes',
                ('padding_left', 'padding_right', 'padding_top', 'padding_bottom'),
                ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'),
            ),
        }),
    )

plugin_pool.register_plugin(StylePlugin)
