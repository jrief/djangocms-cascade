from django.db import migrations
from cmsplugin_cascade.models import CascadeElement


def migrate_link(glossary):
    def foreign_key():
        return {'model': link['model'].lower(), 'pk': link['pk']}

    link = glossary.pop('link', None)
    if link:
        if link['type'] == 'cmspage':
            glossary.update({
                'link_type': 'cmspage',
                'cms_page': foreign_key(),
                'section': link['section'],
            })
        elif link['type'] == 'download':
            glossary.update({
                'link_type': 'download',
                'download_file': foreign_key(),
            })
        elif link['type'] == 'exturl':
            glossary.update({
                'link_type': 'exturl',
                'ext_url': link['url'],
            })
        elif link['type'] == 'email':
            glossary.update({
                'link_type': 'email',
                'mail_to': link['mail_to'],
            })
        elif link['type'] and link['type'] != 'none':
            glossary.update({
                'link_type': link['type'],
            })
        else:
            glossary.update({
                'link_type': '',
            })
        return True


def migrate_icon(glossary):
    icon_font = glossary.pop('icon_font', None)
    if icon_font and not isinstance(icon_font, dict):
        glossary.update({
            'icon_font': {'model': 'cmsplugin_cascade.iconfont', 'pk': int(icon_font)},
        })
        return True


def migrate_image(glossary):
    image = glossary.pop('image', None)
    if image:
        glossary.update({
            'image_file': {'model': 'filer.image', 'pk': image['pk']},
        })
        if 'width' in image and 'height' in image and 'exif_orientation' in image:
            glossary.update({
                '_image_properties': {'width': image['width'], 'height': image['height'],
                                      'exif_orientation': image['exif_orientation']},
            })
        return True


def forwards(apps, schema_editor):
    LINK_PLUGINS = ['TextLinkPlugin', 'LinkPlugin', 'BootstrapButtonPlugin', 'SimpleIconPlugin', 'FramedIconPlugin',
                    'BootstrapImagePlugin', 'BootstrapPicturePlugin', 'TextImagePlugin', 'TextIconPlugin']
    ICON_PLUGINS = ['BootstrapButtonPlugin', 'SimpleIconPlugin', 'FramedIconPlugin', 'TextIconPlugin']
    IMAGE_PLUGINS = ['BootstrapImagePlugin', 'BootstrapPicturePlugin', 'TextImagePlugin',
                     'BootstrapCarouselSlidePlugin', 'BootstrapJumbotronPlugin']
    for cascade_element in CascadeElement.objects.all():
        changed = False
        if cascade_element.plugin_type in LINK_PLUGINS:
            changed = migrate_link(cascade_element.glossary) or changed
        if cascade_element.plugin_type in ICON_PLUGINS:
            changed = migrate_icon(cascade_element.glossary) or changed
        if cascade_element.plugin_type in IMAGE_PLUGINS:
            changed = migrate_icon(cascade_element.glossary) or changed
        if changed:
            cascade_element.save()


def backwards(apps, schema_editor):
    print("Backward migration not implemented")


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0026_cascadepage_menu_symbol'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards),
    ]
