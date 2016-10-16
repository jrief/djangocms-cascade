# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.contrib import admin
from django.core.files import File as DjangoFile
from django.http import QueryDict
from filer.models.foldermodels import Folder
from filer.models.imagemodels import Image
from cms.api import add_plugin, create_page
from cms.utils.plugins import build_plugin_tree
from cmsplugin_cascade.bootstrap3.container import (BootstrapContainerPlugin, BootstrapRowPlugin,
        BootstrapColumnPlugin)
from cmsplugin_cascade.bootstrap3.jumbotron import BootstrapJumbotronPlugin, ImageBackgroundMixin
from cmsplugin_cascade.bootstrap3 import settings
from cmsplugin_cascade.mixins import ImagePropertyMixin
from .test_base import CascadeTestCase
from .utils import get_request_context

BS3_BREAKPOINT_KEYS = list(tp[0] for tp in settings.CMSPLUGIN_CASCADE['bootstrap3']['breakpoints'])


class JumbotronPluginTest(CascadeTestCase):
    def setUp(self):
        super(JumbotronPluginTest, self).setUp()
        self.image = self.upload_demo_image()

    def upload_demo_image(self):
        demo_image = os.path.abspath(os.path.join(os.path.dirname(__file__), 'demo_image.png'))
        folder, dummy = Folder.objects.get_or_create(name='Samples', parent=None)
        file_obj = DjangoFile(open(demo_image, 'rb'), name='demo_image.png')
        image = Image.objects.create(owner=self.user, original_filename='Demo Image',
                                     file=file_obj, folder=folder)
        return image

    def test_jumbotron_plugin(self):
        # create container
        container_model = add_plugin(self.placeholder, BootstrapContainerPlugin, 'en',
            glossary={'breakpoints': BS3_BREAKPOINT_KEYS})
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

        # add Jumbotron plugin
        jumbotron_model = add_plugin(self.placeholder, BootstrapJumbotronPlugin, 'en', target=column_model)
        self.assertIsInstance(jumbotron_model, ImagePropertyMixin)
        self.assertIsInstance(jumbotron_model, ImageBackgroundMixin)
        jumbotron_plugin = jumbotron_model.get_plugin_class_instance(self.admin_site)
        self.assertIsInstance(jumbotron_plugin, BootstrapJumbotronPlugin)
        jumbotron_plugin.cms_plugin_instance = jumbotron_model.cmsplugin_ptr

        # edit jumbotron model
        post_data = QueryDict('', mutable=True)
        post_data.update({
            'background_size': 'auto',
            'background_repeat': 'no-repeat',
            'background_width-height-width': '',
            'background_attachment': 'fixed',
            'background_color_color': '#aabbcc',
            'background_color_disabled': '',
            'background_vertical_position': 'center',
            'background_horizontal_position': 'center',
            'breakpoints': ['xs', 'sm', 'md', 'lg'],
            'extra_inline_styles:Paddings-padding-bottom': '',
            'background-width-height-height': '',
            'container_max_heights-xs': '100%',
            'container_max_heights-sm': '100%',
            'container_max_heights-md': '100%',
            'container_max_heights-lg': '100%',
            'extra_inline_styles:Paddings-padding-top': '200px',
            'resize_options': ['crop', 'subject_location', 'high_resolution'],
            'image_file': str(self.image.pk),
        })

        ModelForm = jumbotron_plugin.get_form(self.request, jumbotron_model)
        form = ModelForm(post_data, None, instance=jumbotron_model)
        self.assertTrue(form.is_valid())
        jumbotron_plugin.save_model(self.request, jumbotron_model, form, False)

        del jumbotron_model._image_model  # invalidate cache
        self.assertEqual(jumbotron_plugin.get_identifier(jumbotron_model), 'Demo Image')

        # render the plugins
        plugin_list = [container_model, row_model, column_model, jumbotron_model]
        build_plugin_tree(plugin_list)
        context = get_request_context(self.request)

        html = container_model.render_plugin(context)
        print(html)
        self.assertHTMLEqual("""
<div class="container"><div class="row"><div class="col-xs-12 col-sm-6 col-md-4 col-lg-3">
  <div id="cascadeelement_id-{}" class="jumbotron"></div>
</div></div></div>""".format(jumbotron_model.pk), html)
        self.assertEqual('background-color: #aabbcc;', jumbotron_model.background_color)
        self.assertEqual('background-position: center center;', jumbotron_model.background_position)
        self.assertEqual('background-repeat: no-repeat;', jumbotron_model.background_repeat)
        self.assertEqual('background-attachment: fixed;', jumbotron_model.background_attachment)
        self.assertEqual('background-size: auto;', jumbotron_model.background_size)
