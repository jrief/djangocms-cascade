from django.db import migrations

def forwards(apps, schema_editor):
    CascadeElement = apps.get_model('cmsplugin_cascade', 'CascadeElement')
    for element in CascadeElement.objects.using(schema_editor.connection.alias).filter(plugin_type='HeadingPlugin'):
        head_size = element.glossary.pop('head_size', None)
        if head_size:
            element.glossary['tag_type'] = 'h{}'.format(head_size)
            element.save()


def backwards(apps, schema_editor):
    CascadeElement = apps.get_model('cmsplugin_cascade', 'CascadeElement')
    for element in CascadeElement.objects.using(schema_editor.connection.alias).filter(plugin_type='HeadingPlugin'):
        tag_type = element.glossary.pop('tag_type', None)
        if tag_type and len(tag_type) == 2:
            element.glossary['head_size'] = tag_type[1]
            element.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0009_cascadepage'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards),
    ]
