#  This file is part of PyBuilder
#
#  Copyright 2011-2014 PyBuilder Team
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import unittest

from mock import patch, Mock, call

from pybuilder.core import Project
from pybuilder.plugins.python.cram_plugin import (
    _command,
    _find_files,
    _report_file,
    cram,
)


class CramPluginTests(unittest.TestCase):

    def test_command_respects_no_verbose(self):
        project = Project('.')
        project.set_property('verbose', False)
        expected = ['cram']
        received = _command(project)
        self.assertEquals(expected, received)

    def test_command_respects_verbose(self):
        project = Project('.')
        project.set_property('verbose', True)
        expected = ['cram', '--verbose']
        received = _command(project)
        self.assertEquals(expected, received)

    @patch('pybuilder.plugins.python.cram_plugin.discover_files_matching')
    def test_find_files(self, discover_mock):
        project = Project('.')
        project.set_property('dir_source_cmdlinetest', '/any/dir')
        expected = ['/any/dir/test.cram']
        discover_mock.return_value = expected
        received = _find_files(project)
        self.assertEquals(expected, received)
        discover_mock.assert_called_once_with('/any/dir', '*.cram')

    def test_report(self):
        project = Project('.')
        project.set_property('dir_reports', '/any/dir')
        expected = './any/dir/cram.err'
        received = _report_file(project)
        self.assertEquals(expected, received)

    @patch('pybuilder.plugins.python.cram_plugin._command')
    @patch('pybuilder.plugins.python.cram_plugin._find_files')
    @patch('pybuilder.plugins.python.cram_plugin._report_file')
    @patch('pybuilder.plugins.python.cram_plugin.read_file')
    @patch('pybuilder.plugins.python.cram_plugin.execute_command')
    def test_running_plugin(self,
                            execute_mock,
                            read_file_mock,
                            report_mock,
                            find_files_mock,
                            command_mock
                            ):
        project = Project('.')
        project.set_property('verbose', False)
        logger = Mock()

        command_mock.return_value = ['cram']
        find_files_mock.return_value = ['test1.cram', 'test2.cram']
        report_mock.return_value = 'report_file'
        read_file_mock.return_value = ['# results']
        execute_mock.return_value = 0

        cram(project, logger)
        execute_mock.assert_called_once_with(
            ['cram', 'test1.cram', 'test2.cram'], 'report_file')
        expected = [call('Running Cram tests'),
                    call('Cram tests were fine'),
                    call('results'),
                    ]
        self.assertEquals(expected, logger.info.call_args_list)
