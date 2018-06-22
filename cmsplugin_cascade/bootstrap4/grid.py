# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from copy import copy
from enum import Enum, unique
from functools import reduce
from operator import add
import re
from django.utils.translation import ugettext_lazy as _


class BootstrapException(Exception):
    """
    Raised if arrangement of Bootstrap-4 elements would render weird results.
    """


@unique
class Breakpoint(Enum):
    xs = 0
    sm = 1
    md = 2
    lg = 3
    xl = 4

    class Labels:
        xs = _('Breakpoint.xs')
        sm = _('Breakpoint.sm')
        md = _('Breakpoint.md')
        lg = _('Breakpoint.lg')
        xl = _('Breakpoint.xl')

    @staticmethod
    def register_messages():
        from django.utils.translation import ugettext_noop
        ugettext_noop('Breakpoint.xs')
        ugettext_noop('Breakpoint.sm')
        ugettext_noop('Breakpoint.md')
        ugettext_noop('Breakpoint.lg')
        ugettext_noop('Breakpoint.xl')

    @classmethod
    def all(self):
        return [Breakpoint.xs, Breakpoint.sm, Breakpoint.md, Breakpoint.lg, Breakpoint.xl]


class Bound(object):
    def __init__(self, min, max):
        self.min = float(min)
        self.max = float(max)

    def __copy__(self):
        return type(self)(self.min, self.max)

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


class ColumnBreak(object):
    def __init__(self, breakpoint, classes, narrower=None):
        self.breakpoint = breakpoint
        self.fixed_units = 0
        self.flex_units = 0
        self.auto_columns = 0
        self._normalize_col_classes(classes)
        if isinstance(narrower, ColumnBreak):
            self._inherit_from(narrower)
        self.bound = None

    def _normalize_col_classes(self, classes):
        if self.breakpoint == Breakpoint.xs:
            flex_pat = re.compile(r'^col$')
            fixed_pat = re.compile(r'^col-(\d+)$')
            auto_pat = re.compile(r'^col-auto$')
        else:
            flex_pat = re.compile(r'^col-{}$'.format(self.breakpoint.name))
            fixed_pat = re.compile(r'^col-{}-(\d+)$'.format(self.breakpoint.name))
            auto_pat = re.compile(r'^col-{}-auto$'.format(self.breakpoint.name))
        for col_class in classes:
            flex = flex_pat.match(col_class)
            if flex:
                self.flex_units = 1
            else:
                fixed = fixed_pat.match(col_class)
                if fixed:
                    if self.flex_units:
                        raise BootstrapException("Can not mix flex- with fixed unit column")
                    units = int(fixed.group(1))
                    if units < 1 or units > 12:
                        raise BootstrapException("Column units value {} out of range".format(units))
                    self.fixed_units = units
                else:
                    auto = auto_pat.match(col_class)
                    if auto:
                        if self.flex_units or self.fixed_units:
                            raise BootstrapException("Can not mix flex- or fixed units with auto column")
                        self.auto_columns = 1

    def _inherit_from(self, narrower):
        if self.flex_units == 0 and self.fixed_units == 0 and self.auto_columns == 0:
            self.flex_units = narrower.flex_units
            self.fixed_units = narrower.fixed_units
            self.auto_columns = narrower.auto_columns

    def __str__(self):
        return "{}: flex={}, fixed={}, auto={}".format(self.breakpoint.name, self.flex_units, self.fixed_units, self.auto_columns)


class Bootstrap4Row(list):
    """
    Abstracts a Bootstrap-4 row element, such as ``<div class="row">...</div>``, so that the minimum and maximum widths
    each each child columns can be computed.
    Each row object is a list of 1 to many ``Bootstrap4Column`` instances.
    """
    def __init__(self, bounds=default_bounds):
        self.bounds = dict(bounds)

    def add_column(self, column):
        if isinstance(column.parent_row, Bootstrap4Row):
            pos = column.parent_row.index(column)
            column.parent_row.pop(pos)
        column.parent_row = self
        self.append(column)

    def get_bounds(self):
        bounds = {}
        for bp in Breakpoint.all():
            remaining_width = copy(self.bounds[bp])
            fixed_bound, flex_bound, auto_bound = 3 * (None,)

            # first compute the bounds of columns with a fixed width
            for column in self:
                if column[bp].fixed_units:
                    fixed_bound = Bound(
                        column[bp].fixed_units * self.bounds[bp].min / 12,
                        column[bp].fixed_units * self.bounds[bp].max / 12,
                    )
                    remaining_width -= fixed_bound

            # next, use the remaining space and divide it through flex units
            flex_columns = reduce(add, [col[bp].flex_columns for col in self], 0)
            if flex_columns:
                flex_bound = Bound(
                    remaining_width.min / flex_columns,
                    remaining_width.max / flex_columns,
                )

            # the width of auto units is unpredictable, and furthermore may reduce the width of flex columns

        return bounds


class Bootstrap4Column(dict):
    """
    Abstracts a Bootstrap-4 column element, such as ``<div class="col...">...</div>``, which shall be added to the above
    Bootstrap4Row element.
    Each column object is a dict of 5 ``ColumnWidth`` instances.
    """
    parent_row = None

    def __init__(self, classes=[]):
        if isinstance(classes, str):
            classes = classes.split()
        self.classes = list(classes)
        narrower = None
        for bp in Breakpoint.all():
            self[bp] = ColumnBreak(bp, classes, narrower)
            narrower = self[bp]

    def __str__(self):
        return '\n'.join([str(self[bp]) for bp in Breakpoint.all()])

    def __copy__(self):
        newone = type(self)()
        newone.__dict__.update(self.__dict__)
        return newone
