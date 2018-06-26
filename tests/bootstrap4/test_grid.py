import pytest
from cmsplugin_cascade.bootstrap4.grid import (Bootstrap4Container, Bootstrap4Row, Bootstrap4Column, BootstrapException,
                                               Breakpoint, Bound)


def test_xs_cols():
    container = Bootstrap4Container()
    row = container.add_row(Bootstrap4Row())
    for _ in range(3):
        row.add_column(Bootstrap4Column('col'))
    row.compute_column_bounds()


def test_xs_cols_with_flex():
    container = Bootstrap4Container()
    row = container.add_row(Bootstrap4Row())
    row.add_column(Bootstrap4Column('col-3'))
    row.add_column(Bootstrap4Column('col'))
    row.add_column(Bootstrap4Column('col'))
    row.compute_column_bounds()
    assert row[0].get_bound(Breakpoint.xs) == Bound(80.0, 143.0)
    assert row[0].get_bound(Breakpoint.sm) == Bound(135.0, 135.0)
    assert row[0].get_bound(Breakpoint.md) == Bound(180.0, 180.0)
    assert row[0].get_bound(Breakpoint.lg) == Bound(240.0, 240.0)
    assert row[0].get_bound(Breakpoint.xl) == Bound(285.0, 285.0)

    assert row[1].get_bound(Breakpoint.xs) == Bound(120.0, 214.5)
    assert row[1].get_bound(Breakpoint.sm) == Bound(202.5, 202.5)
    assert row[1].get_bound(Breakpoint.md) == Bound(270.0, 270.0)
    assert row[1].get_bound(Breakpoint.lg) == Bound(360.0, 360.0)
    assert row[1].get_bound(Breakpoint.xl) == Bound(427.5, 427.5)


def test_xs_cols_with_auto_and_flex():
    container = Bootstrap4Container()
    row = container.add_row(Bootstrap4Row())
    row.add_column(Bootstrap4Column('col-3'))
    row.add_column(Bootstrap4Column('col-auto'))
    row.add_column(Bootstrap4Column('col'))
    row.compute_column_bounds()
    assert row[0].get_bound(Breakpoint.xs) == Bound(80.0, 143.0)
    assert row[0].get_bound(Breakpoint.sm) == Bound(135.0, 135.0)
    assert row[0].get_bound(Breakpoint.md) == Bound(180.0, 180.0)
    assert row[0].get_bound(Breakpoint.lg) == Bound(240.0, 240.0)
    assert row[0].get_bound(Breakpoint.xl) == Bound(285.0, 285.0)

    assert row[1].get_bound(Breakpoint.xs) == Bound(30.0, 369.0)
    assert row[1].get_bound(Breakpoint.sm) == Bound(30.0, 345.0)
    assert row[1].get_bound(Breakpoint.md) == Bound(30.0, 480.0)
    assert row[1].get_bound(Breakpoint.lg) == Bound(30.0, 660.0)
    assert row[1].get_bound(Breakpoint.xl) == Bound(30.0, 795.0)

    assert row[2].get_bound(Breakpoint.xs) == Bound(30.0, 369.0)
    assert row[2].get_bound(Breakpoint.sm) == Bound(30.0, 345.0)
    assert row[2].get_bound(Breakpoint.md) == Bound(30.0, 480.0)
    assert row[2].get_bound(Breakpoint.lg) == Bound(30.0, 660.0)
    assert row[2].get_bound(Breakpoint.xl) == Bound(30.0, 795.0)


def test_mix_flex_with_fixed():
    row = Bootstrap4Row()
    with pytest.raises(BootstrapException):
        row.add_column(Bootstrap4Column('col col-1'))


def test_mix_flex_with_auto():
    row = Bootstrap4Row()
    with pytest.raises(BootstrapException):
        row.add_column(Bootstrap4Column('col col-auto'))


def test_mix_fixed_with_auto():
    row = Bootstrap4Row()
    with pytest.raises(BootstrapException):
        row.add_column(Bootstrap4Column('col-1 col-auto'))


def test_growing_columns():
    container = Bootstrap4Container()
    row = container.add_row(Bootstrap4Row())
    row.add_column(Bootstrap4Column('col-12 col-sm-6 col-lg-4'))
    row.add_column(Bootstrap4Column('col-12 col-sm-6 col-lg-4'))
    row.add_column(Bootstrap4Column('col-12 col-sm-12 col-lg-4'))
    row.compute_column_bounds()
    assert row[0].get_bound(Breakpoint.xs) == Bound(320.0, 572.0)
    assert row[0].get_bound(Breakpoint.sm) == Bound(270.0, 270.0)
    assert row[0].get_bound(Breakpoint.md) == Bound(360.0, 360.0)
    assert row[0].get_bound(Breakpoint.lg) == Bound(320.0, 320.0)
    assert row[0].get_bound(Breakpoint.xl) == Bound(380.0, 380.0)

    assert row[2].get_bound(Breakpoint.xs) == Bound(320.0, 572.0)
    assert row[2].get_bound(Breakpoint.sm) == Bound(540.0, 540.0)
    assert row[2].get_bound(Breakpoint.md) == Bound(720.0, 720.0)
    assert row[2].get_bound(Breakpoint.lg) == Bound(320.0, 320.0)
    assert row[2].get_bound(Breakpoint.xl) == Bound(380.0, 380.0)
