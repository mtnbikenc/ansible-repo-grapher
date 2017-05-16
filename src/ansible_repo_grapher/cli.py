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
Command line code.
"""

import click


@click.command(
    short_help='Graphs a playbook',
    help='Graphs a playbook')
@click.argument('playbook-path', nargs=1)
def playbook(playbook_path):
    """
    Executes the playbook subcommand.

    :param playbook_path: Full path to the playbook
    :type playbook_path: str
    """
    from .graph_playbook import main as exe
    exe(playbook_path)


@click.command(
    short_help='Graphs a folder',
    help='Graphs a folder')
@click.argument('folder-path', nargs=1)
def folder(folder_path):
    """
    Executes the folder subcommand.
    """
    from .graph_folder import main as exe
    exe(folder_path)


def main():
    """Main entry point"""
    cli = click.Group(help='Diagram Ansible playbook and role dependencies')
    cli.add_command(playbook)
    cli.add_command(folder)
    cli()


if __name__ == '__main__':
    main()
