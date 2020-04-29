import gzip

import boto3
from botocore.client import BaseClient
from botocore.response import StreamingBody

from s3_log_shipper.s3_event_models import S3Event


def write_to_redis(json: dict) -> None:
    # TODO: Write JSON to redis
    pass


def parse_log_line(log_line: str) -> dict:
    # TODO: Parse log line and convert to JSON
    pass


def log_handler(event: dict, context) -> None:
    s3_client: BaseClient = boto3.client('s3')
    s3_event: S3Event = S3Event.from_dict(event)

    for record in s3_event.records:
        bucket: str = record.s3.bucket.name
        key: str = record.s3.object.key

        get_object_response: dict = s3_client.get_object(Bucket=bucket, Key=key)

        if 'Body' not in get_object_response:
            raise Exception(f'Expected valid S3 get object response. Found: [{get_object_response}].')

        streaming_body: StreamingBody = get_object_response['Body']

        for log in gzip.GzipFile(streaming_body, mode='rb'):
            json_log: dict = parse_log_line(log)
            write_to_redis(json_log)
