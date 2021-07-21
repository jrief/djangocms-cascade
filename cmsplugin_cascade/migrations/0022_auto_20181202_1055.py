from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0021_cascadepage_verbose_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cascadepage',
            name='icon_font',
            field=models.ForeignKey(blank=True, help_text='Set Icon Font globally for this page', null=True, on_delete=django.db.models.deletion.SET_NULL, to='cmsplugin_cascade.IconFont', verbose_name='Icon Font'),
        ),
    ]
