#!/usr/bin/env python

#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#
__author__ = "Qualthera"

from setuptools import (setup, find_packages)

setup(
    name="xzitaao",
    version="0.0.4",
    description="Crawler for xzit aao",
    author='Qualthera',
    author_email='qualthera@163.com',
    mainitainer='HowieHye',
    mainitainer_email='howiehye@163.com',
    url='https://github.com/Qualthera/xzitaao.git',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    platforms=["all"],
    license="Apache License 2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"],
    install_requires=[
        'beautifulsoup4 == 4.9.3',
        'bs4 == 0.0.1',
        'certifi == 2020.12.5',
        'chardet == 3.0.4',
        'cycler == 0.10.0',
        'idna == 2.10',
        'kiwisolver == 1.3.1',
        'lxml == 4.6.2',
        'numpy == 1.19.3',
        'Pillow == 8.0.1',
        'pyparsing == 2.4.7',
        'python-dateutil == 2.8.1',
        'requests == 2.25.0',
        'six == 1.15.0',
        'soupsieve == 2.1',
        'urllib3 == 1.26.2',
        'pytesseract==0.3.6',

    ],
    packages=find_packages()
)
