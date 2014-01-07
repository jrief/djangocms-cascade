# -*- coding: utf-8 -*-
import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from cms.models.placeholdermodel import Placeholder
from cmsplugin_bootstrap.carousel import CarouselPlugin
from cmsplugin_bootstrap.change_form_widgets import ExtraStylesWidget
from cmsplugin_bootstrap.models import BootstrapElement


class CarouselPluginTest(TestCase):
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

    def test_render_carousel(self):
        carousel = CarouselPlugin()

        # check for options_widget
        self.assertIsInstance(carousel.options_widget, ExtraStylesWidget)
        self.assertEqual(len(carousel.options_widget.widgets), 2)
        value = '{"interval": 5000}'
        html = carousel.options_widget.render('dummy', value)
        self.assertInHTML('<input name="interval" placeholder="interval" type="text" value="5000" />', html)
        self.assertInHTML('<input name="pause" placeholder="pause" type="text" />', html)

    def test_save_carousel(self):
        add_url = '/admin/cms/page/add-plugin/'
        post_data = {u'plugin_parent': [u''], u'csrfmiddlewaretoken': [u'OXEt3SCDiB5lenLHx4z3Nkhn4OpnvEX2'], u'plugin_type': [u'CarouselPlugin'], u'plugin_language': [u'de'], u'placeholder_id': [str(self.placeholder.id)]}
        response = self.client.post(add_url, post_data)
        self.assertContains(response, '/admin/cms/page/edit-plugin/')
        change_url = json.loads(response.content)['url']
        obj_id = change_url.split('/')[-2]
        post_data = {u'_save': [u'Save'], u'interval': [u'5000'], u'csrfmiddlewaretoken': [u'OXEt3SCDiB5lenLHx4z3Nkhn4OpnvEX2'], u'_continue': [True]}
        response = self.client.post(change_url, post_data)
        self.assertContains(response, 'Change a page')
        saved_object = BootstrapElement.objects.get(id=obj_id)
        self.assertDictEqual({'pause': None, 'interval': u'5000'}, saved_object.options)
        self.assertEqual('data-interval=5000', saved_object.data_options)
