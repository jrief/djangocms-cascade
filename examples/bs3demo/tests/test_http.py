# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.conf import settings
from django.contrib import admin
from django.test import modify_settings
from cms.models import Page
from cms.utils.compat.dj import is_installed
from cms.test_utils.testcases import CMSTestCase, URL_CMS_PAGE_ADD, URL_CMS_PLUGIN_ADD


class ContainerPluginTest(CMSTestCase):
    def setUp(self):
        self.admin_site = admin.sites.AdminSite()
        self.user = self.get_superuser()
        self.password = "top_secret"
        self.user.set_password(self.password)
        self.user.save()
        self.client.login(username=self.user.username, password=self.password)
        self.language = 'en-us'
        self.site_id = settings.SITE_ID

        # create page
        response = self.client.post(
            URL_CMS_PAGE_ADD[3:],
            data={
                'language': self.language,
                'site': self.site_id,
                'template': 'INHERIT',
                'title': 'HOME',
                'slug': 'home',
                '_save': 'Save',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        # get page and placeholder
        self.page = Page.objects.get(publisher_is_draft=True, is_home=True)
        self.placeholder = self.page.placeholders.get(slot='Main Content')

    def _create_and_configure_a_container_plugin(self):
        # create a plugin
        response = self.client.post(
            URL_CMS_PLUGIN_ADD[3:],
            data={
                'plugin_parent': '',
                'plugin_type': 'BootstrapContainerPlugin',
                'plugin_language': self.language,
                'placeholder_id': self.placeholder.id,
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        plugin_url = response_data['url']

        # configure that plugin
        response = self.client.post(
            plugin_url,
            data={
                '_popup': '1',
                'breakpoints': ['xs', 'lg'],
                '_save': 'Save',
            },
        )
        self.assertEqual(response.status_code, 200)

    @modify_settings(INSTALLED_APPS={'remove': 'reversion'})
    def test_without_reversion(self):
        self.assertFalse(is_installed('reversion'))
        self._create_and_configure_a_container_plugin()

    def test_with_reversion(self):
        self.assertTrue(is_installed('reversion'))
        self._create_and_configure_a_container_plugin()

