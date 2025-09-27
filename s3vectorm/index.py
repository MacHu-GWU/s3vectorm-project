# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import botocore.exceptions
from func_args.api import OPT, remove_optional
from pydantic import BaseModel, Field, ValidationError
from mypy_boto3_s3vectors.literals import DataTypeType, DistanceMetricType

import boto3_dataclass_s3vectors.type_defs


if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3vectors import S3VectorsClient
    from mypy_boto3_s3vectors.type_defs import MetadataConfigurationTypeDef

    from .vector import Vector
    from .metadata import Expr, CompoundExpr


@dataclasses.dataclass(frozen=True)
class QueryVectorsOutput(boto3_dataclass_s3vectors.type_defs.QueryVectorsOutput):
    data_type: "DataTypeType" = dataclasses.field()

    def to_vectors(
        self,
        vector_class: T.Type["Vector"],
    ) -> list["Vector"]:
        """
        Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/query_vectors.html
        """
        if self.boto3_raw_data.get("vectors", []):
            vectors = []
            for dct in self.boto3_raw_data.get("vectors", []):
                try:
                    vector = vector_class(
                        key=dct["key"],
                        data=dct.get("data", {}).get(self.data_type),
                        **dct.get("metadata", {}),
                        distance=dct.get("distance", None),
                    )
                    vectors.append(vector)
                except ValidationError as e:
                    for error in e.errors():
                        if error["type"] == "missing":
                            field_name = error["loc"][0]
                            if field_name not in ("key", "data", "distance"):
                                raise ValueError(
                                    f"Metadata field '{field_name}' is missing in the response,"
                                    f"you may need to set 'return_metadata = True' in query_vectors(...) method"
                                )
                    raise
            return vectors
        else:
            return []


class Index(BaseModel):
    """ """

    bucket_name: str = Field()
    index_name: str = Field()
    data_type: "DataTypeType" = Field()
    dimension: int = Field()
    distance_metric: "DistanceMetricType" = Field()

    def create(
        self,
        s3_vectors_client: "S3VectorsClient",
        vector_bucket_arn: str = OPT,
        metadata_configuration: "MetadataConfigurationTypeDef" = OPT,
    ) -> dict[str, T.Any] | None:
        """
        Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/create_index.html
        """
        try:
            kwargs = {
                "vectorBucketName": self.bucket_name,
                "vectorBucketArn": vector_bucket_arn,
                "metadataConfiguration": metadata_configuration,
            }
            kwargs = remove_optional(**kwargs)
            if "vectorBucketArn" in kwargs:
                kwargs.pop("vectorBucketName")
            return s3_vectors_client.create_index(
                indexName=self.index_name,
                dataType=self.data_type,
                dimension=self.dimension,
                distanceMetric=self.distance_metric,
                **kwargs,
            )

        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ConflictException":
                return None
            raise

    def put_vectors(
        self,
        s3_vectors_client: "S3VectorsClient",
        vectors: list["Vector"],
    ):
        """
        Ref:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/put_vectors.html
        """
        s3_vectors_client.put_vectors(
            vectorBucketName=self.bucket_name,
            indexName=self.index_name,
            vectors=[
                vector.to_put_vectors_dict(data_type=self.data_type)
                for vector in vectors
            ],
        )

    def query_vectors(
        self,
        s3_vectors_client: "S3VectorsClient",
        data: list[float],
        top_k: int = 10,
        filter: T.Optional[T.Union["Expr", "CompoundExpr"]] = None,
        return_metadata: bool = False,
        return_distance: bool = False,
    ):
        """
        Ref:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/query_vectors.html
        """
        if filter is None:
            kwargs = {}
        else:
            kwargs = {"filter": filter.to_doc()}
        res = s3_vectors_client.query_vectors(
            vectorBucketName=self.bucket_name,
            indexName=self.index_name,
            topK=top_k,
            queryVector={
                self.data_type: data,
            },
            returnMetadata=return_metadata,
            returnDistance=return_distance,
            **kwargs,
        )
        return QueryVectorsOutput(
            boto3_raw_data=res,
            data_type=self.data_type,
        )
