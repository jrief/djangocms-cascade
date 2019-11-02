import factory.fuzzy
import pytest
from pytest_factoryboy import register
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
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


@register
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    @classmethod
    def create(cls, **kwargs):
        user = super().create(**kwargs)
        assert isinstance(user, get_user_model())
        assert user.is_authenticated == True
        return user

    username = factory.Sequence(lambda n: 'uid-{}'.format(n))
    password = make_password('secret')
    email = factory.fuzzy.FuzzyText(suffix='@example.com')
