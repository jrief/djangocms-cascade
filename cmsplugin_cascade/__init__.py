"""
See PEP 386 (https://www.python.org/dev/peps/pep-0386/)

Release logic:
 1. Remove ".devX" from __version__ (below)
 2. Remove ".devX" latest version in docs/source/changelog.rst
 3. git add cmsplugin_cascade/__init__.py docs/source/changelog.rst
 4. git commit -m 'Bump to <version>'
 5. git tag <version>
 6. git push
 7. assure that all tests pass on https://travis-ci.org/jrief/djangocms-cascade
 8. git push --tags
 9. rm -rf dist
10. python setup.py sdist
11. twine upload dist/*
12. bump the version, append ".dev0" to __version__
13. Add a new heading to docs/source/changelog.rst, named "<next-version>.dev0"
14. git add cmsplugin_cascade/__init__.py docs/source/changelog.rst
15. git commit -m 'Start with <version>'
16. git push
"""
__version__ = "2.0.6"

default_app_config = 'cmsplugin_cascade.apps.CascadeConfig'
