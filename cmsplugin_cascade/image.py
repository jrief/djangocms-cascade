# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import apps
from django.contrib.admin.sites import site
from django.core.exceptions import ObjectDoesNotExist
from django.forms import widgets
from django.db.models.fields.related import ManyToOneRel
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from filer.fields.image import AdminFileWidget, FilerImageField
from filer.models.imagemodels import Image

from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import CascadePluginMixinBase


class ImageFormMixin(object):
    def __init__(self, *args, **kwargs):
        super(ImageFormMixin, self).__init__(*args, **kwargs)
        try:
            self.fields['image_file'].initial = kwargs['instance'].image.pk
        except (AttributeError, KeyError):
            pass
        self.fields['image_file'].widget = AdminFileWidget(ManyToOneRel(FilerImageField, Image, 'file_ptr'), site)

    def clean_glossary(self):
        assert isinstance(self.cleaned_data['glossary'], dict), "Expected `glossary` to be a dict."
        return self.cleaned_data['glossary']

    def clean(self):
        cleaned_data = super(ImageFormMixin, self).clean()
        if self.is_valid() and cleaned_data['image_file']:
            width = cleaned_data['image_file']._width
            height = cleaned_data['image_file']._height
            exif_orientation = cleaned_data['image_file'].exif.get('Orientation', 1)
            image_data = {'pk': cleaned_data['image_file'].pk, 'model': 'filer.Image',
               'width': width ,  'height': height , 'exif_orientation' :exif_orientation }
            cleaned_data['glossary'].update(image=image_data)
        self.cleaned_data.pop('image_file', None)
        return cleaned_data


@python_2_unicode_compatible
class ImagePropertyMixin(object):
    """
    A mixin class to convert a CascadeElement into a proxy model for rendering an image element.
    """
    def __str__(self):
        try:
            return self.plugin_class.get_identifier(self)
        except AttributeError:
            return str(self.image)

    @property
    def image(self):
        if not hasattr(self, '_image_model'):
            try:
                Model = apps.get_model(*self.glossary['image']['model'].split('.'))
                self._image_model = Model.objects.get(pk=self.glossary['image']['pk'])
            except (KeyError, ObjectDoesNotExist):
                self._image_model = None
        return self._image_model

    def post_copy(self, old_instance, new_old_ziplist):
        # by saving this model after the full tree has been copied, ``BootstrapImagePlugin.sanitize_model()``
        # is invoked a second time with the now complete information of all column siblings.
        self.save(sanitize_only=True)


class ImageAnnotationMixin(CascadePluginMixinBase):
    """
    This mixin class prepends the glossary fields 'image_title' and 'alt_tag' in front of the
    glossary fields provided by the class LinkPluginBase.
    """
    image_title = GlossaryField(
        widgets.TextInput(),
        label=_('Image Title'),
        help_text=_("Caption text added to the 'title' attribute of the <img> element."),
    )

    alt_tag = GlossaryField(
        widgets.TextInput(),
        label=_('Alternative Description'),
        help_text=_("Textual description of the image added to the 'alt' tag of the <img> element."),
    )
