# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.template.context import Context

from cms.api import create_page
from cms.test_utils.testcases import CMSTestCase
from cmsplugin_cascade.models import CascadePage


class CascadeTestCase(CMSTestCase):
    home_page = None

    def setUp(self):
        self.home_page = create_page(title='HOME', template='testing.html', language='en')
        if not self.home_page.is_home:
            # >= Django CMS v3.5.x
            self.home_page.set_as_homepage()
        CascadePage.assure_relation(self.home_page)

        self.placeholder = self.home_page.placeholders.get(slot='Main Content')

        self.request = self.get_request(self.home_page, 'en')
        self.admin_site = admin.sites.AdminSite()

        UserModel = get_user_model()
        UserModel.objects.get_or_create(
            username='admin',
            is_staff=True,
            is_superuser=True,
            is_active=True,
            password=make_password('admin'),
        )
        UserModel.objects.get_or_create(
            username='staff',
            is_staff=True,
            is_superuser=False,
            is_active=True,
            password=make_password('staff'),
        )

    def get_request_context(self):
        context = {}
        context['request'] = self.request
        context['user'] = self.request.user
        try:
            # >= Django CMS v3.4.x
            context['cms_content_renderer'] = self.get_content_renderer(request=self.request)
        except AttributeError:
            # < Django CMS v3.4.x
            pass
        return Context(context)

    def get_html(self, model_instance, context):
        try:
            # >= Django CMS v3.4.x
            return context['cms_content_renderer'].render_plugin(model_instance, context)
        except KeyError:
            # < Django CMS v3.4.x
            return model_instance.render_plugin(context)
