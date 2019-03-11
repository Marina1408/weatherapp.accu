from setuptools import setup, find_namespace_packages


setup(
	name="weatherapp.accu",
	version="0.1.0",
	author="Marina Popryzhuk",
	description="AccuWeather provider",
	packages=find_namespace_packages(),
	entry_points={
	    '': '',
	},
	install_requires=[
	   'bs4',
	]
)
