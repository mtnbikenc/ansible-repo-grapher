#!/usr/bin/env python
# Copyright 2016 Russell Teague
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Install script.
"""

from setuptools import setup, find_packages


setup(
    name='ansible_repo_grapher',
    version='0.0.2',
    description=(
        'Use Graphviz to diagram Ansible playbook/role dependencies'),
    author='Russell Teague',
    url='https://github.com/mtnbikenc/ansible-repo-grapher',
    license="ASLv2",
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'pygraphviz',
        'PyYAML',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'ansible-repo-grapher=ansible_repo_grapher.cli:main',
        ]
    },
    classifiers=[
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
    ]
)
