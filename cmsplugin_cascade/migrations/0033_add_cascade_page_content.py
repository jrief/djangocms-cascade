from django.contrib.contenttypes.models import ContentType
from django.db import migrations, models
import django.db.models.deletion

from entangled.utils import get_related_object


def forwards(apps, schema_editor):
    CascadeElement = apps.get_model('cmsplugin_cascade', 'CascadeElement')
    CascadePageContent = apps.get_model('cmsplugin_cascade', 'CascadePageContent')

    for cascade_element in CascadeElement.objects.all():
        if cascade_element.placeholder.content_type:
            if element_id := cascade_element.glossary.get('element_id'):
                page_content_type = ContentType.objects.get_for_id(cascade_element.placeholder.content_type.pk)
                page_content = page_content_type.get_object_for_this_type(pk=cascade_element.placeholder.object_id)
                try:
                    cascade_page_content = page_content.cascadepagecontent
                except models.ObjectDoesNotExist:
                    cascade_page_content = CascadePageContent.objects.create(extended_object_id=page_content.id)
                cascade_page_content.glossary.setdefault('element_ids', {})
                cascade_page_content.glossary['element_ids'][str(cascade_element.pk)] = element_id
                cascade_page_content.save()

    for cascade_element in CascadeElement.objects.all():
        if not (section := cascade_element.glossary.get('section')):
            continue
        if cascade_element.glossary.get('link_type') != 'cmspage':
            continue
        cms_page = get_related_object(cascade_element.glossary, 'cms_page')
        try:
            cascade_page = cms_page.cascadepage
        except models.ObjectDoesNotExist:
            continue
        element_ids = cascade_page.glossary.get('element_ids', {}).get(cascade_element.language, {})
        try:
            cascade_element.glossary['section'] = element_ids[section]
        except KeyError:
            pass
        else:
            cascade_element.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0035_auto_20230822_2208'),
        ('cmsplugin_cascade', '0032_alter_cascadeclipboard_id_alter_cascadepage_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CascadePageContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('glossary', models.JSONField(blank=True, default=dict, help_text='Store for arbitrary page data.')),
                ('extended_object', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='cms.pagecontent')),
                ('public_extension', models.OneToOneField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='draft_extension', to='cmsplugin_cascade.cascadepagecontent')),
            ],
            options={
                'verbose_name': 'Cascade Page Settings',
                'verbose_name_plural': 'Cascade Page Settings',
                'db_table': 'cmsplugin_cascade_pagecontent',
            },
        ),
        migrations.RunPython(forwards, reverse_code=migrations.RunPython.noop),
    ]
