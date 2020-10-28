from django.apps import AppConfig, apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import pre_migrate, post_migrate
from django.db.utils import DatabaseError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class CascadeConfig(AppConfig):
    name = 'cmsplugin_cascade'
    verbose_name = _("django CMS Cascade")
    default_permissions = ('add', 'change', 'delete')

    def ready(self):
        if 'django_select2' not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured('django_select2 not configured')

        stylesSet = str(settings.CKEDITOR_SETTINGS.get('stylesSet'))
        if stylesSet != 'default:{}'.format(reverse('admin:cascade_texteditor_config')):
            msg = "settings.CKEDITOR_SETTINGS['stylesSet'] should be `format_lazy('default:{}', reverse_lazy('admin:cascade_texteditor_config'))`"
            raise ImproperlyConfigured(msg)

        pre_migrate.connect(self.__class__.pre_migrate, sender=self)
        post_migrate.connect(self.__class__.post_migrate, sender=self)

    @classmethod
    def pre_migrate(cls, sender=None, **kwargs):
        """
        Iterate over contenttypes and remove those not in proxy models
        """
        ContentType = apps.get_model('contenttypes', 'ContentType')
        try:
            queryset = ContentType.objects.filter(app_label=sender.label)
            for ctype in queryset.exclude(model__in=sender.get_proxy_models().keys()):
                model = ctype.model_class()
                if model is None:
                    sender.revoke_permissions(ctype)
                    ContentType.objects.get(app_label=sender.label, model=ctype).delete()
        except DatabaseError:
            return

    @classmethod
    def post_migrate(cls, sender=None, **kwargs):
        """
        Iterate over fake_proxy_models and add contenttypes and permissions for missing proxy
        models, if this has not been done by Django yet
        """
        ContentType = apps.get_model('contenttypes', 'ContentType')

        for model_name, proxy_model in sender.get_proxy_models().items():
            ctype, created = ContentType.objects.get_or_create(app_label=sender.label, model=model_name)
            if created:
                sender.grant_permissions(proxy_model)

    def get_proxy_models(self):
        from cmsplugin_cascade.plugin_base import fake_proxy_models

        proxy_models = {}
        for model_name in fake_proxy_models.keys():
            proxy_model = self.get_model(model_name)
            model_name = proxy_model._meta.model_name  # the model_name in lowercase normally
            proxy_models[model_name] = proxy_model
        return proxy_models

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
