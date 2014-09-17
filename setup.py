#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import tiling

package_name = 'tiling'

setup(name='python-tiling',
    version=tiling.__version__,
    description="Geographic tiling library for Python.",
    author='Seán Hayes',
    author_email='sean@seanhayes.name',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords='gis geo tiling bounding box',
    url='http://seanhayes.name/',
    download_url='https://github.com/SeanHayes/python-tiling',
    license='BSD',
    packages=[
        package_name,
    ],
    include_package_data=True,
    extras_require = {
        'decimal': ['dmath==0.9.1',],
    },
    dependency_links=['https://github.com/SeanHayes/dmath/archive/master.zip#egg=dmath-0.9.1'],
    test_suite = '%s.tests' % package_name,
)

