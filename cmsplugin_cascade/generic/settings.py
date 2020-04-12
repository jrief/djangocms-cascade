CASCADE_PLUGINS = ['custom_snippet', 'heading', 'horizontal_rule', 'simple_wrapper', 'text_image']

def set_defaults(config):
    from cmsplugin_cascade.extra_fields.config import PluginExtraFieldsConfig

    config.setdefault('plugins_with_extra_fields', {})
    plugins_with_extra_fields = config['plugins_with_extra_fields']
    plugins_with_extra_fields.setdefault('HorizontalRulePlugin', PluginExtraFieldsConfig(
        inline_styles={
            'extra_fields:Border': ['border-top'],
            'extra_fields:Border Radius': ['border-radius'],
            'extra_units:Border Radius': 'px,rem',
        },
        allow_override=False,
    ))
