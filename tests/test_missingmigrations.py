try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from django.test import TestCase
from django.core.management import call_command


class MissingMigrationTest(TestCase):

    def test_for_missing_migrations(self):
        out = StringIO()

        call_command('makemigrations', '--dry-run', 'cmsplugin_cascade',
                     verbosity=3, interactive=False, stdout=out)
        self.assertEqual(out.getvalue(), "No changes detected in app 'cmsplugin_cascade'\n")
