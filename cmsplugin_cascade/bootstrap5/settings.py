from collections import OrderedDict
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from cmsplugin_cascade.extra_fields.config import PluginExtraFieldsConfig
from cmsplugin_cascade.bootstrap5.mixins import BootstrapUtilities
from .grid import Breakpoint, Bound


CASCADE_PLUGINS = ['accordion', 'buttons', 'card', 'carousel', 'container', 'embeds', 'icon', 'image', 'jumbotron',
                   'picture', 'tabs']
if 'cms_bootstrap' in settings.INSTALLED_APPS:
    CASCADE_PLUGINS.append('secondary_menu')


def set_defaults(config):
    config.setdefault('bootstrap5', {})
    config['bootstrap5'].setdefault('default_bounds', OrderedDict([
        (Breakpoint.xs, Bound(320, 572)),
        (Breakpoint.sm, Bound(540, 540)),
        (Breakpoint.md, Bound(720, 720)),
        (Breakpoint.lg, Bound(960, 960)),
        (Breakpoint.xl, Bound(1140, 1140)),
        (Breakpoint.xxl, Bound(1320, 1320)),
    ]))
    config['bootstrap5'].setdefault('fluid_bounds', OrderedDict([
        (Breakpoint.xs, Bound(320, 576)),
        (Breakpoint.sm, Bound(576, 768)),
        (Breakpoint.md, Bound(768, 992)),
        (Breakpoint.lg, Bound(992, 1200)),
        (Breakpoint.xl, Bound(1200, 1400)),
        (Breakpoint.xxl, Bound(1400, 1980)),
    ]))
    config['bootstrap5'].setdefault('gutter', 24)

    config['plugins_with_extra_mixins'].setdefault('BootstrapAccordionPlugin', BootstrapUtilities(
        BootstrapUtilities.margins,
    ))
    config['plugins_with_extra_mixins'].setdefault('BootstrapAccordionGroupPlugin', BootstrapUtilities(
        BootstrapUtilities.background_and_color,
        BootstrapUtilities.margins,
    ))
    config['plugins_with_extra_mixins'].setdefault('BootstrapCardPlugin', BootstrapUtilities(
        BootstrapUtilities.background_and_color,
        BootstrapUtilities.margins,
    ))
    config['plugins_with_extra_mixins'].setdefault('BootstrapCarouselPlugin', BootstrapUtilities(
        BootstrapUtilities.margins,
    ))
    config['plugins_with_extra_mixins'].setdefault('BootstrapContainerPlugin', BootstrapUtilities(
        BootstrapUtilities.paddings,
    ))
    config['plugins_with_extra_mixins'].setdefault('HeadingPlugin', BootstrapUtilities(
        BootstrapUtilities.margins,
    ))
    config['plugins_with_extra_mixins'].setdefault('HorizontalRulePlugin', BootstrapUtilities(
        BootstrapUtilities.margins,
    ))

    config['plugins_with_extra_fields'].setdefault('BootstrapTabSetPlugin', PluginExtraFieldsConfig(
        css_classes={
            'multiple': True,
            'class_names': ['nav-tabs', 'nav-pills', 'nav-fill', 'nav-justified'],
        },
    ))

    config['plugins_with_extra_render_templates'].setdefault('BootstrapSecondaryMenuPlugin', [
        ('cascade/bootstrap5/secmenu-list-group.html', _("List Group")),
        ('cascade/bootstrap5/secmenu-unstyled-list.html', _("Unstyled List"))
    ])
