# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dynamoclasses',
    version='1.0.0a1',
    description='DynamoDB ORM using dataclasses',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ewdurbin/dynamoclasses',
    author='Ernest W. Durbin III',
    author_email='ewdurbin@gmail.com',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='dataclasses dynamodb',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=['boto3', 'dataclasses'],

    extras_require={
        'test': ['moto'],
    },

    package_data={},
    data_files=[],
    entry_points={},

    project_urls={
        'Bug Reports': 'https://github.com/ewdurbin/dynamoclasses/issues',
        'Source': 'https://github.com/ewdurbin/dynamoclasses/',
    },
)
