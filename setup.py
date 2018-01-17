#!/usr/bin/env python
from setuptools import setup, find_packages


packages_deps = ['numpy', 'scipy', 'pyyaml']

setup_args = dict(name='pyg2p',
                  version='2.1',
                  description="Convert a set of PCRaster files to a netCDF4 mapstack",
                  license="Open Source",
                  install_requires=packages_deps,
                  author="Domenico Nappo",
                  author_email="domenico.nappo@gmail.com",
                  packages=find_packages(),
                  keywords="netCDF4 PCRaster",
                  entry_points={'console_scripts': ['pcr2nc = pcr2nc_script:main_script']},
                  zip_safe=True)


setup(**setup_args)

