from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0020_page_icon_font'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cascadepage',
            options={'verbose_name': 'Cascade Page Settings', 'verbose_name_plural': 'Cascade Page Settings'},
        ),
    ]
