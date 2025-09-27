# -*- coding: utf-8 -*-

import typing as T
import dataclasses
import botocore.exceptions
from mypy_boto3_s3vectors.type_defs import VectorDataTypeDef

from pydantic import BaseModel, Field
from mypy_boto3_s3vectors.literals import DataTypeType, DistanceMetricType

import boto3_dataclass_s3vectors.type_defs
from boto3_dataclass_s3vectors import s3vectors_caster


if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3vectors import S3VectorsClient

    from .model import Model
    from .query import Expr, CompoundExpr


@dataclasses.dataclass(frozen=True)
class QueryVectorsOutput(boto3_dataclass_s3vectors.type_defs.QueryVectorsOutput):
    def iterate(self, model_class: T.Type["Model"]) -> list["Model"]:
        if self.boto3_raw_data.get("vectors", []):
            vectors = self.boto3_raw_data
            for vector in self.boto3_raw_data.get("vectors", []):
                key = vector.get("key")
                data_dict: T.Optional[VectorDataTypeDef] = vector.get("data")
                if data_dict is None:
                    continue
                if len(data_dict) != 1:
                    continue
                data = next(iter(data_dict.values()))
                metadata = vector.get("metadata", {})
                yield model_class(key=key, data=data, **metadata)

        else:
            return []



class Index(BaseModel):
    """
    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/create_vector_bucket.html
    """

    bucket_name: str = Field()
    index_name: str = Field()
    data_type: "DataTypeType" = Field()
    dimension: int = Field()
    distance_metric: "DistanceMetricType" = Field()

    def create(
        self,
        s3_vectors_client: "S3VectorsClient",
        # todo: add more parameters
    ) -> dict[str, T.Any] | None:
        try:
            return s3_vectors_client.create_index(
                vectorBucketName=self.bucket_name,
                # vectorBucketArn='string',
                indexName=self.index_name,
                dataType=self.data_type,
                dimension=self.dimension,
                distanceMetric=self.distance_metric,
                # metadataConfiguration=metadataConfiguration,
            )

        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ConflictException":
                return None
            raise

    def put_vectors(
        self,
        s3_vectors_client: "S3VectorsClient",
        vectors: list["Model"],
    ):
        """
        Ref:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/put_vectors.html
        """
        s3_vectors_client.put_vectors(
            vectorBucketName=self.bucket_name,
            indexName=self.index_name,
            vectors=[
                vector.to_vector_dict(data_type=self.data_type) for vector in vectors
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
        return s3vectors_caster.query_vectors(res)
