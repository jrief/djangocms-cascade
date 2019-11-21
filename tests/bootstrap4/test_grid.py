import pytest
from cmsplugin_cascade.bootstrap4.grid import (Bootstrap4Container, Bootstrap4Row, Bootstrap4Column, BootstrapException,
                                               Breakpoint, Bound, fluid_bounds)

def test_breakpoint_iter():
    for k, bp in enumerate(Breakpoint):
        if k == 0: assert bp == Breakpoint.xs
        if k == 1: assert bp == Breakpoint.sm
        if k == 2: assert bp == Breakpoint.md
        if k == 3: assert bp == Breakpoint.lg
        if k == 4: assert bp == Breakpoint.xl
    assert k == 4


def test_breakpoint_range():
    for k, bp in enumerate(Breakpoint.range(Breakpoint.xs, Breakpoint.xl)):
        if k == 0: assert bp == Breakpoint.xs
        if k == 1: assert bp == Breakpoint.sm
        if k == 2: assert bp == Breakpoint.md
        if k == 3: assert bp == Breakpoint.lg
        if k == 4: assert bp == Breakpoint.xl
    assert k == 4


def test_breakpoint_partial():
    for k, bp in enumerate(Breakpoint.range(Breakpoint.sm, Breakpoint.lg)):
        if k == 0: assert bp == Breakpoint.sm
        if k == 1: assert bp == Breakpoint.md
        if k == 2: assert bp == Breakpoint.lg
    assert k == 2


def test_xs_cols():
    """
    <div class="container">
        <div class="row">
            <div class="col"></div>
            <div class="col"></div>
            <div class="col"></div>
        </div>
    </div>
    """
    container = Bootstrap4Container()
    row = container.add_row(Bootstrap4Row())
    for _ in range(3):
        row.add_column(Bootstrap4Column('col'))
    assert row[0].get_bound(Breakpoint.xs) == Bound(106.7, 190.7)
    assert row[1].get_bound(Breakpoint.xs) == Bound(106.7, 190.7)
    assert row[2].get_bound(Breakpoint.xs) == Bound(106.7, 190.7)
    assert row[2].get_bound(Breakpoint.sm) == Bound(180.0, 180.0)
    assert row[2].get_bound(Breakpoint.md) == Bound(240.0, 240.0)
    assert row[2].get_bound(Breakpoint.lg) == Bound(320.0, 320.0)
    assert row[2].get_bound(Breakpoint.xl) == Bound(380.0, 380.0)


def test_fluid_xs_cols():
    """
    <div class="container-fluid">
        <div class="row">
            <div class="col"></div>
            <div class="col"></div>
            <div class="col"></div>
        </div>
    </div>
    """
    container = Bootstrap4Container(bounds=fluid_bounds)
    row = container.add_row(Bootstrap4Row())
    for _ in range(3):
        row.add_column(Bootstrap4Column('col'))
    assert row[0].get_bound(Breakpoint.xs) == Bound(106.7, 192.0)
    assert row[1].get_bound(Breakpoint.xs) == Bound(106.7, 192.0)
    assert row[2].get_bound(Breakpoint.xs) == Bound(106.7, 192.0)
    assert row[2].get_bound(Breakpoint.sm) == Bound(192.0, 256.0)
    assert row[2].get_bound(Breakpoint.md) == Bound(256.0, 330.7)
    assert row[2].get_bound(Breakpoint.lg) == Bound(330.7, 400.0)
    assert row[2].get_bound(Breakpoint.xl) == Bound(400.0, 660.0)


def test_xs_cols_with_flex():
    """
    <div class="container">
        <div class="row">
            <div class="col-3"></div>
            <div class="col"></div>
            <div class="col"></div>
        </div>
    </div>
    """
    container = Bootstrap4Container()
    row = container.add_row(Bootstrap4Row())
    row.add_column(Bootstrap4Column('col-3'))
    row.add_column(Bootstrap4Column('col'))
    row.add_column(Bootstrap4Column('col'))
    repr(row[0])
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
    """
    <div class="container">
        <div class="row">
            <div class="col-3"></div>
            <div class="col-auto"></div>
            <div class="col"></div>
        </div>
    </div>
    """
    container = Bootstrap4Container()
    row = container.add_row(Bootstrap4Row())
    row.add_column(Bootstrap4Column('col-3'))
    row.add_column(Bootstrap4Column('col-auto'))
    row.add_column(Bootstrap4Column('col'))
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
    """
    <div class="container">
        <div class="row">
            <div class="col-12 col-sm-6 col-lg-4"></div>
            <div class="col-12 col-sm-6 col-lg-4"></div>
            <div class="col-12 col-sm-12 col-lg-4"></div>
        </div>
    </div>
    """
    container = Bootstrap4Container()
    row = container.add_row(Bootstrap4Row())
    row.add_column(Bootstrap4Column('col-12 col-sm-6 col-lg-4'))
    row.add_column(Bootstrap4Column('col-12 col-sm-6 col-lg-4'))
    row.add_column(Bootstrap4Column('col-12 col-sm-12 col-lg-4'))
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


def test_haricot():
    """
    <div class="container">
        <div class="row">
            <div class="col"></div>
            <div class="col-auto"></div>
            <div class="col-2"></div>
        </div>
    </div>
    """
    container = Bootstrap4Container()
    row = container.add_row(Bootstrap4Row())
    row.add_column(Bootstrap4Column('col'))
    row.add_column(Bootstrap4Column('col-auto'))
    row.add_column(Bootstrap4Column('col-2'))
    assert row[0].get_bound(Breakpoint.xs) == Bound(30.0, 416.7)
    assert row[0].get_bound(Breakpoint.sm) == Bound(30.0, 390.0)
    assert row[0].get_bound(Breakpoint.md) == Bound(30.0, 540.0)
    assert row[0].get_bound(Breakpoint.lg) == Bound(30.0, 740.0)
    assert row[0].get_bound(Breakpoint.xl) == Bound(30.0, 890.0)

    assert row[1].get_bound(Breakpoint.xs) == Bound(30.0, 416.7)
    assert row[1].get_bound(Breakpoint.sm) == Bound(30.0, 390.0)
    assert row[1].get_bound(Breakpoint.md) == Bound(30.0, 540.0)
    assert row[1].get_bound(Breakpoint.lg) == Bound(30.0, 740.0)
    assert row[1].get_bound(Breakpoint.xl) == Bound(30.0, 890.0)

    assert row[2].get_bound(Breakpoint.xs) == Bound(53.3, 95.3)
    assert row[2].get_bound(Breakpoint.sm) == Bound(90.0, 90.0)
    assert row[2].get_bound(Breakpoint.md) == Bound(120.0, 120.0)
    assert row[2].get_bound(Breakpoint.lg) == Bound(160.0, 160.0)
    assert row[2].get_bound(Breakpoint.xl) == Bound(190.0, 190.0)


def test_nested_row():
    """
    <div class="container">
        <div class="row">
            <div class="col">
                <div class="row">
                    <div class="col-5"></div>
                    <div class="col-7"></div>
                </div>
            </div>
            <div class="col"></div>
        </div>
    </div>
    """
    container = Bootstrap4Container()
    row = container.add_row(Bootstrap4Row())
    row.add_column(Bootstrap4Column('col'))
    row.add_column(Bootstrap4Column('col'))
    nested_row = row[0].add_row(Bootstrap4Row())
    nested_row.add_column(Bootstrap4Column('col-5'))
    nested_row.add_column(Bootstrap4Column('col-7'))

    assert nested_row[0].get_bound(Breakpoint.xs) == Bound(66.7, 119.2)
    assert nested_row[1].get_bound(Breakpoint.xs) == Bound(93.3, 166.8)
    assert nested_row[0].get_bound(Breakpoint.sm) == Bound(112.5, 112.5)
    assert nested_row[1].get_bound(Breakpoint.sm) == Bound(157.5, 157.5)
    assert nested_row[0].get_bound(Breakpoint.md) == Bound(150.0, 150.0)
    assert nested_row[1].get_bound(Breakpoint.md) == Bound(210.0, 210.0)
    assert nested_row[0].get_bound(Breakpoint.lg) == Bound(200.0, 200.0)
    assert nested_row[1].get_bound(Breakpoint.lg) == Bound(280.0, 280.0)
    assert nested_row[0].get_bound(Breakpoint.xl) == Bound(237.5, 237.5)
    assert nested_row[1].get_bound(Breakpoint.xl) == Bound(332.5, 332.5)


def test_repr():
    container = Bootstrap4Container()
    row = container.add_row(Bootstrap4Row())
    row.add_column(Bootstrap4Column('col'))
    row.compute_column_bounds()
    assert repr(container) == 'Bootstrap4Container(Bootstrap4Row(Bootstrap4Column(Break(xs: fixed=0, flex=True, auto=False), Break(sm: fixed=0, flex=True, auto=False), Break(md: fixed=0, flex=True, auto=False), Break(lg: fixed=0, flex=True, auto=False), Break(xl: fixed=0, flex=True, auto=False))))'
