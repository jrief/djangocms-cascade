# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from cms.api import add_plugin
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.bootstrap3.buttons import BootstrapButtonPlugin
from .test_base import CascadeTestCase


class ButtonWrapperPluginTest(CascadeTestCase):
    def test_plugin_context(self):
        glossary = {'link_content': 'Knopf', 'button_type': 'btn-default'}
        model_instance = add_plugin(self.placeholder, BootstrapButtonPlugin, 'en', glossary=glossary)
        button_plugin = model_instance.get_plugin_class_instance()
        self.assertIsInstance(button_plugin, BootstrapButtonPlugin)
        context = button_plugin.render({}, model_instance, None)
        self.assertIn('instance', context)
        self.assertIsInstance(context['instance'], LinkElementMixin)
        self.assertListEqual(button_plugin.get_css_classes(model_instance), ['btn', 'btn-default'])
        self.assertEqual(button_plugin.get_identifier(model_instance), 'Knopf')

    def test_external_link(self):
        glossary = {'link_content': 'Django', 'button_type': 'btn-primary',
                    'link': {'url': 'https://www.djangoproject.com/', 'type': 'exturl'}}
        model_instance = add_plugin(self.placeholder, BootstrapButtonPlugin, 'en', glossary=glossary)
        html = self.get_html(model_instance, self.get_request_context())
        self.assertHTMLEqual(html, '<a href="https://www.djangoproject.com/" class="btn btn-primary">Django</a>')

    def test_internal_link(self):
        glossary = {'link_content': 'HOME', 'button_type': 'btn-success',
            'link': {'pk': self.home_page.id, 'model': 'cms.Page', 'type': 'cmspage'}, 'target': ''}
        model_instance = add_plugin(self.placeholder, BootstrapButtonPlugin, 'en', glossary=glossary)
        html = self.get_html(model_instance, self.get_request_context())
        self.assertHTMLEqual(html, '<a href="/en/"  class="btn btn-success">HOME</a>')
