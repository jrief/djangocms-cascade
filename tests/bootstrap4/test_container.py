import pytest
from bs4 import BeautifulSoup
from django.utils.html import strip_spaces_between_tags
from cms.plugin_rendering import ContentRenderer
from cms.utils.plugins import build_plugin_tree
from cmsplugin_cascade.models import CascadeElement
from cmsplugin_cascade.bootstrap4.container import BootstrapColumnPlugin


@pytest.mark.django_db
def test_edit_bootstrap_container(rf, bootstrap_container):
    container_plugin, container_model = bootstrap_container
    request = rf.get('/')
    ModelForm = container_plugin.get_form(request, container_model)
    data = {'breakpoints': ['sm', 'md']}
    form = ModelForm(data, None, instance=container_model)
    assert form.is_valid()
    soup = BeautifulSoup(form.as_p(), features='lxml')
    input_element = soup.find(id="id_breakpoints_0")
    assert {'type': 'checkbox', 'name': 'breakpoints', 'value': 'xs'}.items() <= input_element.attrs.items()
    input_element = soup.find(id="id_breakpoints_2")
    assert {'type': 'checkbox', 'name': 'breakpoints', 'value': 'md', 'checked': ''}.items() <= input_element.attrs.items()
    input_element = soup.find(id="id_fluid")
    assert {'type': 'checkbox', 'name': 'fluid'}.items() <= input_element.attrs.items()
    container_plugin.save_model(request, container_model, form, False)
    assert container_model.glossary['breakpoints'] == ['sm', 'md']
    assert 'fluid' in container_model.glossary
    assert str(container_model) == "for Landscape Phones, Tablets"


@pytest.mark.django_db
def test_edit_bootstrap_row(rf, bootstrap_row):
    row_plugin, row_model = bootstrap_row
    request = rf.get('/')
    ModelForm = row_plugin.get_form(request, row_model)
    data = {'num_children': 3}
    form = ModelForm(data, None, instance=row_model)
    assert form.is_valid()
    row_plugin.save_model(request, row_model, form, False)

    container_model, container_plugin = row_model.parent.get_plugin_instance()
    plugin_list = [container_model, row_model]

    # we now should have three columns attached to the row
    assert row_model.get_descendant_count() == 3
    for cms_plugin in row_model.get_descendants():
        column_model, column_plugin = cms_plugin.get_plugin_instance()
        assert isinstance(column_model, CascadeElement)
        assert isinstance(column_plugin, BootstrapColumnPlugin)
        assert column_model.parent.id == row_model.id
        plugin_list.append(column_model)

    # change data inside the first column
    cms_plugin = row_model.get_descendants().first()
    column_model, column_plugin = cms_plugin.get_plugin_instance()
    data = {'xs-column-width': 'col', 'sm-column-offset': 'offset-sm-1', 'sm-column-width': 'col-sm-3'}
    ModelForm = column_plugin.get_form(request, column_model)
    form = ModelForm(data, None, instance=column_model)
    assert form.is_valid()
    column_plugin.save_model(request, column_model, form, True)

    # change data inside the last column
    cms_plugin = row_model.get_descendants().last()
    column_model, column_plugin = cms_plugin.get_plugin_instance()
    data = {'xs-column-width': 'col', 'sm-responsive-utils': 'hidden-sm', 'sm-column-width': 'col-sm-4'}
    ModelForm = column_plugin.get_form(request, column_model)
    form = ModelForm(data, None, instance=column_model)
    assert form.is_valid()
    column_plugin.save_model(request, column_model, form, False)

    # render the plugin and check the output
    context = {
        'request': request,
    }
    content_renderer = ContentRenderer(request)
    row_model.parent.child_plugin_instances
    for plugin in plugin_list:
        plugin.refresh_from_db()
    build_plugin_tree(plugin_list)
    html = content_renderer.render_plugin(container_model, context)
    html = strip_spaces_between_tags(html).strip()
    assert html == '<div class="container"><div class="row"><div class="col col-sm-3 offset-sm-1">' \
                   '</div><div class="col"></div><div class="col col-sm-4 hidden-sm"></div></div></div>'
