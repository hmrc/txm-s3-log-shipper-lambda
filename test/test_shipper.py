import io
import json
import unittest
from datetime import datetime
from unittest.mock import Mock

import boto3
from botocore.response import StreamingBody
from botocore.stub import Stubber, ANY
from redis import StrictRedis

from s3_log_shipper.parsers import ParserManager, Parser
from s3_log_shipper.shipper import RedisLogShipper


class RedisLogShipperSpec(unittest.TestCase):
    under_test: RedisLogShipper

    def setUp(self) -> None:
        self.parser_manager = Mock(ParserManager)
        client = boto3.client('s3')
        self.s3_client: Stubber = Stubber(client)
        self.redis_client = Mock(StrictRedis)
        self.under_test = RedisLogShipper(self.redis_client, self.parser_manager, self.s3_client.client)

    def test_ship(self):
        parser = Mock(Parser)
        timestamp = datetime.now().isoformat()

        path_groks = {"timestamp": timestamp, "message": "Hello", "level": "INFO"}
        log_groks = {"cluster": "foo12345", "node": "abc1234"}

        parser.parse_log.return_value = path_groks
        self.parser_manager.get_parser.return_value = parser, log_groks
        self.s3_client.add_response(method="get_object",
                                    service_response={"Body": StreamingBody(io.BytesIO(b"HELLO"), 5)},
                                    expected_params={"Bucket": ANY, "Key": ANY})
        self.s3_client.activate()
        self.under_test.ship("foo", "bar.log")

        expected = log_groks.copy()
        expected.update(path_groks)

        for call in self.redis_client.rpush.call_args_list:
            q, data = call[0]
            self.assertEqual(q, "logstash")
            self.assertEqual(json.loads(data), expected)


if __name__ == '__main__':
    unittest.main()
