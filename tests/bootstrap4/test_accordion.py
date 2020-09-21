import pytest
from django.template.context import RequestContext
from cms.api import add_plugin
from cms.plugin_rendering import ContentRenderer
from cms.utils.plugins import build_plugin_tree
from cmsplugin_cascade.models import CascadeElement
from cmsplugin_cascade.bootstrap4.accordion import BootstrapAccordionGroupPlugin, BootstrapAccordionPlugin


@pytest.fixture
@pytest.mark.django_db
def bootstrap_accordion(rf, admin_site, bootstrap_column):
    request = rf.get('/')
    column_plugin, column_model = bootstrap_column

    # add accordion plugin
    accordion_model = add_plugin(column_model.placeholder, BootstrapAccordionPlugin, 'en', target=column_model)
    assert isinstance(accordion_model, CascadeElement)
    accordion_plugin = accordion_model.get_plugin_class_instance(admin_site)
    assert isinstance(accordion_plugin, BootstrapAccordionPlugin)
    data = {'num_children': 2, 'close_others': 'on', 'first_is_open': 'on'}
    ModelForm = accordion_plugin.get_form(request, accordion_model)
    form = ModelForm(data, None, instance=accordion_model)
    assert form.is_valid()
    accordion_plugin.save_model(request, accordion_model, form, False)
    assert accordion_model.glossary['close_others'] is True
    assert accordion_model.glossary['first_is_open'] is True
    for child in accordion_model.get_children():
        assert isinstance(child.get_plugin_class_instance(admin_site), BootstrapAccordionGroupPlugin)
    return accordion_plugin, accordion_model


@pytest.mark.django_db
def test_edit_accordion_group(rf, admin_site, bootstrap_accordion):
    request = rf.get('/')
    accordion_plugin, accordion_model = bootstrap_accordion
    first_group = accordion_model.get_first_child()
    group_model, group_plugin = first_group.get_plugin_instance(admin_site)
    data = {'heading': "Hello", 'body_padding': 'on'}
    ModelForm = group_plugin.get_form(request, group_model)
    form = ModelForm(data, None, instance=group_model)
    assert form.is_valid()
    group_plugin.save_model(request, group_model, form, False)
    assert group_model.glossary['heading'] == "Hello"
    assert group_model.glossary['body_padding'] is True

    # render the plugin
    build_plugin_tree([accordion_model, group_model])
    context = RequestContext(request)
    content_renderer = ContentRenderer(request)
    html = content_renderer.render_plugin(accordion_model, context).strip()
    html = html.replace('\n', '').replace('\t', '')
    expected = """<div id="cmsplugin_{accordion_id}" class="accordion"><div class="card">
<div class="card-header" id="heading_{group_id}"><h5 class="mb-0">
<button class="btn btn-link" type="button" data-toggle="collapse" data-target="#collapse_{group_id}" aria-expanded="true" aria-controls="collapse_{group_id}">
Hello</button></h5></div>
<div id="collapse_{group_id}" class="collapse" aria-labelledby="heading_{group_id}" data-parent="#cmsplugin_{accordion_id}">
<div class="card-body"></div></div></div></div>""".format(accordion_id=accordion_model.id, group_id=group_model.id)
    expected = expected.replace('\n', '').replace('\t', '')
    assert html == expected
