# -*- coding: utf-8 -*-
import json
from django.test import TestCase
from django.test.client import RequestFactory
from django.forms import widgets
from django.contrib.auth.models import User
from django.test.client import Client
from cms.models.placeholdermodel import Placeholder
from cmsplugin_cascade.widgets import MultipleInlineStylesWidget
from cmsplugin_cascade.models import CascadeElement
from cmsplugin_cascade.bootstrap3.buttons import ButtonWrapperPlugin


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
        context = {'button-type': 'btn-primary', 'button-options': ['btn-block'], 'button-size': 'btn-lg',}
        obj_id = CascadeElement.objects.create(context=context).id
        model = ButtonWrapperPlugin().get_object(self.request, obj_id)
        self.assertEqual(model.context.get('-num-children-'), 0)
        self.assertListEqual(ButtonWrapperPlugin.get_css_classes(model), ['btn', 'btn-primary', 'btn-lg', 'btn-block'])
        self.assertEqual(ButtonWrapperPlugin.get_identifier(model), 'Primary')
        button_wrapper = ButtonWrapperPlugin(model=model)
        self.assertEqual(len(button_wrapper.partial_fields), 4)
        self.assertIsInstance(button_wrapper.partial_fields[0].widget, widgets.RadioSelect)
        self.assertIsInstance(button_wrapper.partial_fields[1].widget, widgets.RadioSelect)
        self.assertIsInstance(button_wrapper.partial_fields[2].widget, widgets.CheckboxSelectMultiple)
        self.assertIsInstance(button_wrapper.partial_fields[3].widget, MultipleInlineStylesWidget)
        self.assertListEqual(button_wrapper.child_classes, ['LinkPlugin'])
        form = button_wrapper.get_form(self.request)
        html = form(instance=model).as_table()
        self.assertInHTML('<input checked="checked" id="id_context_1" name="button-type" type="radio" value="btn-primary" />', html)
        self.assertInHTML('<input id="id_context_1" name="button-size" type="radio" value="" />', html)
        self.assertInHTML('<input checked="checked" id="id_context_0" name="button-options" type="checkbox" value="btn-block" />', html)
        button_wrapper.save_model(self.request, model, form, True)

    def test_save_button(self):
        add_url = '/admin/cms/page/add-plugin/'
        post_data = {u'plugin_parent': [u''], u'csrfmiddlewaretoken': [u'PQ7M8GfaJs4SdlsFRLz7XrNwC23mtD0D'], u'plugin_type': [u'ButtonWrapperPlugin'], u'plugin_language': [u'en'], u'placeholder_id': [str(self.placeholder.id)]}
        response = self.client.post(add_url, post_data)
        self.assertContains(response, '/admin/cms/page/edit-plugin/')
        change_url = json.loads(response.content)['url']
        obj_id = change_url.split('/')[-2]
        post_data = { u'csrfmiddlewaretoken': [u'PQ7M8GfaJs4SdlsFRLz7XrNwC23mtD0D'], u'inline_styles-margin-left': [u''], u'button-type': [u'btn-default'], u'_continue': [True], u'_popup': [u'1'], u'button-size': [u'btn-lg'], u'inline_styles-margin-bottom': [u''], u'inline_styles-margin-right': [u''], u'button-options': [u'btn-block'], u'inline_styles-margin-top': [u'50px'], u'_save': [u'Save']}
        response = self.client.post(change_url, post_data)
        self.assertInHTML('<title>Change a page</title>', response.content)
        model = CascadeElement.objects.get(id=obj_id)
        self.assertDictContainsSubset({ 'button-type': 'btn-default', 'button-size': 'btn-lg' }, model.context)
        self.assertListEqual(model.context.get('button-options'), [u'btn-block'])
        self.assertDictContainsSubset({ 'margin-top': '50px' }, model.context.get('inline_styles'))
        self.assertEquals(model.css_classes, u'btn btn-default btn-lg btn-block')
        self.assertEquals(model.inline_styles, u'margin-top: 50px;')
