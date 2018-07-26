from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='endorser',
    version='0.13',
    description='Annotation based python object validator',
    long_description=long_description,
    long_description_content_type="text/markdown",
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
