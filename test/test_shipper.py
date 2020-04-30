import io
import unittest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import boto3
from botocore.response import StreamingBody
from botocore.stub import Stubber, ANY

from s3_log_shipper.parsers import ParserManager, Parser
from s3_log_shipper.shipper import RedisLogShipper


class RedisLogShipperSpec(unittest.TestCase):
    under_test: RedisLogShipper

    def setUp(self) -> None:
        self.parser_manager = Mock(ParserManager)
        client = boto3.client('s3')
        self.s3_client: Stubber = Stubber(client)
        self.under_test = RedisLogShipper("http://127.0.0.1:6379", self.parser_manager, self.s3_client.client)

    @patch('urllib.request.urlopen')
    def test_ship(self, mock_urlopen):
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = 'THANKS'
        cm.__enter__.return_value = cm
        mock_urlopen.return_value = cm

        parser = Mock(Parser)
        timestamp = datetime.now().isoformat()
        parser.parse_log.return_value = {"timestamp": timestamp, "message": "Hello", "level": "INFO"}

        self.parser_manager.get_parser.return_value = parser, {"cluster": "foo12345", "node": "abc1234"}
        self.s3_client.add_response(method="get_object",
                                    service_response={"Body": StreamingBody(io.BytesIO(b"HELLO"), 5)},
                                    expected_params={"Bucket": ANY, "Key": ANY})
        self.s3_client.activate()
        self.under_test.ship("foo", "bar.log")

        for call in mock_urlopen.call_args_list:
            req, = call[0]
            self.assertEqual(req.full_url, "http://127.0.0.1:6379")
            self.assertIn("application/json", req.headers.values())


if __name__ == '__main__':
    unittest.main()
