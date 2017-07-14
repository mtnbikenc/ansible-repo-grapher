#!/usr/bin/env python
"""
Graph playbook and role dependencies for OpenShift Ansible

Usage:
./graph_playbook.py <path_to_playbook_file>
"""
from __future__ import print_function

import os
import subprocess
import uuid
import pygraphviz as pgv
import yaml

DISPLAY_ROLES = True
DISPLAY_ROLE_DEPS = False


def git_info(directory):
    """ Retrieves the commit date and commit description """

    git_date = subprocess.check_output(
        ['git', 'show', '-s', '--format=%ci'], cwd=directory).decode()
    git_date = str(git_date)[:10]
    git_describe = subprocess.check_output(
        ['git', 'describe', '--always'], cwd=directory).decode().rstrip('\n')

    return '{}-{}'.format(git_date, git_describe)


def add_subgraph(graph, playbook_name, subgraph_style=None):
    """Adds a formatted subgraph to a given graph based on the path of the
    folder provided.  Returns a copy of the subgraph."""
    if subgraph_style is None:
        subgraph_style = {
            'fontname': 'bold',
            'color': 'black',
            'style': 'filled',
            'fillcolor': 'lightgrey',
            'labeljust': 'l'
        }

    # Subgraph names begin with 'cluster_' to draw them as a boxed collection
    subgraph_name = 'cluster_{}'.format(playbook_name)
    subgraph_label = playbook_name

    subgraph = graph.add_subgraph(
        name=subgraph_name,
        label=subgraph_label,
        **subgraph_style)

    return subgraph


def add_roles(roles, subgraph, node_id, repo_root):
    """ Adds role nodes to a subgraph """
    role_node_style = {
        'color': 'blue'
    }

    role_edge_style = {
        'color': 'blue'
    }

    previous_role = None
    for role in roles:
        if 'role' in role:
            # Some 'roles:' include a 'role:' identifier
            role_name = role['role']
        else:
            role_name = role
        role_node_id = uuid.uuid4()
        role_node_label = 'role: {}'.format(role_name)
        subgraph.add_node(role_node_id, label=role_node_label, **role_node_style)

        if DISPLAY_ROLE_DEPS:
            add_role_dependency(subgraph, role_node_id, role_name, repo_root)

        if previous_role is None:
            subgraph.add_edge(node_id, role_node_id, **role_edge_style)
        else:
            subgraph.add_edge(previous_role, role_node_id, **role_edge_style)
        previous_role = role_node_id


def add_tasks(tasks, subgraph, graph, node_id, playbook, repo_root):
    """ Adds tasks nodes to a subgraph """
    task_node_style = {
        'color': 'orange'
    }

    task_edge_style = {
        'color': 'orange'
    }

    previous_task = None
    for task in tasks:
        if 'block' in task:
            block_node_id = uuid.uuid4()
            subgraph.add_node(block_node_id, label="block:", **task_node_style)
            if previous_task is None:
                previous_task = node_id
            subgraph.add_edge(previous_task, block_node_id, **task_edge_style)
            add_tasks(task['block'], subgraph, graph, block_node_id, playbook, repo_root)
            previous_task = block_node_id

        elif 'include_role' in task:
            if 'name' in task:
                task_name = task['name']
            else:
                task_name = '(Unnamed)'
            task_node_id = uuid.uuid4()
            task_node_label = 'include_role: {}'.format(task_name)
            subgraph.add_node(task_node_id, label=task_node_label, **task_node_style)
            add_roles([task['include_role']['name']], subgraph, task_node_id, repo_root)
            if previous_task is None:
                previous_task = node_id
            subgraph.add_edge(previous_task, task_node_id, **task_edge_style)
            previous_task = task_node_id

        elif 'include' in task:
            # Create the node
            task_node_id = uuid.uuid4()
            # We have to split here because sometimes the included file
            # also has string variables inline.  YAML please!
            if '{{' not in task['include']:
                included_file_name = task['include'].split()[0]
            else:
                included_file_name = task['include']
            task_node_label = 'include: {}'.format(included_file_name)
            subgraph.add_node(task_node_id, label=task_node_label, **task_node_style)

            # Add the link to the previous node
            if previous_task is None:
                previous_task = node_id
            subgraph.add_edge(previous_task, task_node_id, **task_edge_style)

            # If the include is a variable reference, don't process the file
            if '{{' in task['include']:
                previous_task = task_node_id
                continue

            # Create the full path to the included file
            included_file = os.path.normpath(
                os.path.join(os.path.dirname(playbook), included_file_name))
            # Create the 'short path' version of the included file
            playbook_name = included_file.replace(repo_root + '/', '')

            # Check to see if the subgraph exists
            playbook_graph = subgraph.get_subgraph('cluster_' + playbook_name)
            if playbook_graph is not None:
                # Subgraph for playbook exists so we just need to create an edge
                subgraph.add_edge(previous_task, playbook_graph.nodes()[0])
                return

            include_subgraph = add_subgraph(graph, playbook_name)

            with open(included_file, 'r') as yaml_file:
                included_tasks = yaml.safe_load(yaml_file.read())
                add_tasks(included_tasks, include_subgraph, graph, task_node_id, included_file, repo_root)

            previous_task = task_node_id

        else:
            if 'name' in task:
                task_name = task['name']
            else:
                # Since there is no name we punt and just grab the first key
                task_name = '(Unnamed) {}'.format(task.keys()[0])
            task_node_id = uuid.uuid4()
            task_node_label = 'task: {}'.format(task_name)
            subgraph.add_node(task_node_id, label=task_node_label, **task_node_style)
            if previous_task is None:
                previous_task = node_id
            subgraph.add_edge(previous_task, task_node_id, **task_edge_style)
            previous_task = task_node_id


# pylint: disable=too-many-arguments
def add_role_dependency(subgraph, role_node_id, role_name, repo_root,
                        role_level=0, first_dep=True):
    """ Adds role dependencies """
    # Increment role_level to show depth of dependencies
    role_level += 1

    dep_role_node_style = {
        'color': 'red'
    }

    # Colorize the first role dependency path different than secondary dependencies
    if first_dep:
        dep_role_edge_style = {
            'color': 'blue'
        }
    else:
        dep_role_edge_style = {
            'color': 'red'
        }

    # Check to see if meta/main.yml or meta/main.yaml exist
    role_meta = os.path.join(repo_root, 'roles', role_name, 'meta', 'main.yml')
    if not os.path.isfile(role_meta):
        role_meta = os.path.join(repo_root, 'roles', role_name, 'meta', 'main.yaml')
        if not os.path.isfile(role_meta):
            return

    with open(role_meta, 'r') as yaml_file:
        try:
            previous_node = role_node_id
            for dependency in yaml.load(yaml_file.read())['dependencies']:
                if 'role' in dependency:
                    # Some 'roles:' include a 'role:' identifier
                    dep_role_name = dependency['role']
                else:
                    dep_role_name = dependency

                dep_role_node_id = uuid.uuid4()
                dep_role_node_label = 'role_dep({}): {}'.format(role_level,
                                                                dep_role_name)
                subgraph.add_node(dep_role_node_id,
                                  label=dep_role_node_label,
                                  **dep_role_node_style)
                subgraph.add_edge(previous_node,
                                  dep_role_node_id,
                                  **dep_role_edge_style)

                add_role_dependency(subgraph, dep_role_node_id, dep_role_name,
                                    repo_root, role_level, first_dep=False)

                previous_node = dep_role_node_id

        except KeyError:
            pass


# pylint: disable=too-many-branches
def add_playbook(graph, playbook, repo_root, parent_node=None):
    """
    Scans a playbook file and
      - Add a subgraph for the playbook
      - Adds nodes to the subgraph for include statements
    """

    play_node_style = {
        'color': 'green'
    }

    playbook_name = playbook.replace(repo_root + '/', '')

    # Set alternate style of first subgraph, the entry-point playbook
    subgraph_style = None
    if graph.subgraphs().__len__() < 1:
        subgraph_style = {
            'fontname': 'bold',
            'color': 'black',
            'style': 'filled',
            'fillcolor': 'green',
            'labeljust': 'l'
        }

    playbook_graph = graph.get_subgraph('cluster_' + playbook_name)
    if playbook_graph is not None:
        # Subgraph for playbook exists so we just need to create an edge
        graph.add_edge(parent_node, playbook_graph.nodes()[0])
        return

    subgraph = add_subgraph(graph, playbook_name, subgraph_style)

    with open(playbook, 'r') as yaml_file:
        previous_task = None
        for task in yaml.safe_load(yaml_file.read()):
            if 'include' in task:
                node_id = uuid.uuid4()
                # We have to strip here because sometimes the included file
                # also has string variables inline.  YAML please!
                included_file_name = task['include'].split()[0]
                node_label = 'include: {}'.format(included_file_name)
                subgraph.add_node(node_id, label=node_label)

                included_file = os.path.normpath(
                    os.path.join(os.path.dirname(playbook), included_file_name))
                add_playbook(graph, included_file, repo_root, parent_node=node_id)

                if previous_task is None:
                    if parent_node is not None:
                        graph.add_edge(parent_node, node_id)
                else:
                    subgraph.add_edge(previous_task, node_id)
                previous_task = node_id

            if 'hosts' in task:
                node_id = uuid.uuid4()
                if 'name' in task:
                    task_name = task['name']
                else:
                    task_name = '(Unnamed)'
                node_label = 'Play: {}\n({})'.format(task_name, task['hosts'])
                subgraph.add_node(node_id, label=node_label, **play_node_style)
                previous_node_id = node_id

                if 'pre_tasks' in task and task['pre_tasks'] is not None:
                    # print('{} {}'.format(playbook, len(task['tasks'])))
                    tasks_node_id = uuid.uuid4()
                    tasks_node_label = 'pre_tasks: {}'.format(len(task['pre_tasks']))
                    subgraph.add_node(tasks_node_id, label=tasks_node_label)
                    subgraph.add_edge(previous_node_id, tasks_node_id)
                    add_tasks(task['pre_tasks'], subgraph, graph, tasks_node_id, playbook, repo_root)
                    previous_node_id = tasks_node_id

                if 'roles' in task:
                    if DISPLAY_ROLES or DISPLAY_ROLE_DEPS:
                        roles_node_id = uuid.uuid4()
                        roles_node_label = 'roles: {}'.format(len(task['roles']))
                        subgraph.add_node(roles_node_id, label=roles_node_label)
                        subgraph.add_edge(previous_node_id, roles_node_id)
                        add_roles(task['roles'], subgraph, roles_node_id, repo_root)
                        previous_node_id = roles_node_id

                if 'tasks' in task and task['tasks'] is not None:
                    # print('{} {}'.format(playbook, len(task['tasks'])))
                    tasks_node_id = uuid.uuid4()
                    tasks_node_label = 'tasks: {}'.format(len(task['tasks']))
                    subgraph.add_node(tasks_node_id, label=tasks_node_label)
                    subgraph.add_edge(previous_node_id, tasks_node_id)
                    add_tasks(task['tasks'], subgraph, graph, tasks_node_id, playbook, repo_root)
                    previous_node_id = tasks_node_id

                if 'post_tasks' in task and task['post_tasks'] is not None:
                    # print('{} {}'.format(playbook, len(task['tasks'])))
                    tasks_node_id = uuid.uuid4()
                    tasks_node_label = 'post_tasks: {}'.format(len(task['post_tasks']))
                    subgraph.add_node(tasks_node_id, label=tasks_node_label)
                    subgraph.add_edge(previous_node_id, tasks_node_id)
                    add_tasks(task['post_tasks'], subgraph, graph, tasks_node_id, playbook, repo_root)

                if previous_task is None:
                    if parent_node is not None:
                        graph.add_edge(parent_node, node_id)
                else:
                    subgraph.add_edge(previous_task, node_id)
                previous_task = node_id


def main(playbook):
    """
    Creates the main graph, subgraphs, nodes and edges (links)

    :param playbook: The name of the playbook.
    :type playbook: str
    """
    playbook_dir = os.path.dirname(playbook)
    playbook_file = os.path.basename(playbook)
    repo_root = subprocess.check_output(
        ['git', 'rev-parse', '--show-toplevel'], cwd=playbook_dir).decode().rstrip('\n')
    repo_name = os.path.split(repo_root)[-1]

    git_checkout = git_info(playbook_dir)

    root_graph_label = '{} ({})'.format(repo_name, git_checkout)
    root_graph = pgv.AGraph(
        strict=True,
        directed=True,
        concentrate=False,
        rankdir='TB',
        label=root_graph_label,
        labelloc='t',
        fontname='bold',
        # ranksep='2.0',
        size="300,300",
        dpi="96",
    )

    # Default node style
    root_graph.node_attr.update(
        shape='box',
        style='rounded, filled',
        color='black',
        fillcolor='white'
    )

    add_playbook(root_graph, playbook, repo_root)

    print('Number of nodes: {}'.format(root_graph.number_of_nodes()))

    filename = '{}-{}_{}'.format(git_checkout,
                                 os.path.split(playbook_dir)[-1],
                                 playbook_file)
    root_graph.write('{}.dot'.format(filename))
    print('Generated: {}.dot'.format(filename))
    root_graph.draw('{}.png'.format(filename), prog='dot')
    print('Generated: {}.png'.format(filename))


if __name__ == '__main__':
    import sys

    main(sys.argv[1])
