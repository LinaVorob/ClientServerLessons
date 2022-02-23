import time
import unittest
from util import CONFIG
from server import handle_response, forming_msg


class ServerTestCase(unittest.TestCase):
    client_response = b'{"action": "presence", "time": "Sun Jan  2 14:54:48 2022", "type": "status", ' \
                      b'"user": {"account_name": "account_name", "status": "I am here!"}}'

    def setUp(self) -> None:
        self.response = handle_response(self.client_response, CONFIG["ENCODING"])

    def test_handle_response(self):
        self.assertEqual(self.response, {"action": "presence", "time": "Sun Jan  2 14:54:48 2022", "type": "status",
                                    "user": {"account_name": "account_name", "status": "I am here!"}})

    def test_handle_response_type(self):
        self.assertEqual(type(self.response), dict)

    def test_forming_msg_access(self):
        self.assertEqual(forming_msg(self.response), {
            "response": 200,
            "time": time.ctime(time.time()),
            "alert": "Accept"
        })

    def test_answer_fail(self):
        self.assertEqual(forming_msg({'action': 'presence'}), {
            "response": 400,
            "error": 'Bad Request'
        })


if __name__ == '__main__':
    unittest.main()
