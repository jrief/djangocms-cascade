#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
from cmsplugin_bootstrap import __version__


INSTALL_REQUIRES = [

]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
]

setup(
    name='djangocms-bootstrap',
    version=__version__,
    description='Collection of plugins for DjangoCMS',
    author='Jacob Rief',
    author_email='jacob.rief@gmail.com',
    url='https://github.com/jrief/djangocms-bootstrap',
    packages=['cmsplugin_bootstrap', 'cmsplugin_bootstrap.migrations'],
    install_requires=INSTALL_REQUIRES,
    license='LICENSE-MIT',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    long_description=open('README.md').read(),
    include_package_data=True,
    zip_safe=False
)
