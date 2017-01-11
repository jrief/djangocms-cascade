import cStringIO

from django.test import TestCase
from django.core.management import call_command


class MissingMigrationTest(TestCase):

    def test_for_missing_migrations(self):
        out = cStringIO.StringIO()

        call_command('makemigrations', '--dry-run',
                     verbocity=3, interactive=False, stdout=out)
        self.assertEquals(out.getvalue(), 'No changes detected\n')
