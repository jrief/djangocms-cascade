# -*- coding: utf-8 -*-
import os
import shutil
from tempfile import mkdtemp
import random
import colorsys

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.files import File as DjangoFile
from filer.utils.compatibility import PILImage, PILImageDraw
from filer.models.foldermodels import Folder
from filer.models.imagemodels import Image

def create_folder_structure(depth, sibling, name, parent=None):
    """
    This method creates a folder structure of the specified depth.
    * depth: is an integer (default=2)
    * sibling: is an integer (default=2)
    * parent: is the folder instance of the parent.
    """
    if depth > 0 and sibling > 0:
        depth_range = list(range(1, depth+1))
        depth_range.reverse()
        for d in depth_range:
            for s in range(1,sibling+1):
                folder = Folder(name=name, parent=parent)
                folder.save()
                create_folder_structure(depth=d-1, sibling=sibling, name=name, parent=folder)

def hsv2rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))

def ramdon_color():
    r, g, b = colorsys.hsv_to_rgb(320, 14, 55)
    intcolor = hsv2rgb(random.uniform(0.0, 1.0), 0.14, 0.80)
    return intcolor

def create_image(mode='RGB', size=(800, 600)):
    image = PILImage.new(mode, size, ramdon_color())
    size_desc = size
    if hasattr(settings, 'CLIPBOARD_LOGO'):
        filename = settings.CLIPBOARD_LOGO
    else:
        filename = finders.find('cascade/admin/djangocms_white_150x36.png')
    im = PILImage.open(filename)
    image.paste(im, (0,0), im)
    return image, size_desc

def create_filer_image(image, image_name, folder=None):
    file_obj = DjangoFile(open(image, 'rb'), name=image_name)
    image = Image.objects.create( original_filename=image_name,
                                  file=file_obj, folder=folder)
    return image

def gen_image( width, height, image_name):
    folder_name='CASCADE_IMG_GEN'
    if not Folder.objects.filter(name=folder_name).exists():
        create_folder_structure(1,1,name=folder_name)
    CASCADE_FILE_UPLOAD_TEMP_DIR = mkdtemp()
    img, size_desc = create_image(size=(width, height))
    img.folder = Folder.objects.filter(name=folder_name)[0]
    filename = os.path.join(CASCADE_FILE_UPLOAD_TEMP_DIR, image_name)
    quality_val = 90
    img.save(filename, 'JPEG', quality=quality_val)
    img_gen = create_filer_image(filename,image_name, Folder.objects.filter(name=folder_name)[0])
    shutil.rmtree(CASCADE_FILE_UPLOAD_TEMP_DIR)
    return img_gen.pk

def add_size_img_to_json(instance, plugin):
    plugin_data=plugin.get_data_representation(instance)['glossary']
    if 'image' in plugin.get_data_representation(instance)['glossary']:
        img = Image.objects.get(pk=plugin_data['image']['pk'])
        size = {'width':img._width, 'height':img._height}
        plugin_data['image'].update(size)

def gen_img_if_pk_and_size_not_match(data):
    if 'image' in data['glossary']:
       pk = data['glossary']['image']['pk']
       data_img_width = data['glossary']['image']['width']
       data_img_height = data['glossary']['image']['height']
       if Image.objects.filter(pk=pk).exists():
           img = Image.objects.filter(pk=pk)[0]
           if img.width == data['glossary']['image']['width'] and img.height == data['glossary']['image']['height']:
               pass
       else:
           gen_name = 'img_{}x{}.jpg'.format(data_img_width, data_img_height)
           img_gen_pk = gen_image(data_img_width,data_img_height, gen_name)
           data['glossary']['image']['pk'] = img_gen_pk

