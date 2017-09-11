# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.template.context import Context

from cms.api import create_page
from cms.test_utils.testcases import CMSTestCase

from djangocms_helper.base_test import BaseTestCase


class CascadeTestCase(CMSTestCase, BaseTestCase):
    home_page = None

    def setUp(self):
        self.home_page = create_page(title='HOME', template='testing.html', language='en')
        self.placeholder = self.home_page.placeholders.get(slot='Main Content')

        self.request = self.get_request(self.home_page, 'en')
        self.admin_site = admin.sites.AdminSite()

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
