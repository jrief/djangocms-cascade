from enum import Enum, unique
import itertools

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

    def __iter__(self):
        yield self.xs
        yield self.sm
        yield self.md
        yield self.lg
        yield self.xl
        yield self.xxl

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
