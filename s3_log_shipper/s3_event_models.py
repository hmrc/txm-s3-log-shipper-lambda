from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, TypeVar, Type, cast, Callable

import dateutil.parser

T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


@dataclass
class RequestParameters:
    source_ip_address: str

    @staticmethod
    def from_dict(obj: Any) -> "RequestParameters":
        assert isinstance(obj, dict)
        source_ip_address = from_str(obj.get("sourceIPAddress"))
        return RequestParameters(source_ip_address)

    def to_dict(self) -> dict:
        result: dict = {}
        result["sourceIPAddress"] = from_str(self.source_ip_address)
        return result


@dataclass
class ResponseElements:
    x_amz_request_id: str
    x_amz_id_2: str

    @staticmethod
    def from_dict(obj: Any) -> "ResponseElements":
        assert isinstance(obj, dict)
        x_amz_request_id = from_str(obj.get("x-amz-request-id"))
        x_amz_id_2 = from_str(obj.get("x-amz-id-2"))
        return ResponseElements(x_amz_request_id, x_amz_id_2)

    def to_dict(self) -> dict:
        result: dict = {}
        result["x-amz-request-id"] = from_str(self.x_amz_request_id)
        result["x-amz-id-2"] = from_str(self.x_amz_id_2)
        return result


@dataclass
class ErIdentity:
    principal_id: str

    @staticmethod
    def from_dict(obj: Any) -> "ErIdentity":
        assert isinstance(obj, dict)
        principal_id = from_str(obj.get("principalId"))
        return ErIdentity(principal_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["principalId"] = from_str(self.principal_id)
        return result


@dataclass
class Bucket:
    name: str
    owner_identity: ErIdentity
    arn: str

    @staticmethod
    def from_dict(obj: Any) -> "Bucket":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        owner_identity = ErIdentity.from_dict(obj.get("ownerIdentity"))
        arn = from_str(obj.get("arn"))
        return Bucket(name, owner_identity, arn)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["ownerIdentity"] = to_class(ErIdentity, self.owner_identity)
        result["arn"] = from_str(self.arn)
        return result


@dataclass
class Object:
    key: str
    size: int
    e_tag: str
    sequencer: str

    @staticmethod
    def from_dict(obj: Any) -> "Object":
        assert isinstance(obj, dict)
        key = from_str(obj.get("key"))
        size = from_int(obj.get("size"))
        e_tag = from_str(obj.get("eTag"))
        sequencer = from_str(obj.get("sequencer"))
        return Object(key, size, e_tag, sequencer)

    def to_dict(self) -> dict:
        result: dict = {}
        result["key"] = from_str(self.key)
        result["size"] = from_int(self.size)
        result["eTag"] = from_str(self.e_tag)
        result["sequencer"] = from_str(self.sequencer)
        return result


@dataclass
class S3:
    s3_schema_version: str
    configuration_id: str
    bucket: Bucket
    object: Object

    @staticmethod
    def from_dict(obj: Any) -> "S3":
        assert isinstance(obj, dict)
        s3_schema_version = from_str(obj.get("s3SchemaVersion"))
        configuration_id = from_str(obj.get("configurationId"))
        bucket = Bucket.from_dict(obj.get("bucket"))
        object = Object.from_dict(obj.get("object"))
        return S3(s3_schema_version, configuration_id, bucket, object)

    def to_dict(self) -> dict:
        result: dict = {}
        result["s3SchemaVersion"] = from_str(self.s3_schema_version)
        result["configurationId"] = from_str(self.configuration_id)
        result["bucket"] = to_class(Bucket, self.bucket)
        result["object"] = to_class(Object, self.object)
        return result


@dataclass
class Record:
    event_version: str
    event_source: str
    aws_region: str
    event_time: datetime
    event_name: str
    user_identity: ErIdentity
    request_parameters: RequestParameters
    response_elements: ResponseElements
    s3: S3

    @staticmethod
    def from_dict(obj: Any) -> "Record":
        assert isinstance(obj, dict)
        event_version = from_str(obj.get("eventVersion"))
        event_source = from_str(obj.get("eventSource"))
        aws_region = from_str(obj.get("awsRegion"))
        event_time = from_datetime(obj.get("eventTime"))
        event_name = from_str(obj.get("eventName"))
        user_identity = ErIdentity.from_dict(obj.get("userIdentity"))
        request_parameters = RequestParameters.from_dict(obj.get("requestParameters"))
        response_elements = ResponseElements.from_dict(obj.get("responseElements"))
        s3 = S3.from_dict(obj.get("s3"))
        return Record(
            event_version,
            event_source,
            aws_region,
            event_time,
            event_name,
            user_identity,
            request_parameters,
            response_elements,
            s3,
        )

    def to_dict(self) -> dict:
        result: dict = {}
        result["eventVersion"] = from_str(self.event_version)
        result["eventSource"] = from_str(self.event_source)
        result["awsRegion"] = from_str(self.aws_region)
        result["eventTime"] = self.event_time.isoformat()
        result["eventName"] = from_str(self.event_name)
        result["userIdentity"] = to_class(ErIdentity, self.user_identity)
        result["requestParameters"] = to_class(
            RequestParameters, self.request_parameters
        )
        result["responseElements"] = to_class(ResponseElements, self.response_elements)
        result["s3"] = to_class(S3, self.s3)
        return result


@dataclass
class S3Event:
    records: List[Record]

    @staticmethod
    def from_dict(obj: Any) -> "S3Event":
        assert isinstance(obj, dict)
        records = from_list(Record.from_dict, obj.get("Records"))
        return S3Event(records)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Records"] = from_list(lambda x: to_class(Record, x), self.records)
        return result


def s3_event_from_dict(s: Any) -> S3Event:
    return S3Event.from_dict(s)


def s3_event_to_dict(x: S3Event) -> Any:
    return to_class(S3Event, x)
