# -*- coding: utf-8 -*-

import typing as T
import botocore.exceptions
from pydantic import BaseModel, Field

from boto3_dataclass_s3vectors import s3vectors_caster

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3vectors import S3VectorsClient
    from boto3_dataclass_s3vectors.type_defs import CreateB


class Bucket(BaseModel):
    """
    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/create_vector_bucket.html
    """

    name: str = Field()

    def create(
        self,
        s3_vectors_client: "S3VectorsClient",
        # todo: add more parameters
    ) -> dict[str, T.Any] | None:
        try:
            return s3_vectors_client.create_vector_bucket(
                vectorBucketName=self.name,
                # encryptionConfiguration={...},
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ConflictException":
                return None
            raise
