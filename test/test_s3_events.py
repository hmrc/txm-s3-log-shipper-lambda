from typing import List
from unittest import TestCase

from s3_log_shipper.s3_event_models import (
    Record,
    S3Event
)


class S3EventsSpec(TestCase):

    def test_event_parsed_with_bucket_and_key(self) -> None:
        expected_bucket: str = 'foo-bucket-name'
        expected_key: str = 'bar-logs/ABC/DEF/baz-type-log/xyzzy.gz'

        event: dict = {
          'Records': [
            {
              'eventVersion': '2.1',
              'eventSource': 'aws:s3',
              'awsRegion': 'eu-west-2',
              'eventTime': '1234-05-06T07:08:09.010Z',
              'eventName': 'ObjectCreated:Put',
              'userIdentity': {
                'principalId': 'AWS:69WC5ZYB3JRQWER7E5MD6:user.name'
              },
              'requestParameters': {
                'sourceIPAddress': '11.22.345.67'
              },
              'responseElements': {
                'x-amz-request-id': '3BFA478D1F79FC89',
                'x-amz-id-2': 'B87WDCU2B88826AUXEP2QR8NQRP5VUXPC/jYckN7BnMC3XBAGMTN3Un9zW2kBY9DEn2SBnvvR3ATtrzDdXe2MMY8FpVnhJHe'
              },
              's3': {
                's3SchemaVersion': '1.0',
                'configurationId': 'foo-lambda-name',
                'bucket': {
                  'name': expected_bucket,
                  'ownerIdentity': {
                    'principalId': 'A1Y696YRRRRDD1'
                  },
                  'arn': f'arn:aws:s3:::{expected_bucket}'
                },
                'object': {
                  'key': expected_key,
                  'size': 10,
                  'eTag': '7e84df40f3510292a01311157c2d4234',
                  'sequencer': '005FA341389GA752AA'
                }
              }
            }
          ]
        }

        s3_event: S3Event = S3Event.from_dict(event)
        s3_event_records: List[Record] = s3_event.records

        s3_event_record_count: int = len(s3_event_records)
        expected_record_count: int = 1

        self.assertEqual(
            first=s3_event_record_count,
            second=expected_record_count,
            msg=f'Expected event to contain exactly {expected_record_count} record(s). Found: {s3_event_record_count}.'
        )

        if s3_event_records:
            head_record: Record = s3_event_records[0]

            self.assertEqual(
                first=head_record.s3.bucket.name,
                second=expected_bucket
            )

            self.assertEqual(
                first=head_record.s3.object.key,
                second=expected_key
            )
