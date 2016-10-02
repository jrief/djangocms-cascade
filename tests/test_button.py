# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from cms.api import add_plugin, create_page
from cms.models.placeholdermodel import Placeholder
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.bootstrap3.buttons import BootstrapButtonPlugin


class ButtonWrapperPluginTest(TestCase):
    def setUp(self):
        self.placeholder = Placeholder.objects.create(slot='test')

    def test_plugin_context(self):
        glossary = {'link_content': 'Knopf', 'button_type': 'btn-default'}
        model_instance = add_plugin(self.placeholder, BootstrapButtonPlugin, 'en', glossary=glossary)
        button_plugin = model_instance.get_plugin_class_instance()
        context = button_plugin.render({}, model_instance, None)
        self.assertIn('instance', context)
        self.assertIsInstance(context['instance'], LinkElementMixin)
        self.assertListEqual(button_plugin.get_css_classes(model_instance), ['btn', 'btn-default'])
        self.assertEqual(button_plugin.get_identifier(model_instance), 'Knopf')

    def test_external_link(self):
        glossary = {'link_content': 'Django', 'button_type': 'btn-primary',
                    'link': {'url': 'https://www.djangoproject.com/', 'type': 'exturl'}}
        model_instance = add_plugin(self.placeholder, BootstrapButtonPlugin, 'en', glossary=glossary)
        html = model_instance.render_plugin({})
        self.assertHTMLEqual(html, '<a href="https://www.djangoproject.com/" class="btn btn-primary">Django</a>')

    def test_internal_link(self):
        page = create_page('HOME', 'cascade/testing.html', 'en')
        glossary = {'link_content': 'HOME', 'button_type': 'btn-success',
            'link': {'pk': page.id, 'model': 'cms.Page', 'type': 'cmspage'}, 'target': ''}
        model_instance = add_plugin(self.placeholder, BootstrapButtonPlugin, 'en', glossary=glossary)
        html = model_instance.render_plugin({})
        self.assertHTMLEqual(html, '<a href="/en/"  class="btn btn-success">HOME</a>')
