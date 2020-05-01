from typing import List
from unittest import TestCase

from s3_log_shipper.s3_event_models import Record, S3Event
from test.fixtures import stub_event


class S3EventsSpec(TestCase):
    def test_event_parsed_with_bucket_and_key(self) -> None:
        expected_bucket: str = "foo-bucket-name"
        expected_key: str = "bar-logs/ABC/DEF/baz-type-log/xyzzy.gz"

        event: dict = stub_event(expected_bucket, expected_key)
        s3_event: S3Event = S3Event.from_dict(event)
        s3_event_records: List[Record] = s3_event.records

        s3_event_record_count: int = len(s3_event_records)
        expected_record_count: int = 1

        self.assertEqual(
            first=s3_event_record_count,
            second=expected_record_count,
            msg=f"Expected event to contain exactly {expected_record_count} record(s). Found: {s3_event_record_count}.",
        )

        if s3_event_records:
            head_record: Record = s3_event_records[0]

            self.assertEqual(first=head_record.s3.bucket.name, second=expected_bucket)
            self.assertEqual(first=head_record.s3.object.key, second=expected_key)
