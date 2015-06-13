# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from cms.api import create_page
from cms.test_utils.testcases import CMSTestCase, URL_CMS_PLUGIN_ADD
from cms.utils.compat.dj import is_installed
from django.contrib import admin
from django.test import Client
from django.test.utils import modify_settings


class ContainerPluginTest(CMSTestCase):
    def setUp(self):
        self.page = create_page('HOME', 'testing.html', 'en-us', published=True, in_navigation=True)
        self.placeholder = self.page.placeholders.get(slot='Main Content')
        self.admin_site = admin.sites.AdminSite()
        self.user = self.get_superuser()
        self.password = "top_secret"
        self.user.set_password(self.password)
        self.user.save()
        self.client.login(username=self.user.username, password=self.password)

    @modify_settings(INSTALLED_APPS={
        'remove': 'reversion',
    })
    def test_without_reversion(self):
        self.assertFalse(is_installed('reversion'))
        response = self.client.post(
            URL_CMS_PLUGIN_ADD[3:],
            data={
                'plugin_parent': '',
                'plugin_type': 'BootstrapContainerPlugin',
                'plugin_language': 'en-us',
                'placeholder_id': self.placeholder.id,
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)

    def test_with_reversion(self):
        self.assertTrue(is_installed('reversion'))
        response = self.client.post(
            URL_CMS_PLUGIN_ADD[3:],
            data={
                'plugin_parent': '',
                'plugin_type': 'BootstrapContainerPlugin',
                'plugin_language': 'en-us',
                'placeholder_id': unicode(self.placeholder.id),
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
