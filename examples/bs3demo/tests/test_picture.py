# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from bs4 import BeautifulSoup
from django.core.files import File as DjangoFile
from django.http import QueryDict
from django.template import RequestContext
from filer.models.foldermodels import Folder
from filer.models.imagemodels import Image
from cms.api import add_plugin
from cms.utils.plugins import build_plugin_tree
from cmsplugin_cascade.sharable.models import SharableCascadeElement
from cmsplugin_cascade.bootstrap3.container import (BootstrapContainerPlugin, BootstrapRowPlugin,
        BootstrapColumnPlugin)
from cmsplugin_cascade.bootstrap3.picture import BootstrapPicturePlugin
from cmsplugin_cascade.bootstrap3.settings import CASCADE_BREAKPOINTS_LIST
from .test_base import CascadeTestCase


class PicturePluginTest(CascadeTestCase):
    maxDiff = None

    def upload_demo_image(self):
        demo_image = os.path.abspath(os.path.join(os.path.dirname(__file__), 'demo_image.png'))
        folder, dummy = Folder.objects.get_or_create(name='Samples', parent=None)
        file_obj = DjangoFile(open(demo_image, 'rb'), name='demo_image.png')
        image = Image.objects.create(owner=self.user, original_filename='Demo Image',
                                     file=file_obj, folder=folder)
        return image

    def test_plugin_context(self):
        # create container
        container_model = add_plugin(self.placeholder, BootstrapContainerPlugin, 'en',
            glossary={'breakpoints': CASCADE_BREAKPOINTS_LIST})
        container_plugin = container_model.get_plugin_class_instance(self.admin_site)
        self.assertIsInstance(container_plugin, BootstrapContainerPlugin)

        # add one row
        row_model = add_plugin(self.placeholder, BootstrapRowPlugin, 'en', target=container_model,
                               glossary={})
        row_plugin = row_model.get_plugin_class_instance()
        self.assertIsInstance(row_plugin, BootstrapRowPlugin)

        # add one column
        column_model = add_plugin(self.placeholder, BootstrapColumnPlugin, 'en', target=row_model,
            glossary={'xs-column-width': 'col-xs-12', 'sm-column-width': 'col-sm-6',
                      'md-column-width': 'col-md-4', 'lg-column-width': 'col-lg-3'})
        column_plugin = column_model.get_plugin_class_instance()
        self.assertIsInstance(column_plugin, BootstrapColumnPlugin)

        # add a picture
        picture_model = add_plugin(self.placeholder, BootstrapPicturePlugin, 'en', target=column_model)
        self.assertIsInstance(picture_model, SharableCascadeElement)
        picture_plugin = picture_model.get_plugin_class_instance(self.admin_site)
        self.assertIsInstance(picture_plugin, BootstrapPicturePlugin)
        picture_plugin.cms_plugin_instance = picture_model.cmsplugin_ptr

        # upload an image and change the form
        ModelForm = picture_plugin.get_form(self.request, picture_model)
        image = self.upload_demo_image()
        post_data = QueryDict('', mutable=True)
        post_data.update({'image_file': image.pk, 'link_type': 'none', 'image-size-width': '300px'})
        form = ModelForm(post_data, None, instance=picture_model)
        self.assertTrue(form.is_valid())
        picture_plugin.save_model(self.request, picture_model, form, False)

        # render the plugins
        plugin_list = [container_model, row_model, column_model, picture_model]
        build_plugin_tree(plugin_list)
        context = RequestContext(self.request, {})
        html = container_model.render_plugin(context)
        soup = BeautifulSoup(html)
        self.assertEqual(soup.img['height'], '100')
        self.assertEqual(soup.img['width'], '300')
        self.assertTrue(soup.img['src'].endswith('demo_image.png__300x100_q85_subsampling-2.png'))

        # use a responsive image
        post_data.setlist('image-shapes', ['img-responsive'])
        form = ModelForm(post_data, None, instance=picture_model)
        self.assertTrue(form.is_valid())
        picture_plugin.save_model(self.request, picture_model, form, False)
        html = container_model.render_plugin(context)
        soup = BeautifulSoup(html)
        sources = dict((s['media'], s['srcset']) for s in soup.picture.find_all('source'))
        self.assertTrue(sources['(max-width: 768px)'].endswith('demo_image.png__720x240_q85_subsampling-2.png'))
        self.assertTrue(sources['(min-width: 768px) and (max-width: 992px)'].endswith('demo_image.png__345x115_q85_subsampling-2.png'))
        self.assertTrue(sources['(min-width: 992px) and (max-width: 1200px)'].endswith('demo_image.png__293x98_q85_subsampling-2.png'))
        self.assertTrue(sources['(min-width: 1200px)'].endswith('demo_image.png__262x87_q85_subsampling-2.png'))
        self.assertTrue('img-responsive' in soup.picture.img['class'])
        self.assertTrue(soup.picture.img['src'].endswith('demo_image.png__100x33_q85_subsampling-2.png'))
