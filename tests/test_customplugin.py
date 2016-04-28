from django.test import TestCase

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import CascadePluginBase


class CustomPlugin(CascadePluginBase):
    name = 'Custom Element'
    render_template = 'cascade/generic/naked.html'


class CustomPluginTest(TestCase):

    def test_register(self):
        plugin_pool.register_plugin(CustomPlugin)

    def test_proxy_model_has_correct_app_label(self):
        self.assertEqual(CustomPlugin.model._meta.app_label, 'cascade_dummy')
