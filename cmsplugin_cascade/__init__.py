"""
See PEP 386 (https://www.python.org/dev/peps/pep-0386/)

Release logic:
 1. Remove ".devX" from __version__ (below)
 2. Remove ".devX" latest version in docs/source/changelog.rst
 3. git add cmsplugin_cascade/__init__.py docs/source/changelog.rst
 4. git commit -m 'Bump to <version>'
 5. git tag <version>
 6. git push
 7. assure that all tests pass on https://github.com/jrief/django-formset/actions/workflows/tests.yml
 8. git push --tags
 9. assure that a new version is published on https://github.com/jrief/django-formset/actions/workflows/publish.yml
10. bump the version, append ".dev0" to __version__
11. Add a new heading to docs/source/changelog.rst, named "<next-version>.dev0"
12. git add cmsplugin_cascade/__init__.py docs/source/changelog.rst
13. git commit -m 'Start with <version>'
14. git push
"""
__version__ = "2.3.4"

default_app_config = 'cmsplugin_cascade.apps.CascadeConfig'
