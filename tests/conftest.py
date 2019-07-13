import pytest
from django.contrib import admin
from cms.api import create_page, add_plugin
from cmsplugin_cascade.models import CascadePage
from cmsplugin_cascade.models import CascadeElement
from cmsplugin_cascade.bootstrap4.container import BootstrapContainerPlugin, BootstrapRowPlugin


@pytest.fixture
def admin_site():
    return admin.sites.AdminSite()


@pytest.fixture
@pytest.mark.django_db
def cms_page():
    home_page = create_page(title='HOME', template='testing.html', language='en')
    if not home_page.is_home:
        home_page.set_as_homepage()
    CascadePage.assure_relation(home_page)
    return home_page


@pytest.fixture
@pytest.mark.django_db
def cms_placeholder(cms_page):
    placeholder = cms_page.placeholders.get(slot='Main Content')
    return placeholder


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
