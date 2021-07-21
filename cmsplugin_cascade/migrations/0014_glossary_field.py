from django.db import migrations

FIELD_MAPPINGS = {
    'BootstrapButtonPlugin': [
        ('button-type', 'button_type'),
        ('button-size', 'button_size'),
        ('button-options', 'button_options'),
        ('quick-float', 'quick_float'),
        ('icon-left', 'icon_left'),
        ('icon-right', 'icon_right'),
    ],
    'CarouselPlugin': [
        ('resize-options', 'resize_options'),
    ],
    'BootstrapGalleryPlugin': [
        ('image-shapes', 'image_shapes'),
        ('image-width-responsive', 'image_width_responsive'),
        ('image-width-fixed', 'image_width_fixed'),
        ('image-height', 'image_height'),
        ('thumbnail-width', 'thumbnail_width'),
        ('thumbnail-height', 'thumbnail_height'),
        ('resize-options', 'resize_options'),
    ],
    'BootstrapImagePlugin': [
        ('image-title', 'image_title'),
        ('alt-tag', 'alt_tag'),
        ('image-shapes', 'image_shapes'),
        ('image-width-responsive', 'image_width_responsive'),
        ('image-width-fixed', 'image_width_fixed'),
        ('image-height', 'image_height'),
        ('resize-options', 'resize_options'),
    ],
    'BootstrapJumbotronPlugin': [
        ('background-color', 'background_color'),
        ('background-repeat', 'background_repeat'),
        ('background-attachment', 'background_attachment'),
        ('background-vertical-position', 'background_vertical_position'),
        ('background-horizontal-position', 'background_horizontal_position'),
        ('background-size', 'background_size'),
        ('background-width-height', 'background_width_height'),
    ],
    'BootstrapPicturePlugin': [
        ('image-title', 'image_title'),
        ('alt-tag', 'alt_tag'),
        ('responsive-heights', 'responsive_heights'),
        ('responsive-zoom', 'responsive_zoom'),
        ('resize-options', 'resize_options'),
    ]
}


def forwards(apps, schema_editor):
    field_mappings = {}
    for key, maps in FIELD_MAPPINGS.items():
        field_mappings[key] = dict(maps)
    migrate_glossary(apps, field_mappings)


def backwards(apps, schema_editor):
    field_mappings = {}
    for key, maps in FIELD_MAPPINGS.items():
        field_mappings[key] = dict((m[1], m[0]) for m in maps)
    migrate_glossary(apps, field_mappings)


def migrate_glossary(apps, field_mappings):
    CascadeElement = apps.get_model('cmsplugin_cascade', 'CascadeElement')
    for element in CascadeElement.objects.all():
        if element.plugin_type not in field_mappings:
            continue
        glossary = dict(element.glossary)
        for srckey, value in element.glossary.items():
            dstkey = field_mappings[element.plugin_type].get(srckey)
            if dstkey and srckey in glossary:
                glossary[dstkey] = glossary.pop(srckey)
        element.glossary = glossary
        element.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0013_iconfont'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards),
    ]
