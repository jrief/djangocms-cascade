# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os, shutil
from collections import OrderedDict
from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.functional import cached_property
from django.utils.six.moves.urllib.parse import urljoin
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from jsonfield.fields import JSONField
from filer.fields.file import FilerFileField
from cms.extensions import PageExtension
from cms.extensions.extension_pool import extension_pool
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.models_base import CascadeModelBase
from cmsplugin_cascade.settings import CMSPLUGIN_CASCADE


@python_2_unicode_compatible
class SharedGlossary(models.Model):
    """
    A model class to hold glossary data shared among different plugins.
    """
    plugin_type = models.CharField(_("Plugin Name"), max_length=50, db_index=True, editable=False)
    identifier = models.CharField(_("Identifier"), max_length=50, unique=True)
    glossary = JSONField(null=True, blank=True, default={})

    class Meta:
        unique_together = ('plugin_type', 'identifier')
        verbose_name_plural = verbose_name = _("Shared between Plugins")

    def __str__(self):
        return self.identifier


class CascadeElement(CascadeModelBase):
    """
    The concrete model class to store arbitrary data for plugins derived from CascadePluginBase.
    """
    shared_glossary = models.ForeignKey(SharedGlossary, blank=True, null=True, on_delete=models.SET_NULL, editable=False)

    class Meta:
        db_table = 'cmsplugin_cascade_element'

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

    def get_data_representation(self):
        # TODO: merge with shared_glossary
        return {'glossary': self.glossary}


class InlineCascadeElement(models.Model):
    cascade_element = models.ForeignKey(CascadeElement, related_name='inline_elements')
    glossary = JSONField(blank=True, default={})

    class Meta:
        db_table = 'cmsplugin_cascade_inline'


class SortableInlineCascadeElement(models.Model):
    cascade_element = models.ForeignKey(CascadeElement, related_name='sortinline_elements')
    glossary = JSONField(blank=True, default={})
    order = models.PositiveIntegerField(verbose_name=_("Sort by"), db_index=True)

    class Meta:
        db_table = 'cmsplugin_cascade_sortinline'
        ordering = ('order',)

    def __str__(self):
        return ""


@python_2_unicode_compatible
class PluginExtraFields(models.Model):
    """
    Store a set of allowed extra CSS classes and inline styles to be used for Cascade plugins
    inheriting from `ExtraFieldsMixin`. Also store if individual ``id=""`` tags are allowed.
    """
    plugin_type = models.CharField(_("Plugin Name"), max_length=50, db_index=True)
    site = models.ForeignKey(Site, verbose_name=_("Site"))
    allow_id_tag = models.BooleanField(default=False)
    css_classes = JSONField(null=True, blank=True, default={})
    inline_styles = JSONField(null=True, blank=True, default={})

    class Meta:
        verbose_name = verbose_name_plural = _("Custom CSS classes and styles")
        unique_together = ('plugin_type', 'site')

    def __str__(self):
        return force_text(self.name)

    @cached_property
    def name(self):
        return plugin_pool.get_plugin(self.plugin_type).name


class Segmentation(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = _("Segmentation")
        managed = False  # it's a dummy model
        db_table = None


@python_2_unicode_compatible
class CascadeClipboard(models.Model):
    """
    A model class to persist, export and re-import the clipboard's content.
    """
    identifier = models.CharField(_("Identifier"), max_length=50, unique=True)
    data = JSONField(null=True, blank=True, default={})

    class Meta:
        verbose_name_plural = verbose_name = _("Persited Clipboard Content")

    def __str__(self):
        return self.identifier


class CascadePage(PageExtension):
    """
    Keep arbitrary data tightly coupled to the CMS page.
    """
    settings = JSONField(blank=True, default={}, help_text=_("User editable settings for this page."))
    glossary = JSONField(blank=True, default={}, help_text=_("Store for arbitrary page data."))

    class Meta:
        db_table = 'cmsplugin_cascade_page'
        verbose_name = verbose_name_plural = _("Cascade Page Settings")

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
                instance.page.cascadepage.glossary['element_ids'].pop(str(instance.pk))
                instance.page.cascadepage.save()
            except (AttributeError, KeyError):
                pass

extension_pool.register(CascadePage)
models.signals.pre_delete.connect(CascadePage.delete_cascade_element, dispatch_uid='delete_cascade_element')


@python_2_unicode_compatible
class IconFont(models.Model):
    """
    Instances of uploaded icon fonts, such as FontAwesone, MaterialIcons, etc.
    """
    identifier = models.CharField(_("Identifier"), max_length=50, unique=True)
    config_data = JSONField()
    zip_file = FilerFileField()
    font_folder = models.FilePathField(path=CMSPLUGIN_CASCADE['icon_font_root'],
                                       allow_files=False, allow_folders=True)

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
        icon_font_url = os.path.relpath(CMSPLUGIN_CASCADE['icon_font_root'], settings.MEDIA_ROOT)
        parts = (icon_font_url, self.font_folder, 'css', 'fontello.css')
        return urljoin(settings.MEDIA_URL, '/'.join(parts))

    @classmethod
    def delete_icon_font(cls, instance=None, **kwargs):
        if isinstance(instance, cls):
            font_folder = os.path.join(CMSPLUGIN_CASCADE['icon_font_root'], instance.font_folder)
            shutil.rmtree(font_folder, ignore_errors=True)
            temp_folder = os.path.abspath(os.path.join(font_folder, os.path.pardir))
            os.rmdir(temp_folder)

models.signals.pre_delete.connect(IconFont.delete_icon_font, dispatch_uid='delete_icon_font')
