import json
import os
import shutil
from collections import OrderedDict
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from jsonfield.fields import JSONField
from filer.fields.file import FilerFileField
from cms.extensions import PageExtension
from cms.extensions.extension_pool import extension_pool
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.models_base import CascadeModelBase
from cmsplugin_cascade import app_settings


class SharedGlossary(models.Model):
    """
    A model class to hold glossary data shared among different plugins.
    """
    plugin_type = models.CharField(
        _("Plugin Name"),
        max_length=50,
        db_index=True,
        editable=False,
    )

    identifier = models.CharField(
        _("Identifier"),
        max_length=50,
        unique=True,
    )

    glossary = JSONField(
        null=True,
        blank=True,
        default={},
    )

    class Meta:
        unique_together = ['plugin_type', 'identifier']
        verbose_name_plural = verbose_name = _("Shared between Plugins")

    def __str__(self):
        return self.identifier

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        Only entries which are declared as sharable, shall be stored in the sharable glossary.
        """
        plugin_instance = plugin_pool.get_plugin(self.plugin_type)
        glossary = dict((key, value) for key, value in self.glossary.items()
                        if key in plugin_instance.sharable_fields)
        self.glossary = glossary
        super().save(force_insert, force_update, using, update_fields)


class CascadeElement(CascadeModelBase):
    """
    The concrete model class to store arbitrary data for plugins derived from CascadePluginBase.
    """
    shared_glossary = models.ForeignKey(
        SharedGlossary,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        db_table = 'cmsplugin_cascade_element'
        verbose_name = _("Element")
        verbose_name_plural = _("Elements")

    def copy_relations(self, oldinstance):
        def init_element(inline_element):
            inline_element.pk = None
            inline_element.cascade_element = self
            inline_element.save()

        for inline_element in oldinstance.inline_elements.all():
            init_element(inline_element)
        for sortinline_element in oldinstance.sortinline_elements.all():
            init_element(sortinline_element)


class SharableCascadeElement(CascadeElement):
    """
    A proxy model which takes care of merging the glossary with its shared instance.
    """
    class Meta:
        proxy = True

    def __getattribute__(self, name):
        """
        Update glossary with content from SharedGlossary model if that exists.
        """
        attribute = object.__getattribute__(self, name)
        if name == 'glossary' and self.shared_glossary:
            attribute.update(self.shared_glossary.glossary)
        return attribute


class InlineCascadeElement(models.Model):
    cascade_element = models.ForeignKey(
        CascadeElement,
        related_name='inline_elements',
        on_delete=models.CASCADE,
    )

    glossary = JSONField(
        blank=True,
        default={},
    )

    class Meta:
        db_table = 'cmsplugin_cascade_inline'


class SortableInlineCascadeElement(models.Model):
    cascade_element = models.ForeignKey(
        CascadeElement,
        related_name='sortinline_elements',
        on_delete=models.CASCADE,
    )

    glossary = JSONField(
        blank=True,
        default={},
    )

    order = models.PositiveIntegerField(
        verbose_name=_("Sort by"),
        db_index=True,
    )

    class Meta:
        db_table = 'cmsplugin_cascade_sortinline'
        ordering = ['order']

    def __str__(self):
        return ""


class PluginExtraFields(models.Model):
    """
    Store a set of allowed extra CSS classes and inline styles to be used for Cascade plugins
    inheriting from `ExtraFieldsMixin`. Also store if individual ``id=""`` tags are allowed.
    """
    plugin_type = models.CharField(
        _("Plugin Name"),
        max_length=50,
        db_index=True,
    )

    site = models.ForeignKey(
        Site,
        verbose_name=_("Site"),
        on_delete=models.CASCADE,
    )

    allow_id_tag = models.BooleanField(default=False)

    css_classes = JSONField(
        null=True,
        blank=True,
        default={},
    )

    inline_styles = JSONField(
        null=True,
        blank=True,
        default={},
    )

    class Meta:
        verbose_name = verbose_name_plural = _("Custom CSS classes and styles")
        unique_together = ['plugin_type', 'site']

    def __str__(self):
        return str(self.name)

    @cached_property
    def name(self):
        return plugin_pool.get_plugin(self.plugin_type).name


class TextEditorConfigFields(models.Model):
    ELEMENT_CHOICES = [(c, c) for c in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'address', 'div', 'span']]

    name = models.CharField(
        _("Name"),
        max_length=50,
    )

    element_type = models.CharField(
        _("Element Type"),
        choices=ELEMENT_CHOICES,
        max_length=12,
    )

    css_classes = models.CharField(
        _("CSS classes"),
        max_length=250,
        help_text=_("Freely selectable CSS classnames for this Text-Editor Style, separated by spaces."),
    )

    class Meta:
        verbose_name = _("Text Editor Config")

    def get_config(self):
        config = {
            'name': self.name,
            'element': self.element_type,
            'attributes': {'class': self.css_classes},
        }
        return json.dumps(config)


class Segmentation(models.Model):
    class Meta:
        verbose_name = _("Segmentation")
        managed = False  # it's a dummy model
        db_table = None


class CascadeClipboard(models.Model):
    """
    A model class to persist, export and re-import the clipboard's content.
    """
    identifier = models.CharField(
        _("Identifier"),
        max_length=50,
        unique=True,
    )

    data = JSONField(
        null=True,
        blank=True,
        default={},
    )

    created_by = models.ForeignKey(
        get_user_model(),
        verbose_name=_("Created by"),
        on_delete=models.SET_NULL,
        editable=False,
        null=True,
    )

    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
        editable=False,
    )

    last_accessed_at = models.DateTimeField(
        _("Last accessed at"),
        null=True,
        default=None,
        editable=False,
    )

    class Meta:
        verbose_name = _("Persisted Clipboard Content")
        verbose_name_plural = _("Persisted Clipboard Contents")

    def __str__(self):
        return self.identifier


class FilePathField(models.FilePathField):
    """
    Implementation of `models.FilePathField` which configures the `path` argument by default
    to avoid the creation of a migration file for each change in local settings.
    """
    def __init__(self, **kwargs):
        kwargs.setdefault('path', app_settings.CMSPLUGIN_CASCADE['icon_font_root'])
        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['path']
        return name, path, args, kwargs


class IconFont(models.Model):
    """
    Instances of uploaded icon fonts, such as FontAwesone, MaterialIcons, etc.
    """
    identifier = models.CharField(
        _("Identifier"),
        max_length=50,
        unique=True,
        help_text=_("A unique identifier to distinguish this icon font."),
    )

    config_data = JSONField()

    zip_file = FilerFileField(
        on_delete=models.CASCADE,
        help_text=_('Upload a zip file created on <a href="http://fontello.com/" target="_blank">Fontello</a> containing fonts.')
    )

    font_folder = FilePathField(allow_files=False, allow_folders=True)

    is_default = models.BooleanField(
        _("Default Font"),
        default=False,
        help_text=_("Use this font as default, unless an icon font is set for the current page."),
    )

    class Meta:
        verbose_name = _("Uploaded Icon Font")
        verbose_name_plural = _("Uploaded Icon Fonts")

    def __str__(self):
        return self.identifier

    def get_icon_families(self):
        """
        Return an ordered dict of css classes required to render these icons
        """
        families = OrderedDict()
        for glyph in self.config_data['glyphs']:
            src = glyph.pop('src', 'default')
            families.setdefault(src, [])
            css = glyph.get('css')
            if css:
                families[src].append(css)
        return families

    def get_stylesheet_url(self):
        icon_font_url = os.path.relpath(app_settings.CMSPLUGIN_CASCADE['icon_font_root'], settings.MEDIA_ROOT)
        name = self.config_data.get('name') or 'fontello'
        parts = (icon_font_url, self.font_folder, 'css/{}.css'.format(name))
        return urljoin(settings.MEDIA_URL, '/'.join(parts))

    def config_data_as_json(self):
        data = dict(self.config_data)
        data.pop('glyphs', None)
        data['families'] = self.get_icon_families()
        return json.dumps(data)

    @classmethod
    def delete_icon_font(cls, instance=None, **kwargs):
        if isinstance(instance, cls):
            font_folder = os.path.join(app_settings.CMSPLUGIN_CASCADE['icon_font_root'], instance.font_folder)
            shutil.rmtree(font_folder, ignore_errors=True)
            try:
                temp_folder = os.path.abspath(os.path.join(font_folder, os.path.pardir))
                os.rmdir(temp_folder)
            except FileNotFoundError:
                pass

models.signals.pre_delete.connect(IconFont.delete_icon_font, dispatch_uid='delete_icon_font')


class CascadePage(PageExtension):
    """
    Keep arbitrary data tightly coupled to the CMS page.
    """
    settings = JSONField(
        blank=True,
        default={},
        help_text=_("User editable settings for this page."),
    )

    glossary = JSONField(
        blank=True,
        default={},
        help_text=_("Store for arbitrary page data."),
    )

    icon_font = models.ForeignKey(
        IconFont,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Icon Font"),
    )

    menu_symbol = models.CharField(
        _("Menu Symbol"),
        blank=True,
        null=True,
        max_length=32,
        help_text=_("Symbol to be used with the menu title for this page."),
    )

    class Meta:
        db_table = 'cmsplugin_cascade_page'
        verbose_name = verbose_name_plural = _("Cascade Page Settings")

    def __str__(self):
        return self.get_page().get_title()

    @classmethod
    def assure_relation(cls, cms_page):
        """
        Assure that we have a foreign key relation, pointing from CascadePage onto CMSPage.
        """
        try:
            cms_page.cascadepage
        except cls.DoesNotExist:
            cls.objects.create(extended_object=cms_page)

    @classmethod
    def delete_cascade_element(cls, instance=None, **kwargs):
        if isinstance(instance, CascadeModelBase):
            try:
                instance.placeholder.page.cascadepage.glossary['element_ids'].pop(str(instance.pk))
                instance.placeholder.page.cascadepage.save()
            except (AttributeError, KeyError):
                pass

extension_pool.register(CascadePage)
models.signals.pre_delete.connect(CascadePage.delete_cascade_element, dispatch_uid='delete_cascade_element')
