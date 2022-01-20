import unittest

from util import parser_argument


class UtilTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.arg = parser_argument()

    def test_parse_argument_default(self):
        self.assertEqual(self.arg, {'addr': '127.0.0.1', 'port': 7777})

    def test_parse_argument_client_without_port_and_ip(self):
        self.assertRaises(AttributeError, parser_argument, server=False)


if __name__ == '__main__':
    unittest.main()
