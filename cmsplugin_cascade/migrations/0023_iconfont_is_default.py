from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0022_auto_20181202_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='iconfont',
            name='is_default',
            field=models.BooleanField(default=False, help_text='Use this font as default, unless an icon font is set for the current page.', verbose_name='Default Font'),
        ),
    ]
