from enum import Enum, unique
import itertools

from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


@unique
class Breakpoint(Enum):
    """
    Enumerate the six breakpoints defined by the Bootstrap-5 CSS framework.
    """
    xs = 0
    sm = 1
    md = 2
    lg = 3
    xl = 4
    xxl = 5

    @classmethod
    def range(cls, first, last):
        """
        Iterate over all elements, starting from `first` until `last`.
        The last element is included.
        """
        if first: first = first.value
        if last: last = last.value + 1
        return itertools.islice(cls, first, last)

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    @property
    def label(self):
        return [
            _("Portrait Phones"),
            _("Landscape Phones"),
            _("Portrait Tablets"),
            _("Landscape Tablets"),
            _("Laptops"),
            _("Large Desktops"),
        ][self.value]

    @property
    def media_query(self):
        return [
            '(max-width: 575.98px)',
            '(min-width: 576px) and (max-width: 767.98px)',
            '(min-width: 768px) and (max-width: 991.98px)',
            '(min-width: 992px) and (max-width: 1199.98px)',
            '(min-width: 1200px) and (max-width: 1399.98px)',
            '(min-width: 1400px)',
        ][self.value]

    @property
    def min_width(self):
        return [
            None,
            576,
            768,
            992,
            1200,
            1400,
        ][self.value]

    @property
    def max_width(self):
        return [
            576,
            768,
            992,
            1200,
            1400,
            None,
        ][self.value]


def get_widget_choices():
    return [
        (Breakpoint.xs.name, format_html("&ensp;<strong>{}</strong><br>{} (<{}px)", _("Extra small"), Breakpoint.xs.label, 576)),
        (Breakpoint.sm.name, format_html("&ensp;<strong>{}</strong><br>{} (≥{}px, <{}px)", _("Small"), Breakpoint.sm.label, 576, 768)),
        (Breakpoint.md.name, format_html("&ensp;<strong>{}</strong><br>{} (≥{}px, <{}px)",_("Medium"), Breakpoint.md.label, 768, 992)),
        (Breakpoint.lg.name, format_html("&ensp;<strong>{}</strong><br>{} (≥{}px, <{}px)",_("Large"), Breakpoint.lg.label, 992, 1200)),
        (Breakpoint.xl.name, format_html("&ensp;<strong>{}</strong><br>{} (≥{}px, <{}px)", _("Extra large"), Breakpoint.xl.label, 1200, 1400)),
        (Breakpoint.xxl.name, format_html("&ensp;<strong>{}</strong><br>{} (>{}px)", _("XXL"), Breakpoint.xxl.label, 1400)),
    ]
