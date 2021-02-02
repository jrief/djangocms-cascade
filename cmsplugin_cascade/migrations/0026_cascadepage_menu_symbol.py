from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0025_texteditorconfigfields'),
    ]

    operations = [
        migrations.AddField(
            model_name='cascadepage',
            name='menu_symbol',
            field=models.CharField(blank=True, help_text='Symbol to be used with the menu title for this page.', max_length=32, null=True, verbose_name='Menu Symbol'),
        ),
        migrations.AlterField(
            model_name='cascadepage',
            name='icon_font',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cmsplugin_cascade.IconFont', verbose_name='Icon Font'),
        ),
    ]
