import csv
import gzip
import json
import os
from unittest import TestCase
from unittest.mock import Mock, patch

import boto3
from moto import mock_s3

from test.fixtures import stub_event, test_config_file


class LogHandlerSpec(TestCase):
    @mock_s3
    @patch.dict(
        os.environ,
        {
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6579",
            "CONFIG_FILE": test_config_file(),
        },
    )
    @patch("redis.StrictRedis", autospec=True)
    def test_log_handler_happy_path(self, redis_client) -> None:
        with open(
            f"{os.path.dirname(__file__)}/sample_logs.csv", "rt"
        ) as sample_logs_file:
            for line in csv.reader(sample_logs_file, delimiter="|"):
                path: str = line[0]
                log = line[1]
                expected = json.loads(line[2])

                log = gzip.compress(log.encode("utf-8"))

                first_slash = path.index("/")
                bucket = path[:first_slash]
                rest = 1 + first_slash
                path = path[rest:]

                s3 = boto3.resource("s3")
                s3.create_bucket(Bucket=bucket)
                s3.Object(bucket, path).put(Body=log)

                from handler import log_handler

                event: dict = stub_event(bucket, path)
                log_handler(event=event, context=Mock())

                od = json.dumps(expected, sort_keys=True)
                redis_client().rpush.assert_called_with("logstash", od)
