from django.db import migrations, models
import django.db.models.deletion


def forwards(apps, schema_editor):
    print("Skipping this migration.")


def backwards(apps, schema_editor):
    print("Backward migration not implemented.")


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0019_verbose_table_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='cascadepage',
            name='icon_font',
            field=models.ForeignKey(blank=True, help_text='Set Icon Font globally for this page', null=True, on_delete=django.db.models.deletion.CASCADE, to='cmsplugin_cascade.IconFont', verbose_name='Icon Font'),
        ),
        migrations.RunPython(forwards, reverse_code=backwards),
    ]
