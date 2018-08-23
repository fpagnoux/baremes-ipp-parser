#! /usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


setup(
    name='IPP-Baremes-Parser',
    version='0.1.0',
    author='Institut des Politiques Publiques',
    author_email='florian.pagnoux@gmail.com',
    include_package_data = True,  # Will read MANIFEST.in
    install_requires=[],
    packages=find_packages(),
    test_suite='nose.collector',
    )
