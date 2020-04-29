from moto import mock_s3
from unittest import TestCase
from unittest.mock import Mock

from handler import log_handler
from test.fixtures import stub_record


class LogHandlerSpec(TestCase):

    @mock_s3
    def test_log_handler_happy_path(self) -> None:
        event: dict = stub_record('foo-bucket', 'bar-logs/ABC/DEF/baz-type-log/xyzzy.gz')
        log_handler(event=event, context=Mock())
