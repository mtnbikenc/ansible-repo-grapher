#!/usr/bin/env python

import os
import shutil

from setuptools import setup

BINS = [
    'graph_folder',
    'graph_playbook',
]
NICE_BINS = []

# Make the nice names for bins
os.mkdir('./bins/')
for bin in BINS:
    nice_name = 'bins/ansible-{}'.format(bin.replace('_', '-'))
    shutil.copyfile('{}.py'.format(bin), nice_name)
    NICE_BINS.append(nice_name)

EXIT = SystemExit(0)

try:
    setup(
        name='ansible_repo_grapher',
        version='0.0.1',
        description=(
            'Use Graphviz to diagram Ansible playbook/role dependencies'),
        author='Russell Teague',
        url='https://github.com/mtnbikenc/ansible-repo-grapher',
        license="ASLv2",

        install_requires=[
            'pygraphviz',
            'PyYAML',
        ],
        scripts=NICE_BINS,
        classifiers=[
            'Topic :: Utilities',
            'License :: OSI Approved :: Apache Software License',
        ]
    )
except SystemExit as error:
    EXIT = error
finally:
    # Clean up
    shutil.rmtree('./bins/', ignore_errors=True)

raise EXIT
