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
            "OUTPUT_REDIS_HOST": "localhost",
            "OUTPUT_REDIS_PORT": "6579",
            "CONFIG_FILE": test_config_file(),
        },
    )
    @patch("redis.StrictRedis", autospec=True)
    def test_log_handler_happy_path(self, redis_client) -> None:
        fn = "emr-logs/j-2QN8WF3UJZKK3/node/i-0c08a7e99b9985c73/applications/oozie/oozie.log-2020-04-28-05.gz"
        log_str = "".join(
            [
                "2020-04-28 05:58:34,602  INFO StatusTransitService$StatusTransitRunnable:520 "
                "- SERVER[ip-10-202-31-224.eu-west-2.compute.internal] USER[-] GROUP[-] "
                "TOKEN[-] APP[-] JOB[-] ACTION[-] Released lock for ["
                "org.apache.oozie.service.StatusTransitService]"
            ]
        )
        log = gzip.compress(log_str.encode("utf-8"))

        s3 = boto3.resource("s3")
        s3.create_bucket(Bucket="foo-bucket")
        s3.Object("foo-bucket", fn).put(Body=log)

        from handler import log_handler

        event: dict = stub_event("foo-bucket", fn)
        log_handler(event=event, context=Mock())

        expected = {
            "bucketname": "foo-bucket",
            "cluster": "j-2QN8WF3UJZKK3",
            "node": "i-0c08a7e99b9985c73",
            "type": "oozie",
            "level": "INFO",
            "message": log_str.split("INFO ")[1],
            "@timestamp": "2020-04-28T05:58:34.602000",
        }

        od = json.dumps(expected, sort_keys=True)
        redis_client().rpush.assert_called_with("logstash", od)
