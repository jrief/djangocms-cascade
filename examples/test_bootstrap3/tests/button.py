# -*- coding: utf-8 -*-
import json
from django.test import TestCase
from django.forms.widgets import RadioSelect, TextInput
from django.contrib.auth.models import User
from django.test.client import Client
from cms.models.placeholdermodel import Placeholder
from cmsplugin_cascade.widgets import JSONMultiWidget, NumberInputWidget, MultipleTextInputWidget
from cmsplugin_cascade.models import CascadeElement
from cmsplugin_cascade.bootstrap3.buttons import ButtonWrapperPlugin


class ButtonWrapperPluginTest(TestCase):
    admin_password = 'secret'
    client = Client()

    def setUp(self):
        self.createAdminUser()
        self.placeholder = Placeholder.objects.create()

    def createAdminUser(self):
        self.user = User.objects.create_user('admin', 'admin@example.com', self.admin_password)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        logged_in = self.client.login(username=self.user.username, password=self.admin_password)
        self.assertTrue(logged_in, 'User is not logged in')

    def test_render_button(self):
        button_wrapper = ButtonWrapperPlugin()

        # check for extra_classes_widget
        #self.assertIsInstance(button_wrapper.extra_classes_widget, MultipleRadioButtonsWidget)
        self.assertEqual(len(button_wrapper.extra_classes_widget.widgets), 2)
        self.assertIsInstance(button_wrapper.extra_classes_widget.widgets[0], RadioSelect)
        self.assertIsInstance(button_wrapper.extra_classes_widget.widgets[0].choices, list)
        value = '{"buttonsize":"btn-small", "buttontype":"btn-success"}'
        html = button_wrapper.extra_classes_widget.render('dummy', value)
        self.assertInHTML('<input checked="checked" name="buttonsize" type="radio" value="btn-small" />', html)

        # check for extra_styles_widget
        #self.assertIsInstance(button_wrapper.extra_styles_widget, ExtraStylesWidget)
        self.assertEqual(len(button_wrapper.extra_styles_widget.widgets), 4)
        self.assertIsInstance(button_wrapper.extra_styles_widget.widgets[0], TextInput)
        self.assertDictContainsSubset(button_wrapper.extra_styles_widget.widgets[0].attrs, {'placeholder': 'margin-top'})
        value = '{"margin-right":null, "margin-top":null, "margin-left":"35px", "margin-bottom":null}'
        html = button_wrapper.extra_styles_widget.render('dummy', value)
        self.assertInHTML('<input name="margin-left" placeholder="margin-left" type="text" value="35px" />', html)

        # check for tagged_classes_widget
        #self.assertIsInstance(button_wrapper.tagged_classes_widget, MultipleCheckboxesWidget)
        self.assertEqual(len(button_wrapper.tagged_classes_widget.choices), 1)
        self.assertIsInstance(button_wrapper.tagged_classes_widget.choices[0], tuple)
        value = '["disabled"]'
        html = button_wrapper.tagged_classes_widget.render('dummy', value)
        self.assertInHTML('<input checked="checked" name="dummy" type="checkbox" value="disabled" />', html)

    def test_save_button(self):
        add_url = '/admin/cms/page/add-plugin/'
        post_data = {u'plugin_parent': [u''], u'csrfmiddlewaretoken': [u'OXEt3SCDiB5lenLHx4z3Nkhn4OpnvEX2'], u'plugin_type': [u'ButtonWrapperPlugin'], u'plugin_language': [u'de'], u'placeholder_id': [str(self.placeholder.id)]}
        response = self.client.post(add_url, post_data)
        self.assertContains(response, '/admin/cms/page/edit-plugin/')
        change_url = json.loads(response.content)['url']
        obj_id = change_url.split('/')[-2]
        post_data = {u'_save': [u'Save'], u'margin-left': [u''], u'buttontype': [u'btn-link'], u'margin-bottom': [u''], u'_popup': [u'1'], u'margin-top': [u'1em'], u'tagged_classes': [u'disabled'], u'buttonsize': [u'btn-mini'], u'margin-right': [u''], u'csrfmiddlewaretoken': [u'OXEt3SCDiB5lenLHx4z3Nkhn4OpnvEX2'], u'_continue': [True]}
        response = self.client.post(change_url, post_data)
        self.assertContains(response, 'Change a page')
        saved_object = CascadeElement.objects.get(id=obj_id)
        self.assertDictEqual({'buttonsize': 'btn-mini', 'buttontype': 'btn-link'}, saved_object.extra_classes)
        self.assertDictContainsSubset({'margin-top': '1em'}, saved_object.extra_styles)
        self.assertListEqual(['disabled'], saved_object.tagged_classes)
        self.assertEqual('btn btn-mini btn-link disabled', saved_object.css_classes)
        self.assertEqual('margin-top: 1em;', saved_object.inline_styles)
