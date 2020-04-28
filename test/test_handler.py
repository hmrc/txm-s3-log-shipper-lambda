from moto import mock_s3
from unittest import TestCase
from unittest.mock import Mock

from handler import log_handler


class LogHandlerSpec(TestCase):

    @mock_s3
    def test_log_handler_happy_path(self) -> None:
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
                  'name': 'foo-bucket-name',
                  'ownerIdentity': {
                    'principalId': 'A1Y696YRRRRDD1'
                  },
                  'arn': 'arn:aws:s3:::foo-bucket-name'
                },
                'object': {
                  'key': 'bar-logs/ABC/DEF/baz-type-log/xyzzy.gz',
                  'size': 10,
                  'eTag': '7e84df40f3510292a01311157c2d4234',
                  'sequencer': '005FA341389GA752AA'
                }
              }
            }
          ]
        }

        log_handler(event=event, context=Mock())
