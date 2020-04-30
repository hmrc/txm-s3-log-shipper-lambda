import codecs
import gzip
import json
import logging

from botocore.client import BaseClient
from botocore.response import StreamingBody
from redis import StrictRedis

from s3_log_shipper.parsers import ParserManager

log: logging.Logger = logging.getLogger(__name__)


class RedisLogShipper:

    def __init__(self, redis_endpoint: StrictRedis, parser_manager: ParserManager, s3_client: BaseClient):
        self.redis_endpoint: StrictRedis = redis_endpoint
        self.parser_manager: ParserManager = parser_manager
        self.s3_client: BaseClient = s3_client

    def ship(self, bucket: str, key: str):
        parser, path_groks = self.parser_manager.get_parser(f"{bucket}/{key}")

        if parser is None:
            raise KeyError(f"No parser configured to handle logs from {key}")

        with self.open_file_stream(bucket, key) as log_file:
            for line in log_file:
                log_groks: dict = parser.parse_log(line)

                if path_groks is not None:
                    log_groks.update(path_groks)

                self.redis_endpoint.rpush("logstash", json.dumps(log_groks, sort_keys=True))

    def open_file_stream(self, bucket, key):
        get_object_response = self.s3_client.get_object(Bucket=bucket, Key=key)

        is_gzipped = key.endswith(".gz")

        if 'Body' not in get_object_response:
            msg = f'Expected valid S3 get object response. Found: [{get_object_response}].'
            log.error(msg)
            raise Exception(msg)

        streaming_body: StreamingBody = get_object_response['Body']

        return gzip.open(streaming_body, 'rt', encoding='utf-8') if is_gzipped else codecs.getreader('utf-8')(streaming_body)
