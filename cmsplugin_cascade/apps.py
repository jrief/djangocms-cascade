# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig, apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_migrate, post_migrate
from django.db.utils import DatabaseError
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

        pre_migrate.connect(self.__class__.pre_migrate, sender=self)
        post_migrate.connect(self.__class__.post_migrate, sender=self)
        self.monkeypatch_django_cms()

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

    def monkeypatch_django_cms(self):
        """
        This monkey patch can be removed when https://github.com/divio/django-cms/pull/5809
        has been merged
        """
        import warnings
        import functools

        from django.utils.safestring import mark_safe

        from cms.plugin_base import CMSPluginBase
        from cms.plugin_rendering import ContentRenderer
        from cms.toolbar.utils import get_placeholder_toolbar_js, get_plugin_toolbar_js
        from cms.templatetags.cms_js_tags import register

        def get_child_classes(cls, slot, page, instance=None):
            """Check :method:`cms.plugin_base.CMSPluginBase.get_child_classes` for details"""
            child_classes = cls.get_child_class_overrides(slot, page)
            if child_classes:
                return child_classes

            installed_plugins = cls.get_child_plugin_candidates(slot, page)

            child_classes = []
            plugin_type = cls.__name__
            for plugin_class in installed_plugins:
                allowed_parents = plugin_class.get_parent_classes(slot, page, instance)
                if not allowed_parents or plugin_type in allowed_parents:
                    child_classes.append(plugin_class.__name__)

            return child_classes

        def get_parent_classes(cls, slot, page, instance=None):
            """Check :method:`cms.plugin_base.CMSPluginBase.get_parent_classes` for details"""
            from cms.utils.placeholder import get_placeholder_conf

            template = page and page.get_template() or None

            # config overrides..
            ph_conf = get_placeholder_conf('parent_classes', slot, template, default={})
            parent_classes = ph_conf.get(cls.__name__, cls.parent_classes)
            return parent_classes

        def render_editable_plugin(self, instance, context, plugin_class,
                                   placeholder=None, content=''):
            if not placeholder:
                placeholder = instance.placeholder

            # this is fine. I'm fine.
            output = ('<template class="cms-plugin '
                      'cms-plugin-start cms-plugin-%(pk)s"></template>%(content)s'
                      '<template class="cms-plugin cms-plugin-end cms-plugin-%(pk)s"></template>')
            try:
                # Compatibility with CMS < 3.4
                template = self.get_cached_template(plugin_class.frontend_edit_template)
            except AttributeError:
                content = output % {'pk': instance.pk, 'content': content}
            else:
                warnings.warn(
                    "Attribute `frontend_edit_template` will be removed in django CMS 3.5",
                    PendingDeprecationWarning
                )
                content = template.render(context)

            plugin_type = instance.plugin_type
            placeholder_cache = self._rendered_plugins_by_placeholder.setdefault(placeholder.pk, {})

            parents_cache = placeholder_cache.setdefault('plugin_parents', {})
            children_cache = placeholder_cache.setdefault('plugin_children', {})

            if plugin_class.cache_parent_classes and plugin_type not in parents_cache:
                parent_classes = plugin_class.get_parent_classes(
                    slot=placeholder.slot,
                    page=self.current_page,
                    instance=instance,
                )
                parents_cache[plugin_type] = parent_classes or []

            if plugin_class.cache_child_classes and plugin_type not in children_cache:
                child_classes = plugin_class.get_child_classes(
                    slot=placeholder.slot,
                    page=self.current_page,
                    instance=instance,
                )
                children_cache[plugin_type] = child_classes or []
            return content

        CMSPluginBase.cache_child_classes = True
        CMSPluginBase.cache_parent_classes = True
        CMSPluginBase.get_child_classes = classmethod(get_child_classes)
        CMSPluginBase.get_parent_classes = classmethod(get_parent_classes)
        ContentRenderer.render_editable_plugin = render_editable_plugin

        @register.simple_tag(takes_context=False)
        def render_placeholder_toolbar_js(placeholder, render_language, content_renderer):
            page = placeholder.page
            slot = placeholder.slot
            placeholder_cache = content_renderer.get_rendered_plugins_cache(placeholder)
            rendered_plugins = placeholder_cache['plugins']
            plugin_parents = placeholder_cache['plugin_parents']
            plugin_children = placeholder_cache['plugin_children']
            plugin_pool = content_renderer.plugin_pool
            plugin_types = [cls.__name__ for cls in plugin_pool.get_all_plugins(slot, page)]
            allowed_plugins = plugin_types + plugin_pool.get_system_plugins()

            get_toolbar_js = functools.partial(
                get_plugin_toolbar_js,
                request_language=content_renderer.request_language,
            )

            def _render_plugin_js(plugin):
                try:
                    child_classes = plugin_children[plugin.plugin_type]
                except KeyError:
                    child_classes = plugin.get_plugin_class().get_child_classes(slot=slot,
                                                                                page=page,
                                                                                instance=plugin)

                try:
                    parent_classes = plugin_parents[plugin.plugin_type]
                except KeyError:
                    parent_classes = plugin.get_plugin_class().get_parent_classes(slot=slot,
                                                                                  page=page,
                                                                                  instance=plugin)

                content = get_toolbar_js(
                    plugin,
                    children=child_classes,
                    parents=parent_classes,
                )
                return content

            plugin_js_output = ''.join(_render_plugin_js(plugin) for plugin in rendered_plugins)
            placeholder_js_output = get_placeholder_toolbar_js(
                placeholder=placeholder,
                request_language=content_renderer.request_language,
                render_language=render_language,
                allowed_plugins=allowed_plugins,
            )
            return mark_safe(plugin_js_output + '\n' + placeholder_js_output)
