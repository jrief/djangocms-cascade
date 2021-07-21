from django.db import migrations, models
import django.db.models.deletion

from cmsplugin_cascade import app_settings

plugins_with_sharables = app_settings.CMSPLUGIN_CASCADE['plugins_with_sharables'].keys()
plugins_with_sharables = ','.join(["'{}'".format(p) for p in plugins_with_sharables])


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0015_auto_20160421_0000'),
        ('cmsplugin_cascade', '0010_refactor_heading'),
    ]

    operations = [
        migrations.AddField(
            model_name='cascadeelement',
            name='shared_glossary',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cmsplugin_cascade.SharedGlossary'),
        ),
        migrations.RunSQL(
            [("INSERT INTO cmsplugin_cascade_element (cmsplugin_ptr_id, glossary, shared_glossary_id) SELECT cmsplugin_ptr_id, glossary, shared_glossary_id FROM cmsplugin_cascade_sharableelement", None)],
            reverse_sql=[
                ("INSERT INTO cmsplugin_cascade_sharableelement (cmsplugin_ptr_id, glossary) SELECT cmsplugin_ptr_id, glossary FROM cmsplugin_cascade_element INNER JOIN cms_cmsplugin ON cmsplugin_ptr_id=cms_cmsplugin.id WHERE plugin_type IN ({})".format(plugins_with_sharables), None),
                ("DELETE FROM cmsplugin_cascade_element WHERE cmsplugin_ptr_id IN (SELECT cmsplugin_ptr_id FROM cmsplugin_cascade_sharableelement)", None)
            ]
        ),
        migrations.RemoveField(
            model_name='sharablecascadeelement',
            name='cmsplugin_ptr',
        ),
        migrations.RemoveField(
            model_name='sharablecascadeelement',
            name='shared_glossary',
        ),
        migrations.DeleteModel(
            name='SharableCascadeElement',
        ),
        migrations.CreateModel(
            name='SharableCascadeElement',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
    ]
