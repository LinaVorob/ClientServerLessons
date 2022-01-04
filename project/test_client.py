import json
import unittest

from client import handle_response
from util import CONFIG


class ClientTestCase(unittest.TestCase):
    server_response_accept = {
        "response": 200,
        "time": 'Sun Jan  2 14:54:48 2022',
        "alert": "Accept"
    }
    server_response_deny = {
        "response": 400,
        "error": 'Bad Request'
    }

    def setUp(self) -> None:
        self.response_accept = bytes(json.dumps(self.server_response_accept).encode(CONFIG["ENCODING"]))
        self.response_deny = bytes(json.dumps(self.server_response_deny).encode(CONFIG["ENCODING"]))

    def test_handle_response_accept(self):
        result = handle_response(self.response_accept, CONFIG["ENCODING"])
        self.assertEqual(result, f'Код ответа: 200.\nСообщение от сервера: Accept')

    def test_handle_response_deny(self):
        result = handle_response(self.response_deny, CONFIG["ENCODING"])
        self.assertEqual(result, f'Код ответа: 400.\nОшибка: Bad Request')

    def test_handle_response_type(self):
        result = handle_response(self.response_accept, CONFIG["ENCODING"])
        self.assertEqual(type(result), str)


if __name__ == '__main__':
    unittest.main()
