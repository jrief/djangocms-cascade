# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from cmsplugin_cascade.models import CascadeModelBase
from cmsplugin_cascade.plugin_base import fake_proxy_models
from django.db import migrations
from django.utils.decorators import classproperty


class Migration(migrations.Migration):
    """
    This migration is a noop. It pretends that the proxy models created by Cascade do already
    exists, so that ``./manage.py makemigrations`` does not create any migration file for you.
    """

    dependencies = [
        ('cmsplugin_cascade', '0016_shared_glossary_uneditable'),
    ]

    @classproperty
    def operations(self):
        for name, bases in sorted(fake_proxy_models.items()):
            bases = tuple(
                b._meta.app_label + '.' + b._meta.model_name if issubclass(b, CascadeModelBase) else b
                for b in bases
            )
            yield migrations.CreateModel(
                name=name,
                fields=[],
                options={'proxy': True},
                bases=bases,
            )
