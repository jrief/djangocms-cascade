import pytest
from bs4 import BeautifulSoup
from django.contrib import admin
from django.http import QueryDict
from cms.api import create_page, add_plugin
from cms.utils.plugins import build_plugin_tree
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



if False:

    # add a RowPlugin with 3 Columns
    row_model = add_plugin(self.placeholder, BootstrapRowPlugin, 'en', target=container_model)
    row_plugin = row_model.get_plugin_class_instance()
    row_change_form = BootstrapRowForm({'num_children': 3})
    row_change_form.full_clean()
    row_plugin.save_model(self.request, row_model, row_change_form, False)
    self.assertDictEqual(row_model.glossary, {})
    self.assertIsInstance(row_model, CascadeElement)
    self.assertEqual(str(row_model), 'with 3 columns')
    plugin_list = [container_model, row_model]
    columns_qs = CascadeElement.objects.filter(parent_id=row_model.id)
    self.assertEqual(columns_qs.count(), 3)
    for column_model in columns_qs:
        self.assertIsInstance(column_model, CascadeElement)
        column_plugin = column_model.get_plugin_class_instance()
        self.assertIsInstance(column_plugin, BootstrapColumnPlugin)
        self.assertEqual(column_model.parent.id, row_model.id)
        self.assertEqual(str(column_model), 'default width: 4 units')
        plugin_list.append(column_model)

    # Render the Container Plugin with all of its children
    build_plugin_tree(plugin_list)
    html = self.get_html(container_model, self.get_request_context())
    self.assertHTMLEqual(html, '<div class="container"><div class="row">' +
                         '<div class="col-sm-4"></div><div class="col-sm-4"></div><div class="col-sm-4"></div>' +
                         '</div></div>')

    # change data inside the first column
    column_model = columns_qs[0]
    delattr(column_model, '_inst')
    column_plugin = column_model.get_plugin_class_instance(self.admin_site)
    column_plugin.cms_plugin_instance = column_model
    post_data = QueryDict('', mutable=True)
    post_data.update({'sm-column-offset': 'col-sm-offset-1', 'sm-column-width': 'col-sm-3'})
    ModelForm = column_plugin.get_form(self.request, column_model)
    form = ModelForm(post_data, None, instance=column_model)
    self.assertTrue(form.is_valid())
    column_plugin.save_model(self.request, column_model, form, True)

    # change data inside the second column
    column_model = columns_qs[1]
    delattr(column_model, '_inst')
    column_plugin = column_model.get_plugin_class_instance(self.admin_site)
    column_plugin.cms_plugin_instance = column_model
    post_data = QueryDict('', mutable=True)
    post_data.update({'sm-responsive-utils': 'hidden-sm', 'sm-column-width': 'col-sm-4'})
    ModelForm = column_plugin.get_form(self.request, column_model)
    form = ModelForm(post_data, None, instance=column_model)
    self.assertTrue(form.is_valid())
    column_plugin.save_model(self.request, column_model, form, False)

    html = self.get_html(container_model, self.get_request_context())
    self.assertHTMLEqual(html, '<div class="container"><div class="row">' +
                         '<div class="col-sm-3 col-sm-offset-1"></div><div class="col-sm-4 hidden-sm"></div><div class="col-sm-4"></div>' +
                         '</div></div>')
