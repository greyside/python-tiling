#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import bounding_boxes

package_name = 'bounding_boxes'

setup(name='bounding-boxes',
	version=bounding_boxes.__version__,
	description="Generates geographic bounding boxes, which can be useful for caching geospatial queries..",
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
	keywords='django configuration generator',
	url='http://seanhayes.name/',
	download_url='https://github.com/SeanHayes/bounding-boxes',
	license='BSD',
	packages=[
		package_name,
	],
	include_package_data=True,
	install_requires=['dmath',],
	test_suite = '%s.tests' % package_name,
)

