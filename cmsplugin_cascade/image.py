from django.core.exceptions import ValidationError
from django.forms.fields import CharField
from django.utils.translation import ugettext_lazy as _
from entangled.forms import EntangledModelFormMixin, EntangledField, get_related_object
from cmsplugin_cascade.fields import CascadeImageField


class ImageFormMixin(EntangledModelFormMixin):
    image_file = CascadeImageField()

    image_title = CharField(
        label=_('Image Title'),
        required=False,
        help_text=_("Caption text added to the 'title' attribute of the <img> element."),
    )

    alt_tag = CharField(
        label=_('Alternative Description'),
        required=False,
        help_text=_("Textual description of the image added to the 'alt' tag of the <img> element."),
    )

    image_properties = EntangledField()

    class Meta:
        entangled_fields = {'glossary': ['image_file', 'image_title', 'alt_tag', 'image_properties']}

    def clean(self):
        cleaned_data = super().clean()
        image_file = cleaned_data.get('image_file')
        if not image_file:
            raise ValidationError(_("No image has been selected."))
        # _image_properties are just a cached representation, maybe useless
        cleaned_data['image_properties'] = {
            'width': image_file._width,
            'height': image_file._height,
            'exif_orientation': image_file.exif.get('Orientation', 1),
        }
        return cleaned_data


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
        if not hasattr(self, '_image_file'):
            self._image_file = get_related_object(self.glossary, 'image_file')
        return self._image_file

    def post_copy(self, old_instance, new_old_ziplist):
        # by saving this model after the full tree has been copied, ``<Any>ImagePlugin.sanitize_model()``
        # is invoked a second time with the now complete information of all column siblings.
        self.save(sanitize_only=True)
