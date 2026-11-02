from enum import Enum


class StoreType(str, Enum):
    FILE = "file"
    S3 = "s3"
