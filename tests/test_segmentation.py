# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bs4 import BeautifulSoup

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

from cms.api import add_plugin
from cms.utils.plugins import build_plugin_tree
from djangocms_text_ckeditor.cms_plugins import TextPlugin
from cmsplugin_cascade.generic.cms_plugins import SimpleWrapperPlugin
from cmsplugin_cascade.segmentation.cms_plugins import SegmentPlugin

from .test_base import CascadeTestCase


class SegmentationPluginTest(CascadeTestCase):
    def setUp(self):
        super(SegmentationPluginTest, self).setUp()
        UserModel = get_user_model()
        try:
            self.staff_user = UserModel.objects.get(username='staff')
        except UserModel.DoesNotExist:
            self.staff_user = self.get_staff_user_with_no_permissions()
        try:
            self.staff_user = UserModel.objects.get(username='staff')
        except UserModel.DoesNotExist:
            self.staff_user = self.get_staff_user_with_no_permissions()

    def test_plugin_context(self):
        # create container
        wrapper_model = add_plugin(self.placeholder, SimpleWrapperPlugin, 'en',
            glossary={'tag_type': 'naked'})
        wrapper_plugin = wrapper_model.get_plugin_class_instance(self.admin_site)
        self.assertIsInstance(wrapper_plugin, SimpleWrapperPlugin)

        # add an `if`-segment with some text as child
        if_segment_model = add_plugin(self.placeholder, SegmentPlugin, 'en', target=wrapper_model,
                               glossary={'open_tag': 'if', 'condition': 'user.is_superuser'})
        self.assertIsInstance(if_segment_model.get_plugin_class_instance(), SegmentPlugin)
        text_model_admin = add_plugin(self.placeholder, TextPlugin, 'en', target=if_segment_model,
            body='<p>User is admin</p>')
        self.assertIsInstance(text_model_admin.get_plugin_class_instance(), TextPlugin)

        # add an `elif`-segment with some text as child
        elif_segment_model = add_plugin(self.placeholder, SegmentPlugin, 'en', target=wrapper_model,
                               glossary={'open_tag': 'elif', 'condition': 'user.is_authenticated'})
        self.assertIsInstance(elif_segment_model.get_plugin_class_instance(), SegmentPlugin)
        text_model_staff = add_plugin(self.placeholder, TextPlugin, 'en', target=elif_segment_model,
            body='<p>User is staff</p>')
        self.assertIsInstance(text_model_staff.get_plugin_class_instance(), TextPlugin)

        # add an `else`-segment with some text as child
        else_segment_model = add_plugin(self.placeholder, SegmentPlugin, 'en', target=wrapper_model,
                               glossary={'open_tag': 'else'})
        self.assertIsInstance(else_segment_model.get_plugin_class_instance(), SegmentPlugin)
        text_model_anon = add_plugin(self.placeholder, TextPlugin, 'en', target=else_segment_model,
            body='<p>User is anonymous</p>')
        self.assertIsInstance(text_model_anon.get_plugin_class_instance(), TextPlugin)

        # build the DOM
        plugin_list = [wrapper_model, if_segment_model, text_model_admin, elif_segment_model,
                       text_model_staff, else_segment_model, text_model_anon]
        build_plugin_tree(plugin_list)

        # render the plugins as admin user
        soup = BeautifulSoup(self.get_html(wrapper_model, self.get_request_context()), 'html.parser')
        self.assertHTMLEqual(soup.p.text, 'User is admin')

        # render the plugins as staff user
        self.request.user = self.staff_user
        soup = BeautifulSoup(self.get_html(wrapper_model, self.get_request_context()), 'html.parser')
        self.assertHTMLEqual(soup.p.text, 'User is staff')

        # render the plugins as anonymous user
        self.request.user = AnonymousUser
        soup = BeautifulSoup(self.get_html(wrapper_model, self.get_request_context()), 'html.parser')
        self.assertHTMLEqual(soup.p.text, 'User is anonymous')
