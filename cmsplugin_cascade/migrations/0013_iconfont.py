from django.db import migrations, models
import django.db.models.deletion
import filer.fields.file
import cmsplugin_cascade.models


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0006_auto_20160623_1627'),
        ('cmsplugin_cascade', '0012_auto_20160619_1854'),
    ]

    operations = [
        migrations.CreateModel(
            name='IconFont',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(help_text='A unique identifier to distinguish this icon font.', max_length=50, unique=True, verbose_name='Identifier')),
                ('config_data', models.JSONField()),
                ('font_folder', cmsplugin_cascade.models.FilePathField(allow_files=False, allow_folders=True)),
                ('zip_file', filer.fields.file.FilerFileField(help_text='Upload a zip file created on <a href="http://fontello.com/" target="_blank">Fontello</a> containing fonts.', on_delete=django.db.models.deletion.CASCADE, to='filer.File')),
            ],
            options={
                'verbose_name': 'Uploaded Icon Font',
                'verbose_name_plural': 'Uploaded Icon Fonts',
            },
        ),
    ]
