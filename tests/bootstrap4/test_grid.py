import pytest
from cmsplugin_cascade.bootstrap4.grid import Bootstrap4Row, Bootstrap4Column, BootstrapException


def test_3_cols_xs():
    row = Bootstrap4Row()
    for _ in range(3):
        row.add_column(Bootstrap4Column('col'))
    print(row[0])
    print
    print(row[1])
    print
    print(row.get_bounds())


def test_mix_flex_with_fixed():
    row = Bootstrap4Row()
    with pytest.raises(BootstrapException):
        row.add_column(Bootstrap4Column('col col-1'))


@pytest.mark.skip
def test_grid2():
    row = Bootstrap4Row()
    #for k in range(0, 1):
    row.add_column(Bootstrap4Column('col col-sm-6 col-lg-3'))
    print
    print(row[0])
