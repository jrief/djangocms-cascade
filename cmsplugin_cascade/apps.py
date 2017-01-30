# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig, apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db.models.signals import post_migrate
from django.utils.text import force_text
from django.utils.translation import ugettext_lazy as _


class CascadeConfig(AppConfig):
    name = 'cmsplugin_cascade'
    verbose_name = _("django CMS Cascade")
    default_permissions = ('add', 'change', 'delete')

    def ready(self):
        if 'cmsplugin_cascade.icon' in settings.INSTALLED_APPS:
            stylesSet = force_text(settings.CKEDITOR_SETTINGS.get('stylesSet'))
            if stylesSet != 'default:{}'.format(reverse('admin:cascade_texticon_wysiwig_config')):
                msg = "settings.CKEDITOR_SETTINGS['stylesSet'] should be `format_lazy('default:{}', reverse_lazy('admin:cascade_texticon_wysiwig_config'))`"
                raise ImproperlyConfigured(msg)

        post_migrate.connect(CascadeConfig.set_permissions, sender=self)

    @classmethod
    def set_permissions(cls, sender=None, **kwargs):
        from cmsplugin_cascade.plugin_base import fake_proxy_models

        ContentType = apps.get_model('contenttypes', 'ContentType')

        # iterate over fake_proxy_models and add contenttypes and permissions for missing proxy models
        proxy_model_names = []
        for model_name in fake_proxy_models.keys():
            proxy_model = sender.get_model(model_name)
            model_name = proxy_model._meta.model_name
            proxy_model_names.append(model_name)
            ctype, created = ContentType.objects.get_or_create(app_label=sender.label, model=model_name)
            if created:
                sender.grant_permissions(proxy_model)

        # iterate over contenttypes and remove those not in proxy models
        for ctype in ContentType.objects.filter(app_label=sender.label).exclude(model__in=proxy_model_names).all():
            model = ctype.model_class()
            if model is None:
                sender.revoke_permissions(ctype)
                ContentType.objects.get(app_label=sender.label, model=ctype).delete()

    def grant_permissions(self, proxy_model):
        """
        Create the default permissions for the just added proxy model
        """
        ContentType = apps.get_model('contenttypes', 'ContentType')
        try:
            Permission = apps.get_model('auth', 'Permission')
        except LookupError:
            return

        # searched_perms will hold the permissions we're looking for as (content_type, (codename, name))
        searched_perms = []
        ctype = ContentType.objects.get_for_model(proxy_model)
        for perm in self.default_permissions:
            searched_perms.append((
                '{0}_{1}'.format(perm, proxy_model._meta.model_name),
                "Can {0} {1}".format(perm, proxy_model._meta.verbose_name_raw)
            ))

        all_perms = set(Permission.objects.filter(
            content_type=ctype,
        ).values_list(
            'content_type', 'codename'
        ))
        permissions = [
            Permission(codename=codename, name=name, content_type=ctype)
            for codename, name in searched_perms if (ctype.pk, codename) not in all_perms
        ]
        Permission.objects.bulk_create(permissions)

    def revoke_permissions(self, ctype):
        """
        Remove all permissions for the content type to be removed
        """
        ContentType = apps.get_model('contenttypes', 'ContentType')
        try:
            Permission = apps.get_model('auth', 'Permission')
        except LookupError:
            return

        codenames = ['{0}_{1}'.format(perm, ctype) for perm in self.default_permissions]
        cascade_element = apps.get_model(self.label, 'cascadeelement')
        element_ctype = ContentType.objects.get_for_model(cascade_element)
        Permission.objects.filter(content_type=element_ctype, codename__in=codenames).delete()
