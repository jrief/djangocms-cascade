# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import pytest

from bs4 import BeautifulSoup

from django.core.files.uploadedfile import File
from django.template import RequestContext, Template
from django.test import RequestFactory

from cmsplugin_cascade.models import IconFont

from .test_base import CascadeTestCase


class StridePluginTest(CascadeTestCase):
    def setUp(self):
        request = RequestFactory().get('/')
        self.context = RequestContext(request, {})

    def test_bootstrap_jumbotron(self):
        template = Template('{% load cascade_tags sekizai_tags %}{% render_block "css" %}{% render_cascade "strides/bootstrap-jumbotron.json" %}')
        html = template.render(self.context)
        soup = BeautifulSoup(html, 'lxml')
        self.assertEqual(soup.style.text, '\n#cascadeelement_id-1501 {\n\tbackground-color: #12308b;\n\tbackground-attachment: scroll;\n\tbackground-position: center center;\n\tbackground-repeat: no-repeat;\n\tbackground-size: cover;\n\tpadding-top: 500px;\n}\n\n')
        element = soup.find(id='cascadeelement_id-1501')
        self.assertEqual(str(element), '<div class="jumbotron" id="cascadeelement_id-1501"><h1 style="text-align: center;"><span style="color: #ffffe0;">Manage your website</span></h1><p style="text-align: center;"><span style="color: #ffffe0;">with ease</span></p><p style="text-align: center;"></p><p style="text-align: center;"></p></div>')

    def test_bootstrap_container(self):
        template = Template('{% load cascade_tags %}{% render_cascade "strides/bootstrap-container.json" %}')
        html = template.render(self.context)
        soup = BeautifulSoup(html, 'lxml')
        element = soup.find(class_='container')
        self.assertEqual(str(element), '<div class="foo bar container">\n</div>')

    def test_bootstrap_row(self):
        template = Template('{% load cascade_tags %}{% render_cascade "strides/bootstrap-row.json" %}')
        html = template.render(self.context)
        soup = BeautifulSoup(html, 'lxml')
        element = soup.find(class_='row')
        self.assertEqual(str(element), '<div class="row" style="margin-bottom: 20px;">\n</div>')

    def test_bootstrap_column(self):
        template = Template('{% load cascade_tags %}{% render_cascade "strides/bootstrap-column.json" %}')
        html = template.render(self.context)
        soup = BeautifulSoup(html, 'lxml')
        element = soup.find(class_='col-xs-12')
        self.assertEqual(str(element), '<div class="col-xs-12">\n</div>')

    @pytest.mark.skip
    def test_simple_wrapper(self):
        template = Template('{% load cascade_tags %}{% render_cascade "strides/simple-wrapper.json" %}')
        html = template.render(self.context)
        soup = BeautifulSoup(html, 'lxml')
        # TODO: styles might be out of order
        self.assertEqual(str(soup.div), '<div style="background-color: #42c8c6; padding-right: 50px; height: 360px; color: #ffffff; padding-left: 50px;">\n</div>')

    @pytest.mark.skip
    def test_framed_icon(self):
        config_file = os.path.join(os.path.dirname(__file__), 'assets/fontello-config-data.json')
        with open(config_file) as fp:
            config_data = json.load(fp)
        zip_file = os.path.join(os.path.dirname(__file__), 'assets/fontello-b504201f.zip')
        with open(zip_file) as fp:
            zip_file = File(fp)
        IconFont.objects.create(
            id=1,  # to match id in fixture "strides/framed-icon.json"
            identifier="fontawesome",
            config_data=config_data,
            zip_file=zip_file,
            font_folder='no-file',
        )

        template = Template('{% load cascade_tags sekizai_tags %}{% render_block "css" %}{% render_cascade "strides/framed-icon.json" %}')
        html = template.render(self.context)
        soup = BeautifulSoup(html, 'lxml')
        print(soup.prettify())
        self.assertEqual(str(soup.div), '<div style="background-color: #42c8c6; padding-right: 50px; height: 360px; color: #ffffff; padding-left: 50px;">\n</div>')
