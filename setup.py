#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from setuptools import setup, find_packages
from cmsplugin_cascade import __version__

with open('README.md', 'r') as fh:
    long_description = fh.read()

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Framework :: Django :: 1.11',
]

setup(
    name='djangocms-cascade',
    version=__version__,
    description='Build Single Page Applications using the Django-CMS plugin system',
    author='Jacob Rief',
    author_email='jacob.rief@gmail.com',
    url='https://github.com/jrief/djangocms-cascade',
    packages=find_packages(exclude=['examples', 'docs', 'tests']),
    install_requires=[
        'django>=1.11,<2.0',
        'django-classy-tags>=0.8',
        'django-cms>=3.4,<3.6',
        'djangocms-text-ckeditor>=3.4',
        'jsonfield',
    ],
    license='MIT',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    zip_safe=False,
)
