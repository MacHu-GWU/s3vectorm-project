# -*- coding: utf-8 -*-

import typing as T
from pydantic import BaseModel, Field

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3vectors.literals import DataTypeType
    from mypy_boto3_s3vectors.type_defs import PutInputVectorTypeDef


class Vector(BaseModel):
    """
    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/list_vectors.html
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/put_vectors.html
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/query_vectors.html
    """

    key: str = Field()
    data: list[float] = Field()
    distance: float | None = Field(default=None)

    def to_put_vectors_dct(
        self,
        data_type: "DataTypeType",
    ) -> "PutInputVectorTypeDef":
        dct = self.model_dump()
        return {
            "key": dct.pop("key"),
            "data": {
                data_type: dct.pop("data"),
            },
            "metadata": dct,
        }

    def to_metadata_dict(self):
        dct = self.model_dump()
        dct.pop("key")
        dct.pop("data")
        return dct
