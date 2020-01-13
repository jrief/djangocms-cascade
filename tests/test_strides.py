# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import django
import os

from bs4 import BeautifulSoup

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.template import RequestContext, Template
from django.test import RequestFactory


from cmsplugin_cascade.models import IconFont
from filer.admin.clipboardadmin import ajax_upload

from .test_base import CascadeTestCase


class StridePluginTest(CascadeTestCase):
    def setUp(self):
        request = RequestFactory().get('/')
        self.context = RequestContext(request, {})

    def assertStyleEqual(self, provided, expected):
        styles = dict((pair.split(':')[0].strip(), pair.split(':')[1].strip())
                      for pair in provided.split(';') if ':' in pair)
        self.assertDictEqual(styles, expected)

    def skiptest_bootstrap_jumbotron(self):
        template = Template('{% load cascade_tags sekizai_tags %}{% render_block "css" %}{% render_cascade "strides/bootstrap-jumbotron.json" %}')
        html = template.render(self.context)
        soup = BeautifulSoup(html, features='lxml')
        self.assertEqual(soup.style.text.find('#cascadeelement_id-1501 {\n\tbackground-color: #12308b;\n\tbackground-attachment: scroll;\n\tbackground-position: center center;\n\tbackground-repeat: no-repeat;\n\tbackground-size: cover;\n\tpadding-top: 500px;'), 1 )
        element = soup.find(id='cascadeelement_id-1501')
        self.assertEqual(element.h1.text, "Manage your website")
        self.assertStyleEqual(element.h1.attrs['style'], {'text-align': 'center'})

    def test_bootstrap_container(self):
        template = Template('{% load cascade_tags %}{% render_cascade "strides/bootstrap-container.json" %}')
        html = template.render(self.context)
        soup = BeautifulSoup(html, features='lxml')
        element = soup.find(class_='container')
        self.assertSetEqual(set(element.attrs['class']), {'foo', 'bar', 'container'})

    def skiptest_bootstrap_row(self):
        template = Template('{% load cascade_tags %}{% render_cascade "strides/bootstrap-row.json" %}')
        html = template.render(self.context)
        soup = BeautifulSoup(html, features='lxml')
        self.assertEqual(str(soup.div), '<div class="row" style="margin-bottom: 20px;">\n</div>')

    def skiptest_bootstrap_column(self):
        template = Template('{% load cascade_tags %}{% render_cascade "strides/bootstrap-column.json" %}')
        html = template.render(self.context)
        soup = BeautifulSoup(html, features='lxml')
        self.assertEqual(str(soup.div), '<div class="col-xs-12">\n</div>')

    def skiptest_simple_wrapper(self):
        template = Template('{% load cascade_tags %}{% render_cascade "strides/simple-wrapper.json" %}')
        html = template.render(self.context)
        soup = BeautifulSoup(html, features='lxml')
        expected_styles = {
            'background-color':'#42c8c6',
            'color':'#ffffff',
            'height':'360px',
            'padding-left':'50px',
            'padding-right':'50px',
        }
        self.assertStyleEqual(soup.div.attrs['style'], expected_styles)

    def upload_icon_font(self):
        UserModel = get_user_model()
        admin_user = UserModel.objects.get(username='admin')
        with self.login_user_context(admin_user):
            filename = os.path.join(os.path.dirname(__file__), 'assets/fontello-b504201f.zip')
            with open(filename, 'rb') as zipfile:
                uploaded_file = SimpleUploadedFile('fontello-b504201f.zip', zipfile.read(), content_type='application/zip')
            request = self.get_request(reverse('admin:filer-ajax_upload'))
            request.FILES.update(file=uploaded_file)
            response = ajax_upload(request)
            self.assertEqual(response.status_code, 200)
            content = json.loads(response.content.decode('utf-8'))

            # save the form and submit the remaining fields
            add_iconfont_url = reverse('admin:cmsplugin_cascade_iconfont_add')
            data = {
                'identifier': "Fontellico",
                'zip_file': content['file_id'],
                '_continue': "Save and continue editing",
            }
            response = self.client.post(add_iconfont_url, data)
            self.assertEqual(response.status_code, 302)
        self.assertEqual(IconFont.objects.count(), 1)

    def test_framed_icon(self):
        self.upload_icon_font()
        icon_font = IconFont.objects.first()
        icon_font.id = 1  # to match id in fixture "strides/framed-icon.json"
        icon_font.save()

        template = Template('{% load cascade_tags sekizai_tags %}{% render_block "css" %}{% render_cascade "strides/framed-icon.json" %}')
        html = template.render(self.context)
        soup = BeautifulSoup(html, features='lxml')
        self.assertSetEqual(set(soup.div.attrs['class']), {'text-center'})
        self.assertStyleEqual(soup.div.attrs['style'], {'font-size': '10em'})
        expected_style = {
            'color': '#ffffff',
            'display': 'inline-block',
        }
        self.assertStyleEqual(soup.div.span.attrs['style'], expected_style)

    def test_text_plugin(self):
        template = Template('{% load cascade_tags %}{% render_cascade "strides/text-plugin.json" %}')
        html = template.render(self.context)
        soup = BeautifulSoup(html, features='lxml')
        self.assertEqual(soup.h2.text, "Customizable")
        self.assertStyleEqual(soup.h2.attrs['style'], {'text-align': 'center'})
        self.assertEqual(soup.p.text, "Lorem ipsum dolor")

    def test_carousel_plugin(self):
        template = Template('{% load cascade_tags %}{% render_cascade "strides/carousel-plugin.json" %}')
        html = template.render(self.context)
        soup = BeautifulSoup(html, features='lxml')
        carousel = soup.find(class_='carousel')
        self.assertSetEqual(set(carousel.attrs['class']), {'carousel', 'slide', 'pause', 'wrap', 'slide'})
        self.assertListEqual(carousel.ol.attrs['class'], ['carousel-indicators'])
        self.assertListEqual(carousel.ol.li.attrs['class'], ['active'])
        slide = carousel.find(class_='carousel-inner')
        self.assertSetEqual(set(slide.div.attrs['class']), {'carousel-item', 'active'})

    def test_navbar_plugin(self):
        template = Template('{% load cascade_tags %}{% render_cascade "strides/bootstrap-navbar.json" %}')
        html = template.render(self.context)
        soup = BeautifulSoup(html, features='lxml')
        navbar = soup.find(class_='navbar')
        self.assertSetEqual(set( navbar.attrs['class']), {'navbar', 'navbar-expand-md','navbar-light','bg-transparent' })

    def test_button_plugin(self):
        template = Template('{% load cascade_tags %}{% render_cascade "strides/bootstrap-button.json" %}')
        html = template.render(self.context)
        soup = BeautifulSoup(html, features='lxml')
        button = soup.find(class_='btn')
        self.assertSetEqual(set(button.attrs['class']), {'btn', 'btn-secondary'})
