# -*- coding: utf-8 -*-
import json
from django.test import TestCase
from django.test.client import RequestFactory
from django.forms import widgets
from django.contrib.auth.models import User
from django.test.client import Client
from cms.models.placeholdermodel import Placeholder
from cmsplugin_cascade.widgets import MultipleCascadingSizeWidget
from cmsplugin_cascade.models import CascadeElement
from cmsplugin_cascade.bootstrap3.buttons import BootstrapButtonPlugin


class ButtonWrapperPluginTest(TestCase):
    admin_password = 'secret'
    client = Client()

    def setUp(self):
        self.createAdminUser()
        self.factory = RequestFactory()
        self.placeholder = Placeholder.objects.create()
        self.request = self.factory.get('/admin/dummy-change-form/')

    def createAdminUser(self):
        self.user = User.objects.create_user('admin', 'admin@example.com', self.admin_password)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        logged_in = self.client.login(username=self.user.username, password=self.admin_password)
        self.assertTrue(logged_in, 'User is not logged in')

    def test_change_form(self):
        glossary = {'button-type': 'btn-primary', 'button-options': ['btn-block'], 'button-size': 'btn-lg',}
        obj_id = CascadeElement.objects.create(glossary=glossary).id
        model = BootstrapButtonPlugin().get_object(self.request, obj_id)
        self.assertEqual(model.context.get('-num-children-'), 0)
        self.assertListEqual(BootstrapButtonPlugin.get_css_classes(model), ['btn', 'btn-primary', 'btn-lg', 'btn-block'])
        self.assertEqual(BootstrapButtonPlugin.get_identifier(model), 'Primary')
        button_wrapper = BootstrapButtonPlugin(model=model)
        self.assertEqual(len(button_wrapper.glossary_fields), 4)
        self.assertIsInstance(button_wrapper.glossary_fields[0].widget, widgets.RadioSelect)
        self.assertIsInstance(button_wrapper.glossary_fields[1].widget, widgets.RadioSelect)
        self.assertIsInstance(button_wrapper.glossary_fields[2].widget, widgets.CheckboxSelectMultiple)
        self.assertIsInstance(button_wrapper.glossary_fields[3].widget, MultipleCascadingSizeWidget)
        self.assertListEqual(button_wrapper.child_classes, ['LinkPlugin'])
        form = button_wrapper.get_form(self.request)
        html = form(instance=model).as_table()
        self.assertInHTML('<input checked="checked" id="id_context_1" name="button-type" type="radio" value="btn-primary" />', html)
        self.assertInHTML('<input id="id_context_1" name="button-size" type="radio" value="" />', html)
        self.assertInHTML('<input checked="checked" id="id_context_0" name="button-options" type="checkbox" value="btn-block" />', html)
        button_wrapper.save_model(self.request, model, form, True)

    def test_save_button(self):
        add_url = '/admin/cms/page/add-plugin/'
        post_data = {'plugin_parent': [''], 'csrfmiddlewaretoken': ['PQ7M8GfaJs4SdlsFRLz7XrNwC23mtD0D'], 'plugin_type': ['ButtonWrapperPlugin'], 'plugin_language': ['en'], 'placeholder_id': [str(self.placeholder.id)]}
        response = self.client.post(add_url, post_data)
        self.assertContains(response, '/admin/cms/page/edit-plugin/')
        change_url = json.loads(response.content.decode('utf-8'))['url']
        obj_id = change_url.split('/')[-2]
        post_data = {'csrfmiddlewaretoken': ['PQ7M8GfaJs4SdlsFRLz7XrNwC23mtD0D'], 'inline_styles-margin-left': [''], 'button-type': ['btn-default'], '_continue': [True], '_popup': ['1'], 'button-size': ['btn-lg'], 'inline_styles-margin-bottom': [''], 'inline_styles-margin-right': [''], 'inline_styles-margin-top': ['50px'], 'button-options': ['btn-block'], '_save': ['Save']}
        response = self.client.post(change_url, post_data)
        self.assertInHTML('<title>Change a page</title>', response.content.decode('utf-8'))
        model = CascadeElement.objects.get(id=obj_id)
        self.assertDictContainsSubset({'button-type': 'btn-default', 'button-size': 'btn-lg'}, model.context)
        self.assertListEqual(model.context.get('button-options'), ['btn-block'])
        self.assertDictContainsSubset({'margin-top': '50px'}, model.context.get('inline_styles'))
        self.assertListEqual(model.css_classes.split(), ['btn', 'btn-default', 'btn-lg', 'btn-block'])
        self.assertEqual(model.inline_styles, 'margin-top: 50px;')
