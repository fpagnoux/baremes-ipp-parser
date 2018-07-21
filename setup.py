#! /usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


setup(
    name='OpenFisca-Baremes-IPP',
    version='0.1.0',
    author='Institut des Politiques Publiques',
    author_email='florian.pagnoux@gmail.com',
    include_package_data = True,  # Will read MANIFEST.in
    install_requires=[
        'OpenFisca-Core >= 23.3, < 24.0',
        ],
    extras_require = {
        'api': [
            'OpenFisca-Web-API >= 4.0.0, < 7.0',
            ],
        'test': [
            'flake8 >= 3.4.0, < 3.5.0',
            'flake8-print',
            'nose',
            ]
        },
    packages=find_packages(),
    test_suite='nose.collector',
    )
