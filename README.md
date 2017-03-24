# ansible-repo-grapher
Use Python and Graphviz to diagram Ansible playbook and role dependencies

This tool was originally developed to visualize the [openshift-ansible] repo.

## Usage:
Clone this repo and the [openshift-ansible] repo

    .
    ├── ansible-repo-grapher
    └── openshift-ansible

From the root of ansible-repo-grapher run:

    python ./graph_folder.py

[openshift-ansible]: https://github.com/openshift/openshift-ansible
