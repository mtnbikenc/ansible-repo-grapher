# ansible-repo-grapher
Use Python and Graphviz to diagram Ansible playbook and role dependencies

This tool was originally developed to visualize the [openshift-ansible] repo.

# Requirements

- git binary in $PATH
- PyYAML
- pygraphviz
- click

## Usage:

### Source
Clone this repo and the [openshift-ansible] repo

    .
    ├── ansible-repo-grapher
    └── openshift-ansible

From the root of ansible-repo-grapher run:

    python ./src/ansible_repo_grapher/graph_folder.py

### Install

- Clone this repo
- ``python setup.py install``
- Move to the root of a ansible directory
- Execute ``ansible-repo-grapher`` with options


[openshift-ansible]: https://github.com/openshift/openshift-ansible
