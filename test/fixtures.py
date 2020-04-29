def stub_event(bucket, key, record_count=1) -> dict:
    return {
        'Records': [
            stub_record(bucket, key) for x in range(0, record_count)
        ]
    }


def stub_record(bucket, key) -> dict:
    return {
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
                'name': bucket,
                'ownerIdentity': {
                    'principalId': 'A1Y696YRRRRDD1'
                },
                'arn': f'arn:aws:s3:::{bucket}'
            },
            'object': {
                'key': key,
                'size': 10,
                'eTag': '7e84df40f3510292a01311157c2d4234',
                'sequencer': '005FA341389GA752AA'
            }
        }
    }
