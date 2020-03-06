import pytest
from cms.api import add_plugin
from cmsplugin_cascade.models import CascadeElement
from cmsplugin_cascade.bootstrap4.container import BootstrapContainerPlugin, BootstrapRowPlugin, BootstrapColumnPlugin


@pytest.fixture
@pytest.mark.django_db
def bootstrap_container(admin_site, cms_placeholder):
    # add a Bootstrap Container Plugin
    glossary = {'breakpoints': ['xs', 'sm', 'md', 'lg', 'xl'], 'fluid': ''}
    container_model = add_plugin(cms_placeholder, BootstrapContainerPlugin, 'en', glossary=glossary)
    assert isinstance(container_model, CascadeElement)
    container_plugin = container_model.get_plugin_class_instance(admin_site)
    assert isinstance(container_plugin, BootstrapContainerPlugin)
    return container_plugin, container_model


@pytest.fixture
@pytest.mark.django_db
def bootstrap_row(admin_site, bootstrap_container):
    # add a Bootstrap Row Plugin to the given container
    container_plugin, container_model = bootstrap_container
    row_model = add_plugin(container_model.placeholder, BootstrapRowPlugin, 'en', target=container_model)
    assert isinstance(row_model, CascadeElement)
    row_plugin = row_model.get_plugin_class_instance()
    assert isinstance(row_plugin, BootstrapRowPlugin)
    return row_plugin, row_model


@pytest.fixture
@pytest.mark.django_db
def bootstrap_column(admin_site, bootstrap_row):
    # add a Bootstrap Column Plugin to the given row
    row_plugin, row_model = bootstrap_row
    glossary = {'xs-column-width': 'col'}
    column_model = add_plugin(row_model.placeholder, BootstrapColumnPlugin, 'en', target=row_model, glossary=glossary)
    assert isinstance(column_model, CascadeElement)
    column_plugin = column_model.get_plugin_class_instance()
    assert isinstance(column_plugin, BootstrapColumnPlugin)
    return column_plugin, column_model
