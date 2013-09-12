from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(
	name='ckanext-intro',
	version=version,
	description="Quick introduction to writiing CKAN extensions",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Adri\xc3\xa0 Mercader',
	author_email='',
	url='http://ckan.org',
	license='GPL v3.0',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.intro'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
	# Add plugins here, eg
	intro_plugin=ckanext.intro.plugin:IntroExamplePlugin
	""",
)
