# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from cmsplugin_cascade.models import CascadeElement


def forwards(apps, schema_editor):
    for cascade_element in CascadeElement.objects.all():
        if cascade_element.plugin_type != 'FramedIconPlugin':
            continue

        color = cascade_element.glossary.get('color')
        if isinstance(color, str):
            cascade_element.glossary['color'] = ('', color)
            cascade_element.save()
        shared = cascade_element.shared_glossary
        if shared:
            color = shared.glossary.get('color')
            if isinstance(color, str):
                shared.glossary['color'] = ('', color)
                shared.save()


def backwards(apps, schema_editor):
    for cascade_element in CascadeElement.objects.all():
        if cascade_element.plugin_type != 'FramedIconPlugin':
            continue

        color = cascade_element.glossary.get('color')
        if isinstance(color, (list, tuple)):
            cascade_element.glossary['color'] = color[1]
            cascade_element.save()
        shared = cascade_element.shared_glossary
        if shared:
            color = shared.glossary.get('color')
            if isinstance(color, (list, tuple)):
                shared.glossary['color'] = color[1]
                shared.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0017_fake_proxy_models'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards),
    ]
