# -*- coding: utf-8 -*-
#
# Copyright 2018 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
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
"""Track provenance of data created by executing programs."""

import os
from subprocess import call

import click
from werkzeug.utils import secure_filename

from renga.models.cwl.command_line_tool import CommandLineToolFactory

from ._git import _mapped_std_streams, with_git
from ._repo import pass_repo


@click.command(context_settings=dict(ignore_unknown_options=True, ))
@click.argument('command_line', nargs=-1, type=click.UNPROCESSED)
@pass_repo
@with_git(clean=True, up_to_date=True, commit=True, ignore_std_streams=True)
def run(repo, command_line):
    """Activate environment for tracking work on a specific problem."""
    candidates = [x[0] for x in repo.git.index.entries] + \
        repo.git.untracked_files
    factory = CommandLineToolFactory(
        command_line=command_line,
        **_mapped_std_streams(candidates))

    with repo.with_workflow_storage() as wf:
        with factory.watch(repo.git) as tool:
            call(factory.command_line, cwd=os.getcwd())
            wf.add_step(run=tool)
