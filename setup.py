#!/usr/bin/env python
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
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Framework :: Django :: 3.2',
    'Framework :: Django :: 4.0',
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
        'django>=3.2,<5',
        'django-classy-tags>=1.0',
        'django-cms>=3.10,<4',
        'django-entangled>=0.5.3',
        'djangocms-text-ckeditor>=4.0',
        'django-select2>=7.7',
        'requests',
    ],
    license='MIT',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    zip_safe=False,
)
