from hstest.stage_test import StageTest
from hstest.test_case import TestCase
from hstest.check_result import CheckResult

import os
import shutil

import sys
if sys.platform.startswith("win"):
    import _locale
    # pylint: disable=protected-access
    _locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])

CheckResult.correct = lambda: CheckResult(True, '')
CheckResult.wrong = lambda feedback: CheckResult(False, feedback)


class TextBasedBrowserTest(StageTest):

    def generate(self):
        return [
            TestCase(
                stdin='bloomberg.com\nbloomberg\nexit',
                attach=('Bloomberg', 'New York Times', 'bloomberg'),
                args=['tb_tabs']
            ),
            TestCase(
                stdin='nytimes.com\nnytimes\nexit',
                attach=('New York Times', 'Bloomberg', 'nytimes'),
                args=['tb_tabs']
            ),
            TestCase(
                stdin='nytimescom\nexit',
                args=['tb_tabs']
            ),
            TestCase(
                stdin='blooomberg.com\nexit',
                args=['tb_tabs']
            ),
            TestCase(
                stdin='blooomberg.com\nnytimes.com\nexit',
                attach=(None, 'New York Times', 'Bloomberg', 'nytimes'),
                args=['tb_tabs']
            ),
            TestCase(
                stdin='nytimescom\nbloomberg.com\nexit',
                attach=(None, 'Bloomberg', 'New York Times', 'bloomberg'),
                args=['tb_tabs']
            ),
        ]

    def _check_files(self, path_for_tabs: str, right_word: str) -> int:
        """
        Helper which checks that browser saves visited url in files and
        provides access to them.

        :param path_for_tabs: directory which must contain saved tabs
        :param right_word: Word-marker which must be in right tab
        :return: True, if right_words is present in saved tab
        """

        path, dirs, files = next(os.walk(path_for_tabs))

        for file in files:
            with open(os.path.join(path_for_tabs, file), 'r') as tab:
                try:
                    content = tab.read()
                except UnicodeDecodeError:
                    return -1
                if right_word in content:
                    return 1

        return 0

    def check(self, reply, attach):

        # Incorrect URL
        if attach is None:
            if 'error' in reply.lower():
                return CheckResult.correct()
            else:
                return CheckResult.wrong('There was no "error" word, but should be.')

        # Correct URL
        if isinstance(attach, tuple):

            if len(attach) == 4:
                _, *attach = attach
                if 'error' not in reply.lower():
                    return CheckResult.wrong('There was no "error" word, but should be.')

            right_word, wrong_word, correct_file_name = attach

            path_for_tabs = 'tb_tabs'

            if not os.path.isdir(path_for_tabs):
                return CheckResult.wrong(
                    "Can't find a directory \"" + path_for_tabs + "\" "
                    "in which you should save your web pages.")

            if not os.path.exists(os.path.join(path_for_tabs, correct_file_name)):
                return CheckResult.wrong(
                    "Seems like you did\'n save the web page "
                    "\"" + right_word + "\" into the "
                    "directory \"" + path_for_tabs + "\". "
                    "This file with page should be named \"" + correct_file_name + "\"")

            check_files_result = self._check_files(path_for_tabs, right_word)
            if not check_files_result:
                return CheckResult.wrong(
                    "Seems like the content of your saved file \"{0}\" is not what it's supposed to be. Perhaps it is empty or doesn't correspond to the name of the file?".format(correct_file_name))
            elif check_files_result == -1:
                return CheckResult.wrong('An error occurred while reading your saved tab. '
                                         'Perhaps you used the wrong encoding?')

            try:
                shutil.rmtree(path_for_tabs)
            except PermissionError:
                return CheckResult.wrong("Impossible to remove the directory for tabs. Perhaps you haven't closed some file?")

            if wrong_word in reply:
                return CheckResult.wrong('It seems like you printed wrong variable')

            if right_word in reply:
                return CheckResult.correct()

            return CheckResult.wrong('You printed neither bloomberg_com nor nytimes_com')


TextBasedBrowserTest('browser.browser').run_tests()