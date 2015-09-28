# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cmsplugin_cascade.link.plugin_base
import cmsplugin_cascade.segmentation.mixins
import shop.cascade.plugin_base


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_cascade', '0003_inlinecascadeelement'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PanelGroupPluginModel',
        ),
        migrations.DeleteModel(
            name='PanelPluginModel',
        ),
        migrations.CreateModel(
            name='AcceptConditionFormPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='BillingAddressFormPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='BootstrapAccordionPanelPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='BootstrapAccordionPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='BootstrapPanelPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='BootstrapSecondaryMenuPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='CatalogLinkPluginBaseModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='CheckoutAddressPluginBaseModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='CustomerFormPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='DialogFormPluginBaseModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ExtraAnnotationFormPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='GuestFormPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='PaymentMethodFormPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ProcessBarPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ProcessNextStepPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=(cmsplugin_cascade.link.plugin_base.LinkElementMixin, 'cmsplugin_cascade.cascadeelement'),
        ),
        migrations.CreateModel(
            name='ProcessStepPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='SegmentPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=(cmsplugin_cascade.segmentation.mixins.SegmentPluginModelMixin, 'cmsplugin_cascade.cascadeelement'),
        ),
        migrations.CreateModel(
            name='ShippingAddressFormPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ShippingMethodFormPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ShopAuthenticationPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=(shop.cascade.plugin_base.ShopLinkElementMixin, 'cmsplugin_cascade.cascadeelement'),
        ),
        migrations.CreateModel(
            name='ShopButtonPluginBaseModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ShopCartPluginModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ShopLinkPluginBaseModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ShopPluginBaseModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cmsplugin_cascade.cascadeelement',),
        ),
        migrations.CreateModel(
            name='ShopProceedButtonModel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=(cmsplugin_cascade.link.plugin_base.LinkElementMixin, 'cmsplugin_cascade.cascadeelement'),
        ),
    ]
