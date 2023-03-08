import os
from bs4 import BeautifulSoup
import pytest
import factory.fuzzy
from pytest_factoryboy import register
from django import VERSION as DJANGO_VERSION
from django.forms.models import ModelForm
from django.urls import reverse, resolve
from django.core.files import File as DjangoFile
from django.template.context import RequestContext
from filer.models.filemodels import File as FilerFileModel
from cms.api import add_plugin
from cms.plugin_rendering import ContentRenderer
from cmsplugin_cascade.models import CascadeElement, IconFont
from cmsplugin_cascade.icon.forms import IconFormMixin
from cmsplugin_cascade.icon.simpleicon import SimpleIconPlugin
from cmsplugin_cascade.link.forms import LinkForm
from .conftest import UserFactory


@register
class IconFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FilerFileModel

    @classmethod
    def create(cls, **kwargs):
        filename = os.path.join(os.path.dirname(__file__), 'assets/fontello-b504201f.zip')
        fileobj = DjangoFile(open(filename, 'rb'), name='fontello-b504201f.zip')
        owner = UserFactory(is_active=True, is_staff=True)
        filer_fileobj = FilerFileModel.objects.create(
            owner=owner,
            original_filename=fileobj.name,
            file=fileobj,
        )
        return filer_fileobj


@pytest.fixture
@pytest.mark.django_db
def icon_font(admin_client, icon_file_factory):
    icon_file = icon_file_factory()
    data = {
        'identifier': "Fontellico",
        'zip_file': icon_file.id,
        'is_default': 'on',
        '_continue': "Save and continue editing",
    }
    add_iconfont_url = reverse('admin:cmsplugin_cascade_iconfont_add')
    response = admin_client.post(add_iconfont_url, data)
    assert response.status_code == 302
    resolver_match = resolve(response.url)
    assert resolver_match.url_name == 'cmsplugin_cascade_iconfont_change'

    # check the content of the uploaded file
    if DJANGO_VERSION >= (2, 0):
        icon_font = IconFont.objects.get(pk=resolver_match.kwargs['object_id'])
    else:
        icon_font = IconFont.objects.get(pk=resolver_match.args[0])
    assert icon_font.identifier == "Fontellico"
    assert icon_font.config_data['name'] == 'fontelico'
    assert len(icon_font.config_data['glyphs']) == 34
    return icon_font


@pytest.mark.django_db
def test_iconfont_change_view(admin_client, icon_font):
    # check if the uploaded fonts are rendered inside Preview Icons
    change_url = reverse('admin:cmsplugin_cascade_iconfont_change', args=[icon_font.id])
    response = admin_client.get(change_url)
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, 'lxml')
    css_prefix = soup.find('div', class_='field-css_prefix').find('div', class_='readonly')
    assert css_prefix.text == 'icon-'
    preview_iconfont = soup.find('div', class_='preview-iconfont')
    icon_items = preview_iconfont.ul.find_all('li')
    assert len(icon_items) == 34
    assert icon_items[0].i.attrs['class'] == ['icon-emo-happy']
    assert icon_items[33].i.attrs['class'] == ['icon-marquee']


@pytest.fixture
@pytest.mark.django_db
def simple_icon(admin_site, cms_placeholder, icon_font):
    """Create and edit a SimpleIconPlugin"""
    class IconFontForm(IconFormMixin, LinkForm, ModelForm):
        class Meta(IconFormMixin.Meta):
            model = CascadeElement

    # add simple icon plugin
    simple_icon_model = add_plugin(cms_placeholder, SimpleIconPlugin, 'en')
    assert isinstance(simple_icon_model, CascadeElement)

    # edit simple icon plugin
    data = {'icon_font': str(icon_font.id), 'symbol': 'icon-skiing',
            'link_type': 'exturl', 'ext_url': 'http://test.ru/test', 'link_target': '_blank', 'link_title': 'test title'}
    form = IconFontForm(data=data, instance=simple_icon_model)
    assert form.is_valid()
    simple_icon_model = form.save()
    assert simple_icon_model.glossary['icon_font']['model'] == 'cmsplugin_cascade.iconfont'
    assert simple_icon_model.glossary['symbol'] == 'icon-skiing'
    simple_icon_plugin = simple_icon_model.get_plugin_class_instance(admin_site)
    assert isinstance(simple_icon_plugin, SimpleIconPlugin)
    return simple_icon_plugin, simple_icon_model


@pytest.mark.django_db
def test_simple_icon(rf, simple_icon):
    """Render a SimpleIconPlugin"""
    simple_icon_plugin, simple_icon_model = simple_icon
    request = rf.get('/')
    context = RequestContext(request)
    content_renderer = ContentRenderer(request)
    html = content_renderer.render_plugin(simple_icon_model, context).strip()
    assert html == '<a href="http://test.ru/test" title="test title" target="_blank"><i class="icon-icon-skiing"></i></a>'
