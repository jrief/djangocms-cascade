# Generated by Django 2.2.11 on 2020-03-10 12:27

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import migrations, models
import django.db.models.deletion
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
        migrations.CreateModel(
            name='CascadeClipboardGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='cascadeclipboard',
            name='group',
            field=models.ManyToManyField(blank=True, to='cmsplugin_cascade.CascadeClipboardGroup'),
        ),
    ]
