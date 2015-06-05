#!/usr/bin/env python
import os
from setuptools import setup, find_packages
from hadaly import meta

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='hadaly',
    version=meta.version,
    description=meta.description,
    packages=find_packages(),
    url='https://octogene.github.io/hadaly/',
    license=meta.license,
    author=meta.author,
    author_email=meta.author_email,
    requires=['lxml', 'Pillow', 'kivy'],
    long_description=read('README.md'),
    package_data={'hadaly': ['data/*.png',
                             'data/fonts/*.ttf',
                             'data/locales/fr/LC_MESSAGES/*.mo']},
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Natural Language :: French",
        "Topic :: Education",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    scripts = ['scripts/hadaly'],
    zip_safe = False,
)
