from django.db import migrations
from django.conf import settings


def forwards(apps, schema_editor):
    CascadePage = apps.get_model('cmsplugin_cascade', 'CascadePage')

    for cascade_page in CascadePage.objects.all():
        try:
            element_ids = cascade_page.glossary.pop('element_ids')
        except:
            continue
        cascade_page.glossary['element_ids'] = {settings.LANGUAGE_CODE: element_ids}
        cascade_page.save()


def backwards(apps, schema_editor):
    CascadePage = apps.get_model('cmsplugin_cascade', 'CascadePage')

    for cascade_page in CascadePage.objects.all():
        try:
            element_ids = cascade_page.glossary.pop('element_ids')
        except:
            continue
        cascade_page.glossary['element_ids'] = element_ids[settings.LANGUAGE_CODE]
        cascade_page.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0029_json_field'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards),
    ]
