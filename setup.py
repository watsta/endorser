import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name='object_validator',
    version='0.12',
    description='Annotation based python object validator',
    long_description='Annotation based python object validator',
    classifiers=[
        'Programming Language :: Python',
    ],
    author='Krisztian Toth',
    author_email='tkrisztiana@gmail.com',
    url='',
    keywords='object validator validate converter convert',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
