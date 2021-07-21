from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
        ('cmsplugin_cascade', '0008_sortableinlinecascadeelement'),
    ]

    operations = [
        migrations.CreateModel(
            name='CascadePage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('settings', models.JSONField(blank=True, default={}, help_text='User editable settings for this page.')),
                ('glossary', models.JSONField(blank=True, default={}, help_text='Store for arbitrary page data.')),
                ('extended_object', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='cms.Page')),
                ('public_extension', models.OneToOneField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='draft_extension', to='cmsplugin_cascade.CascadePage')),
            ],
            options={
                'db_table': 'cmsplugin_cascade_page',
                'verbose_name': 'Cascade Page Settings',
                'verbose_name_plural': 'Cascade Page Settings',
            },
        ),
    ]
