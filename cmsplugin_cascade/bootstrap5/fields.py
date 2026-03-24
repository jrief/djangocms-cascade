from django.forms import fields
from django.utils.translation import gettext

from cmsplugin_cascade.bootstrap5.breakpoint import Breakpoint
from cmsplugin_cascade.fields import MultiSizeField


class BootstrapMultiSizeField(MultiSizeField):
    """
    Some size input fields must be specified per Bootstrap breakpoint. Use this multiple
    input field to handle this.
    """

    def __init__(self, *args, **kwargs):
        properties = [bp.name for bp in Breakpoint]
        kwargs['sublabels'] = [bp.label for bp in Breakpoint]
        super().__init__(properties, *args, **kwargs)


class AspectRatioChoiceField(fields.ChoiceField):
    def __init__(self, breakpoint, *args, **kwargs):
        kwargs.setdefault('label', gettext("Aspect Ratio for ‘{}’").format(breakpoint.label))
        choices = [
            ('16/9', "16:9"),
            ('4/3', "4:3"),
            ('1/1', "1:1"),
            ('2/1', "2:1"),
            ('21/9', "21:9"),
            ('3/2', "3:2"),
            ('2/3', "2:3"),
            ('3/4', "3:4"),
            ('9/16', "9:16"),
            ('9/21', "9:21"),
            ('1/2', "1:2"),
        ]
        self.add_original = kwargs.pop('add_original', False)
        if self.add_original:
            choices.insert(0, ('orig', gettext("Original")))
        if empty_label := kwargs.pop('empty_label', None):
            choices.insert(
                0,
                ('', empty_label)
            )
        kwargs.setdefault('choices', choices)
        super().__init__(*args, **kwargs)
