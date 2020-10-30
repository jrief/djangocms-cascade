from django.core.exceptions import ValidationError
from django.forms.fields import MultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple, MediaDefiningClass
from django.utils.translation import gettext_lazy as _

from entangled.forms import EntangledModelFormMixin


def remove_duplicates(lst):
    """
    Emulate what a Python ``set()`` does, but keeping the element's order.
    """
    dset = set()
    return [l for l in lst if l not in dset and not dset.add(l)]


def rectify_partial_form_field(base_field, partial_form_fields):
    """
    In base_field reset the attributes label and help_text, since they are overriden by the
    partial field. Additionally, from the list, or list of lists of partial_form_fields
    append the bound validator methods to the given base field.
    """
    base_field.label = ''
    base_field.help_text = ''
    for fieldset in partial_form_fields:
        if not isinstance(fieldset, (list, tuple)):
            fieldset = [fieldset]
        for field in fieldset:
            base_field.validators.append(field.run_validators)

def validate_link(link_data):
    """
    Check if the given model exists, otherwise raise a Validation error
    """
    from django.apps import apps

    try:
        Model = apps.get_model(link_data['model'])
        Model.objects.get(pk=link_data['pk'])
    except Model.DoesNotExist:
        raise ValidationError(_("Unable to link onto '{0}'.").format(Model.__name__))


def compute_aspect_ratio(image):
    if image.exif.get('Orientation', 1) > 4:
        # image is rotated by 90 degrees, while keeping width and height
        return float(image.width) / float(image.height)
    else:
        return float(image.height) / float(image.width)


def compute_aspect_ratio_with_glossary(glossary):
    if glossary['image']['exif_orientation'] > 4:
        # image is rotated by 90 degrees, while keeping width and height
        return float(glossary['image']['width']) / float(glossary['image']['height'])
    else:
        return float(glossary['image']['height']) / float(glossary['image']['width'])


def get_image_size(width, image_height, aspect_ratio):
    if image_height[0]:
        # height was given in px
        return (width, image_height[0])
    elif image_height[1]:
        # height was given in %
        return (width, int(round(width * image_height[1])))
    else:
        # as fallback, adopt height to current width
        return (width, int(round(width * aspect_ratio)))


def parse_responsive_length(responsive_length):
    """
    Takes a string containing a length definition in pixels or percent and parses it to obtain
    a computational length. It returns a tuple where the first element is the length in pixels and
    the second element is its length in percent divided by 100.
    Note that one of both returned elements is None.
    """
    responsive_length = responsive_length.strip()
    if responsive_length.endswith('px'):
        return (int(responsive_length.rstrip('px')), None)
    elif responsive_length.endswith('%'):
        return (None, float(responsive_length.rstrip('%')) / 100)
    return (None, None)


class CascadeUtilitiesMixin(metaclass=MediaDefiningClass):
    """
    If a Cascade plugin is listed in ``settings.CMSPLUGIN_CASCADE['plugins_with_extra_mixins']``,
    then this ``CascadeUtilitiesMixin`` class is added automatically to its plugin class in order to
    enrich it with utility classes, such as :class:`cmsplugin_cascade.bootstrap4.mixins.BootstrapUtilities`.
    """
    def __str__(self):
        return self.plugin_class.get_identifier(self)

    def get_form(self, request, obj=None, **kwargs):
        form = kwargs.get('form', self.form)
        assert issubclass(form, EntangledModelFormMixin), "Form must inherit from EntangledModelFormMixin"
        kwargs['form'] = type(form.__name__, (self.utility_form_mixin, form), {})
        return super().get_form(request, obj, **kwargs)

    @classmethod
    def get_css_classes(cls, obj):
        """Enrich list of CSS classes with customized ones"""
        css_classes = super().get_css_classes(obj)
        for utility_field_name in cls.utility_form_mixin.base_fields.keys():
            css_class = obj.glossary.get(utility_field_name)
            if css_class:
                if isinstance(css_class, str):
                    css_classes.append(css_class)
                elif isinstance(css_class, list):
                    css_classes.extend(css_class)
        return css_classes


class NamedCSSClasses:
    """
    Factory for building a class ``NamedCSSClassesMixin``. This class then is used as a mixin to
    all sorts of Cascade plugins. It shall be used to optionally activate preconfigured CSS classes
    for each configured plugin.
    To configure, pass in a list of 2-tuples, consisting of the CSS class plus a string describing
    this feature. For example:
    ```
    CMSPLUGIN_CASCADE['plugins_with_extra_mixins'] = {
        'LinkPlugin': NamedCSSClasses([
            ('stretched-link', "Use stretched Link"),
            ('full-width', "Full width"),
            …
        ]),
        …
    }
    ```

    The above configuration will add a checkbox for each entry in that list to the plugin editors.
    The administrator then can choose whether to add those classes to the HTML element or not.
    """
    def __new__(cls, choices):
        named_css_classes = MultipleChoiceField(
            label=_("Extra Styles"),
            choices=choices,
            widget=CheckboxSelectMultiple,
            required=False,
        )

        class Meta:
            entangled_fields = {'glossary': ['named_css_classes']}

        attrs = {
            'named_css_classes': named_css_classes,
            'Meta': Meta,
        }
        utility_form_mixin = type('UtilitiesFormMixin', (EntangledModelFormMixin,), attrs)
        return type('NamedCSSClassesMixin', (CascadeUtilitiesMixin,), {'utility_form_mixin': utility_form_mixin})
