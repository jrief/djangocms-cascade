import pytest
from django.forms.models import ModelForm
from django.template.context import RequestContext
from cms.api import add_plugin
from cms.plugin_rendering import ContentRenderer
from cmsplugin_cascade.models import CascadeElement
from cmsplugin_cascade.link.forms import LinkForm
from cmsplugin_cascade.link.cms_plugins import TextLinkPlugin


@pytest.fixture
@pytest.mark.django_db
def link(admin_site, cms_placeholder):
    """Create and edit a TextLinkPlugin"""
    class LinkModelForm(LinkForm, ModelForm):
        class Meta(LinkForm.Meta):
            model = CascadeElement

    # add text link plugin
    link_model = add_plugin(cms_placeholder, TextLinkPlugin, 'en')
    assert isinstance(link_model, CascadeElement)

    # edit text link plugin
    data = {'link_type': 'exturl', 'ext_url': 'http://test.ru/test', 'link_target': '_blank', 'link_title': 'test title'}
    form = LinkModelForm(data=data, instance=link_model)
    assert form.is_valid()
    link_model = form.save()
    link_plugin = link_model.get_plugin_class_instance(admin_site)
    assert isinstance(link_plugin, TextLinkPlugin)
    return link_plugin, link_model


@pytest.mark.django_db
def test_link_plugin(rf, link):
    """Render a LinkPluginBase"""
    link_plugin, link_model = link
    request = rf.get('/')
    context = RequestContext(request)
    content_renderer = ContentRenderer(request)
    html = content_renderer.render_plugin(link_model, context).strip()
    assert html == '<a href="http://test.ru/test" title="test title" target="_blank"></a>'
