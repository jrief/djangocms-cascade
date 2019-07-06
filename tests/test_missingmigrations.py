try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import pytest
from django.core.management import call_command


@pytest.mark.django_db
def test_for_missing_migrations():
    out = StringIO()

    call_command('makemigrations', '--dry-run', 'cmsplugin_cascade', verbosity=3, interactive=False, stdout=out)
    assert out.getvalue() == "No changes detected in app 'cmsplugin_cascade'\n"
