import logging
import os
from pathlib import Path
from urllib.parse import (
    ParseResult,
    urlparse
)

import boto3

from s3_log_shipper.parsers import ParserManager
from s3_log_shipper.s3_event_models import S3Event
from s3_log_shipper.shipper import RedisLogShipper

log: logging.Logger = logging.getLogger(__name__)


class LazyHandlerState:
    """
    Stateful component which lazily creates and caches the ParserManager to keep it in memory when the lambda is in a
    'warm' state, avoiding rereading of config files and reconstruction of parsers.
    """
    redis_endpoint: ParseResult
    log_parser: ParserManager
    shipper: RedisLogShipper

    def get_log_parser(self) -> ParserManager:

        if self.log_parser is None:
            parser_config_file = Path('./input_files.json')

            if not parser_config_file.exists() or not parser_config_file.is_file():
                msg = f'Expected to find parser config file at {parser_config_file.absolute()}. No such file found.'
                log.error(msg)
                raise Exception(msg)
            self.log_parser = ParserManager(config_file=parser_config_file)

        return self.log_parser

    @staticmethod
    def get_redis_endpoint() -> ParseResult:
        redis_endpoint_env_var_name = 'REDIS_ENDPOINT'

        try:
            redis_endpoint_str: str = os.environ[redis_endpoint_env_var_name]
        except Exception as e:
            msg = (
                'No non-empty Redis endpoint provided to which S3 logs should be shipped. '
                f'This should be provided as the environment variable [{redis_endpoint_env_var_name}]. '
                f'Details: [{e}].'
            )
            log.error(msg)
            raise Exception(msg)

        try:
            endpoint: ParseResult = urlparse(redis_endpoint_str)
        except Exception as e:
            msg = (
                f'Expected valid Redis endpoint url. Found: [{redis_endpoint_str}]. '
                f'Details: [{e}].'
            )
            log.error(msg)
            raise Exception(msg)

        return endpoint

    def get_shipper(self):
        if self.shipper is None:
            self.shipper = RedisLogShipper(self.get_redis_endpoint(), self.get_log_parser(), boto3.client("s3"))

        return self.shipper


state = LazyHandlerState()


def log_handler(event: dict, context) -> None:
    shipper = state.get_shipper()

    s3_event: S3Event = S3Event.from_dict(event)

    for record in s3_event.records:
        bucket = record.s3.bucket.name
        key = record.s3.object.key

        shipper.ship(bucket, key)
