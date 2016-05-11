# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import QueryDict
from cms.api import add_plugin
from cms.utils.plugins import build_plugin_tree
from cmsplugin_cascade.models import CascadeElement
from cmsplugin_cascade.bootstrap3.container import (BootstrapContainerPlugin, BootstrapRowPlugin,
         BootstrapRowForm, BootstrapColumnPlugin, BS3_BREAKPOINT_KEYS)
from cmsplugin_cascade.generic.cms_plugins import HeadingPlugin
from .test_base import CascadeTestCase
from .utils import get_request_context


class SectionPluginTest(CascadeTestCase):
    def setUp(self):
        super(SectionPluginTest, self).setUp()

        # add a Bootstrap Container Plugin
        container_model = add_plugin(self.placeholder, BootstrapContainerPlugin, 'en',
                                     glossary={'breakpoints': BS3_BREAKPOINT_KEYS})
        self.assertIsInstance(container_model, CascadeElement)
        container_plugin = container_model.get_plugin_class_instance(self.admin_site)
        self.assertIsInstance(container_plugin, BootstrapContainerPlugin)
        ModelForm = container_plugin.get_form(self.request, container_model)
        post_data = QueryDict('', mutable=True)
        post_data.setlist('breakpoints', ['sm', 'md'])
        form = ModelForm(post_data, None, instance=container_model)
        html = form.as_p()
        self.assertInHTML(
            '<input id="id_glossary_breakpoints_0" name="breakpoints" type="checkbox" value="xs" />',
            html)
        self.assertInHTML(
            '<input checked="checked" id="id_glossary_breakpoints_2" name="breakpoints" type="checkbox" value="md" />',
            html)
        self.assertInHTML('<input id="id_glossary_fluid" name="fluid" type="checkbox" />', html)
        container_plugin.save_model(self.request, container_model, form, False)
        self.assertListEqual(container_model.glossary['breakpoints'], ['sm', 'md'])
        self.assertTrue('fluid' in container_model.glossary)
        self.assertEqual(str(container_model), 'for tablets, laptops')

        # add a RowPlugin with 1 ColumnPlugin
        row_model = add_plugin(self.placeholder, BootstrapRowPlugin, 'en', target=container_model)
        row_plugin = row_model.get_plugin_class_instance()
        row_change_form = BootstrapRowForm({'num_children': 1})
        row_change_form.full_clean()
        row_plugin.save_model(self.request, row_model, row_change_form, False)
        self.assertDictEqual(row_model.glossary, {})
        self.assertIsInstance(row_model, CascadeElement)
        column_models = CascadeElement.objects.filter(parent_id=row_model.id)
        self.assertEqual(column_models.count(), 1)

        # work with the ColumnPlugin
        self.column_model = column_models.first()
        self.assertIsInstance(self.column_model, CascadeElement)
        self.column_plugin = self.column_model.get_plugin_class_instance()
        self.assertIsInstance(self.column_plugin, BootstrapColumnPlugin)
        self.assertEqual(self.column_model.parent.id, row_model.id)

        self.plugin_list = [container_model, row_model, self.column_model]

    def test_section(self):
        heading_model = add_plugin(self.placeholder, HeadingPlugin, 'en', target=self.column_model)
        self.assertIsInstance(heading_model, CascadeElement)
        heading_plugin = heading_model.get_plugin_class_instance(self.admin_site)
        self.assertIsInstance(heading_plugin, HeadingPlugin)
        ModelForm = heading_plugin.get_form(self.request, heading_model)
        post_data = QueryDict('', mutable=True)
        post_data.update(tag_type='h2', content="Hello", element_id='foo')
        form = ModelForm(post_data, None, instance=heading_model)
        html = form.as_p()
        needle = '<input id="id_glossary_element_id" name="element_id" type="text" value="foo" />'
        self.assertInHTML(needle, html)
        self.assertTrue(form.is_valid())
        heading_plugin.save_model(self.request, heading_model, form, False)

        # check identifier
        html = heading_plugin.get_identifier(heading_model)
        expected = '<code>h2</code>: Hello <code>id="foo"</code>'
        self.assertHTMLEqual(html, expected)

        # render the Container Plugin with the Heading Plgin as a child
        self.plugin_list.append(heading_model)
        build_plugin_tree(self.plugin_list)
        context = get_request_context(self.request)
        html = heading_model.render_plugin(context)
        expected = '<h2 id="foo">Hello</h2>'
        self.assertHTMLEqual(html, expected)

        # add another heading model with the same id
        heading_model = add_plugin(self.placeholder, HeadingPlugin, 'en', target=self.column_model)
        form = ModelForm(post_data, None, instance=heading_model)
        self.assertFalse(form.is_valid())
        expected = '<ul class="errorlist"><li>glossary<ul class="errorlist"><li>The element ID `foo` is not unique for this page.</li></ul></li></ul>'
        print(str(form.errors))
        self.assertHTMLEqual(str(form.errors), expected)
