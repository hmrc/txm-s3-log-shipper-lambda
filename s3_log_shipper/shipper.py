import codecs
import gzip
import json
import logging
import urllib
from contextlib import closing
from urllib.parse import ParseResult, urlparse

from botocore.client import BaseClient
from botocore.response import StreamingBody

from s3_log_shipper.parsers import ParserManager

log: logging.Logger = logging.getLogger(__name__)


class RedisLogShipper:

    def __init__(self, redis_endpoint: str, parser_manager: ParserManager, s3_client: BaseClient):
        self.redis_endpoint: ParseResult = urlparse(redis_endpoint)
        self.parser_manager: ParserManager = parser_manager
        self.s3_client: BaseClient = s3_client

    def ship(self, bucket: str, key: str):
        parser, path_groks = self.parser_manager.get_parser(key)

        if parser is None:
            raise KeyError(f"No parser configured to handle logs from {key}")

        with self.open_file_stream(bucket, key) as log_file:
            for line in log_file:
                log_groks: dict = parser.parse_log(line)

                if path_groks is not None:
                    log_groks.update(path_groks)

                self.ship_to_redis(log_groks)

    def open_file_stream(self, bucket, key):
        get_object_response = self.s3_client.get_object(Bucket=bucket, Key=key)

        is_gzipped = key.endswith(".gz")

        if 'Body' not in get_object_response:
            msg = f'Expected valid S3 get object response. Found: [{get_object_response}].'
            log.error(msg)
            raise Exception(msg)

        streaming_body: StreamingBody = get_object_response['Body']

        return gzip.open(streaming_body, 'rb') if is_gzipped else codecs.getreader('utf-8')(streaming_body)

    def ship_to_redis(self, data: dict) -> None:
        redis_url: str = self.redis_endpoint.geturl()

        request = urllib.request.Request(url=redis_url,
                          data=json.dumps(data).encode("utf-8"),
                          headers={'content-type': 'application/json'})

        log.debug(f'Sending logs to Redis endpoint at [{redis_url}].')

        try:
            with closing(urllib.request.urlopen(request)) as response:
                log.debug(f"Response: ", response.getcode())
        except Exception as e:
            msg = f'Failed to send logs to Redis. Details: [{e}].'
            log.error(msg)