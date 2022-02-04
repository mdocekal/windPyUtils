# -*- coding: UTF-8 -*-
""""
Created on 23.12.19

:author:     Martin Dočekal
"""
from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='windpyutils',
    version='1.2.4',
    description='Useful tools for Python projects.',
    long_description_content_type="text/markdown",
    long_description=README,
    license='The Unlicense',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    author='Martin Dočekal',
    keywords=['utils', 'general usage'],
    url='https://github.com/mdocekal/windPyUtils',
    python_requires='>=3.6',
    install_requires=[]
)

if __name__ == '__main__':
    setup(**setup_args)