# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from cms.api import create_page
from cms.admin.pageadmin import PageAdmin
from cms.models.placeholdermodel import Placeholder
from cms.test_utils.testcases import CMSTestCase
from django.template.context import Context


class CascadeTestCase(CMSTestCase):
    admin_password = 'secret'
    home_page = None

    def setUp(self):
        self.create_admin_user()
        self.home_page = create_page('HOME', 'cascade/testing.html', 'en', published=True, in_navigation=True,
            created_by=self.user)
        self.placeholder = Placeholder.objects.create(slot='Main Content')
        self.placeholder.page_set.add(self.home_page)
        self.placeholder.save()
        self.request = self.get_request(language='en', page=self.home_page)
        self.admin_site = admin.sites.AdminSite()
        self.page_admin = PageAdmin(self.home_page, self.admin_site)

    def create_admin_user(self):
        self.user = User.objects.create_user('admin', 'admin@example.com', self.admin_password)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        logged_in = self.client.login(username=self.user.username, password=self.admin_password)
        self.assertTrue(logged_in, "User is not logged in")

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
