import logging
import os
from pathlib import Path
from urllib.parse import (
    ParseResult,
    urlparse
)

import boto3
import redis

from s3_log_shipper.parsers import ParserManager
from s3_log_shipper.s3_event_models import S3Event
from s3_log_shipper.shipper import RedisLogShipper

log: logging.Logger = logging.getLogger(__name__)


def get_log_parser() -> ParserManager:
    parser_config_file = Path('./input_files.json')

    if not parser_config_file.exists() or not parser_config_file.is_file():
        msg = f'Expected to find parser config file at {parser_config_file.absolute()}. No such file found.'
        log.error(msg)
        raise Exception(msg)

    return ParserManager(config_file=parser_config_file)


def get_output_redis_host_from_environment():
    try:
        return os.environ['OUTPUT_REDIS_HOST']
    except KeyError as e:
        raise Exception('env variable is not found: {}'.format(e))


def get_output_redis_port_from_environment():
    try:
        return os.environ['OUTPUT_REDIS_PORT']
    except KeyError as e:
        raise Exception('env variable is not found: {}'.format(e))


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


S3_CLIENT = boto3.client("s3")
PARSER_MANAGER = get_log_parser()
REDIS = redis.StrictRedis(host=get_output_redis_host_from_environment(),
                          port=int(get_output_redis_port_from_environment()),
                          db=0)
SHIPPER: RedisLogShipper = RedisLogShipper(REDIS, PARSER_MANAGER, S3_CLIENT)


def log_handler(event: dict, context) -> None:
    s3_event: S3Event = S3Event.from_dict(event)

    for record in s3_event.records:
        bucket = record.s3.bucket.name
        key = record.s3.object.key

        SHIPPER.ship(bucket, key)
