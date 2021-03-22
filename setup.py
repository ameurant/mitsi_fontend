# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '5.1.4 '

setup(
    name='mitsibox',
    version=version,
    description="Plone product for mitsibox website",
    long_description=open("README.rst").read(),
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 5.1.4 ",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    author='Netvaast',
    author_email='alain.meurant@netvaast.be',
    url='https://github.com/ameurant/mitsibox',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.api',
        'plone.app.dexterity',
        'setuptools',
        'z3c.jbot',
        'mysql-connector-python',
    ],
    entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
