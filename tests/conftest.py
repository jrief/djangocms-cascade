import pytest
from django.contrib import admin
from cms.api import create_page
from cmsplugin_cascade.models import CascadePage


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
