from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cmsplugin_cascade', '0027_version_1'),
    ]

    operations = [
        migrations.AddField(
            model_name='cascadeclipboard',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Created at'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cascadeclipboard',
            name='created_by',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created by'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cascadeclipboard',
            name='last_accessed_at',
            field=models.DateTimeField(default=None, editable=False, null=True, verbose_name='Last accessed at'),
        ),
    ]
