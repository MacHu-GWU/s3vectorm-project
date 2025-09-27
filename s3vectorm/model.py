# -*- coding: utf-8 -*-

import typing as T
from pydantic import BaseModel, Field

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3vectors.literals import DataTypeType
    from mypy_boto3_s3vectors.type_defs import VectorDataTypeDef


class Model(BaseModel):
    """
    Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/put_vectors.html
    """

    key: str = Field()
    data: list[float] = Field()

    def to_vector_dict(
        self,
        data_type: "DataTypeType",
    ):
        metadata = self.model_dump()
        return {
            "key": metadata.pop("key"),
            "data": {
                data_type: metadata.pop("data"),
            },
            "metadata": metadata,
        }
