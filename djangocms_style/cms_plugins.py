from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from django.utils.translation import ugettext_lazy as _
from djangocms_style.models import Style


class StylePlugin(CMSPluginBase):
    module = 'Bootstrap'
    model = Style
    name = _("Style")
    render_template = "cms/plugins/style.html"
    allow_children = True
    child_classes = ['LinkPlugin']

    fieldsets = (
        (None, {
            'fields': ('tag_type',)
        }),
        (_('Advanced Settings'), {
            'classes': ('collapse',),
            'fields': (
                'class_name',
                'additional_classes',
                ('padding_left', 'padding_right', 'padding_top', 'padding_bottom'),
                ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'),
            ),
        }),
    )

plugin_pool.register_plugin(StylePlugin)
