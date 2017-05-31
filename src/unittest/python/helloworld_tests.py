from mockito import mock, verify
import unittest

from helloworld import helloworld


class HelloWorldTest(unittest.TestCase):

    @staticmethod
    def test_should_issue_hello_world_message():
        out = mock()

        helloworld(out)

        verify(out).write("Hello world of Python\n")
