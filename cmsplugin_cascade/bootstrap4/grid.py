from copy import copy
from enum import Enum, unique
from functools import reduce
import itertools
from operator import add
import re
from django.utils.translation import gettext_lazy as _


class BootstrapException(Exception):
    """
    Raised if arrangement of Bootstrap-4 elements would render weird results.
    """


@unique
class Breakpoint(Enum):
    """
    Enumerate the five breakpoints defined by the Bootstrap-4 CSS framework.
    """
    xs = 0
    sm = 1
    md = 2
    lg = 3
    xl = 4

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

    @property
    def label(self):
        return [
            _("Portrait Phones"),
            _("Landscape Phones"),
            _("Tablets"),
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
            '(min-width: 1200px)',
        ][self.value]


class Bound(object):
    def __init__(self, min, max):
        self.min = float(min)
        self.max = float(max)

    def __copy__(self):
        return type(self)(self.min, self.max)

    def __eq__(self, other):
        return round(self.min, 1) == round(other.min, 1) and round(self.max, 1) == round(other.max, 1)

    def __add__(self, other):
        return Bound(
            self.min + other.min,
            self.max + other.max,
        )

    def __sub__(self, other):
        return Bound(
            self.min - other.min,
            self.max - other.max,
        )

    def __repr__(self):
        return "{}(min={}, max={})".format(self.__class__.__name__, self.min, self.max)

    def extend(self, other):
        self.min = min(self.min, other.min)
        self.max = max(self.max, other.max)


default_bounds = {
    Breakpoint.xs: Bound(320, 572),
    Breakpoint.sm: Bound(540, 540),
    Breakpoint.md: Bound(720, 720),
    Breakpoint.lg: Bound(960, 960),
    Breakpoint.xl: Bound(1140, 1140),
}

fluid_bounds = {
    Breakpoint.xs: Bound(320, 576),
    Breakpoint.sm: Bound(576, 768),
    Breakpoint.md: Bound(768, 992),
    Breakpoint.lg: Bound(992, 1200),
    Breakpoint.xl: Bound(1200, 1980),
}


class Break(object):
    def __init__(self, breakpoint, classes, narrower=None):
        self.breakpoint = breakpoint
        self.fixed_units = 0
        self.flex_column = False
        self.auto_column = False
        self._normalize_col_classes(classes)
        if isinstance(narrower, Break):
            self._inherit_from(narrower)
        self.bound = None

    def _normalize_col_classes(self, classes):
        if self.breakpoint == Breakpoint.xs:
            fixed_pat = re.compile(r'^col-(\d+)$')
            flex_pat = re.compile(r'^col$')
            auto_pat = re.compile(r'^col-auto$')
        else:
            fixed_pat = re.compile(r'^col-{}-(\d+)$'.format(self.breakpoint.name))
            flex_pat = re.compile(r'^col-{}$'.format(self.breakpoint.name))
            auto_pat = re.compile(r'^col-{}-auto$'.format(self.breakpoint.name))
        for col_class in classes:
            # look for CSS classes matching fixed size columns
            fixed = fixed_pat.match(col_class)
            if fixed:
                if self.fixed_units or self.flex_column or self.auto_column:
                    raise BootstrapException("Can not mix fixed- with flex- or auto-column")
                units = int(fixed.group(1))
                if units < 1 or units > 12:
                    raise BootstrapException("Column units value {} out of range".format(units))
                self.fixed_units = units

            # look for CSS classes matching flex columns
            flex = flex_pat.match(col_class)
            if flex:
                if self.fixed_units or self.flex_column or self.auto_column:
                    raise BootstrapException("Can not mix flex- with fixed- or auto-column")
                self.flex_column = True

            # look for CSS classes matching auto columns
            auto = auto_pat.match(col_class)
            if auto:
                if self.fixed_units or self.flex_column or self.auto_column:
                    raise BootstrapException("Can not mix auto- with fixed- or flex-column")
                self.auto_column = True

    def _inherit_from(self, narrower):
        if self.breakpoint <= narrower.breakpoint:
            raise BootstrapException("Can only inherit column bounds from narrower breakpoint")
        if self.fixed_units == 0 and self.flex_column is False and self.auto_column is False:
            self.fixed_units = narrower.fixed_units
            self.flex_column = narrower.flex_column
            self.auto_column = narrower.auto_column

    def __copy__(self):
        newone = type(self)()
        if self.bound:
            newone.bound = dict(self.bound)
        return newone

    def __repr__(self):
        return "{}({}: fixed={}, flex={}, auto={})".format(
            self.__class__.__name__, self.breakpoint.name, self.fixed_units, self.flex_column, self.auto_column)


class Bootstrap4Container(list):
    """
    Abstracts a Bootstrap-4 container element, such as ``<div class="container">...</div>``, so that the minimum and
    maximum widths each each child row can be computed.
    Each container object is a list of one to many ``Bootstrap4Row`` instances.
    In order to model a "fluid" container, use ``fluid_bounds`` during construction.
    """
    # def __init__(self, bounds=app_settings.CMSPLUGIN_CASCADE['bootstrap4']['default_bounds']):
    def __init__(self, bounds=default_bounds):
            self.bounds = bounds

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ', '.join([repr(o) for o in self]))

    def add_row(self, row):
        if isinstance(row.parent, (Bootstrap4Container, Bootstrap4Column)):
            # detach from previous container or column
            pos = row.parent.index(row)
            row.parent.pop(pos)
        row.parent = self
        row.bounds = dict(self.bounds)
        self.append(row)
        return row


class Bootstrap4Row(list):
    """
    Abstracts a Bootstrap-4 row element, such as ``<div class="row">...</div>``, so that the minimum and maximum widths
    each each child columns can be computed.
    Each row object is a list of 1 to many ``Bootstrap4Column`` instances.
    """
    parent = None
    bounds = None

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ', '.join([repr(o) for o in self]))

    def add_column(self, column):
        if isinstance(column.parent, Bootstrap4Row):
            pos = column.parent.index(column)
            column.parent.pop(pos)
        column.parent = self
        self.append(column)

    def compute_column_bounds(self):
        assert isinstance(self.bounds, dict), "Expected `bounds` to be a dict."
        for bp in [Breakpoint.xs, Breakpoint.sm, Breakpoint.md, Breakpoint.lg, Breakpoint.xl]:
            if bp in self.bounds:
                remaining_width = copy(self.bounds[bp])

            # first compute the bounds of columns with a fixed width
            for column in self:
                if column.breaks[bp].fixed_units:
                    assert column.breaks[bp].bound is None, "Expected `column.breaks[bp].bound` to be None."
                    column.breaks[bp].bound = Bound(
                        column.breaks[bp].fixed_units * self.bounds[bp].min / 12,
                        column.breaks[bp].fixed_units * self.bounds[bp].max / 12,
                    )
                    remaining_width -= column.breaks[bp].bound

            flex_columns = reduce(add, [int(col.breaks[bp].flex_column) for col in self], 0)
            auto_columns = reduce(add, [int(col.breaks[bp].auto_column) for col in self], 0)
            if auto_columns:
                # we use auto-columns, therefore estimate the min- and max values
                for column in self:
                    if column.breaks[bp].flex_column or column.breaks[bp].auto_column:
                        assert column.breaks[bp].bound is None, "Expected `column.breaks[bp].bound` to be None."
                        column.breaks[bp].bound = Bound(
                            30,
                            remaining_width.max - 30 * (flex_columns + auto_columns),
                        )
            else:
                # we use flex-columns exclusively, therefore subdivide the remaining width
                for column in self:
                    if column.breaks[bp].flex_column:
                        assert column.breaks[bp].bound is None, "Expected `column.breaks[bp].bound` to be None."
                        column.breaks[bp].bound = Bound(
                            remaining_width.min / flex_columns,
                            remaining_width.max / flex_columns,
                        )


class Bootstrap4Column(list):
    """
    Abstracts a Bootstrap-4 column element, such as ``<div class="col...">...</div>``, which shall be added to a
    ``Bootstrap4Row`` element.
    Each column may contain elements of type ``Bootstrap4Row``.
    For each breakpoint, a columns knows its extensions.
    """
    parent = None

    def __init__(self, classes=[]):
        if isinstance(classes, str):
            classes = classes.split()
        narrower = None
        self.breaks = {}
        for bp in Breakpoint:
            self.breaks[bp] = Break(bp, classes, narrower)
            narrower = self.breaks[bp]

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ', '.join([repr(self.breaks[bp]) for bp in Breakpoint]))

    def __copy__(self):
        newone = type(self)()
        newone.__dict__.update(self.__dict__)
        return newone

    def add_row(self, row):
        if isinstance(row.parent, (Bootstrap4Container, Bootstrap4Column)):
            # detach from previous container or column
            pos = row.parent.index(row)
            row.parent.pop(pos)
            row.parent.bounds = None
        row.parent = self
        row.bounds = dict((bp, self.get_bound(bp)) for bp in Breakpoint)
        self.append(row)
        return row

    def get_bound(self, breakpoint):
        if self.breaks[breakpoint].bound is None:
            self.parent.compute_column_bounds()
            assert self.breaks[breakpoint].bound, "Expected `column.breaks[bp].bound` not to be None."
        return self.breaks[breakpoint].bound

    def get_min_max_bounds(self):
        """
        Return a dict of min- and max-values for the given column.
        This is required to estimate the bounds of images.
        """
        bound = Bound(999999.0, 0.0)
        for bp in Breakpoint:
            bound.extend(self.get_bound(bp))
        return {'min': bound.min, 'max': bound.max}
