import logging
import os
from pathlib import Path

import aws_lambda_logging
import boto3
import redis

from s3_log_shipper.parsers import ParserManager
from s3_log_shipper.s3_event_models import S3Event
from s3_log_shipper.shipper import RedisLogShipper

log: logging.Logger = logging.getLogger(__name__)


def get_parser_manager() -> ParserManager:
    return ParserManager(config_file=get_config_file())


def get_config_file() -> Path:
    default = f"{os.path.dirname(__file__)}/input_files.json"
    path = os.environ.get("CONFIG_FILE", default)
    file = Path(path)
    if not file.exists() or not file.is_file():
        msg = f"Expected to find parser config file at {file.absolute()}. No such file found."
        log.error(msg)
        raise Exception(msg)
    return file


def get_output_redis_host_from_environment():
    try:
        return os.environ["REDIS_HOST"]
    except KeyError as e:
        raise Exception("env variable is not found: {}".format(e))


def get_output_redis_port_from_environment():
    try:
        return os.environ["REDIS_PORT"]
    except KeyError as e:
        raise Exception("env variable is not found: {}".format(e))


S3_CLIENT = boto3.client("s3")
PARSER_MANAGER = get_parser_manager()
REDIS = redis.StrictRedis(
    host=get_output_redis_host_from_environment(),
    port=int(get_output_redis_port_from_environment()),
    db=0,
)
SHIPPER: RedisLogShipper = RedisLogShipper(REDIS, PARSER_MANAGER, S3_CLIENT)


def log_handler(event: dict, context) -> None:
    aws_lambda_logging.setup(level='DEBUG')
    log.info(event)
    s3_event: S3Event = S3Event.from_dict(event)

    for record in s3_event.records:
        bucket = record.s3.bucket.name
        key = record.s3.object.key

        log.info(f"Processing {bucket}/{key}")
        SHIPPER.ship(bucket, key)
