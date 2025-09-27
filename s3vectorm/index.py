# -*- coding: utf-8 -*-

"""
S3 Vector Index Management

This module provides functionality for managing S3 vector indexes, including
index creation, vector storage, and vector querying operations. It integrates
with AWS S3 Vectors service to provide a Pythonic interface for vector search
operations.

The module includes classes for:

- Index management and operations (:class:`Index`)
- Query result processing (:class:`QueryVectorsOutput`)

These classes handle the complexities of AWS S3 Vectors API interactions,
data format conversions, and error handling.
"""

import typing as T
import dataclasses

import botocore.exceptions
from func_args.api import OPT, remove_optional
from pydantic import BaseModel, Field, ValidationError
from mypy_boto3_s3vectors.literals import DataTypeType, DistanceMetricType
from boto3_dataclass_s3vectors import s3vectors_caster
import boto3_dataclass_s3vectors.type_defs


if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3vectors import S3VectorsClient
    from mypy_boto3_s3vectors.type_defs import MetadataConfigurationTypeDef

    from .vector import Vector
    from .metadata import Expr, CompoundExpr

# TypeVar for preserving Vector subclass types
VectorT = T.TypeVar("VectorT", bound="Vector")


@dataclasses.dataclass(frozen=True)
class VectorsOutputMixin:
    """
    Mixin providing common functionality for vector operation outputs.

    This mixin provides functionality for converting raw AWS S3 Vectors responses
    into Vector objects. It is used by both QueryVectorsOutput and ListVectorsOutput
    to provide consistent vector conversion capabilities.

    :param data_type: The data type of the vectors in the response
    :param boto3_raw_data: The raw response data from AWS (inherited)

    Example:
        >>> output = QueryVectorsOutput(
        ...     boto3_raw_data=s3vectors_client_query_vectors_response,
        ...     data_type="float32"
        ... )
        >>> vectors = output.as_vector_objects(Vector)
    """

    data_type: "DataTypeType" = dataclasses.field()

    def as_vector_objects(
        self,
        vector_class: T.Type[VectorT],
    ) -> list[VectorT]:
        """
        Convert query results into Vector objects.

        This method transforms the raw AWS query response into a list of Vector
        objects, handling data type conversion, metadata extraction, and validation
        errors. It provides helpful error messages for common issues like missing
        metadata fields.

        :param vector_class: The Vector class to use for creating vector objects

        :returns: A list of Vector objects created from the query results.
            Returns an empty list if no vectors were found.

        Raises:
            ValidationError: If vector creation fails due to missing required fields
            ValueError: If metadata fields are missing from the response, with
                guidance on enabling metadata in the query

        Example:
            >>> output = QueryVectorsOutput(
            ...     boto3_raw_data={
            ...         "vectors": [
            ...             {
            ...                 "key": "doc1",
            ...                 "data": {"float32": [0.1, 0.2, 0.3]},
            ...                 "distance": 0.95,
            ...                 "metadata": {"category": "documents"}
            ...             }
            ...         ]
            ...     },
            ...     data_type="float32"
            ... )
            >>> vectors = output.to_vectors(Vector)
            >>> print(vectors[0].key)  # "doc1"

        Reference:
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/query_vectors.html
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


@dataclasses.dataclass(frozen=True)
class QueryVectorsOutput(
    boto3_dataclass_s3vectors.type_defs.QueryVectorsOutput,
    VectorsOutputMixin,
):
    """
    Query vectors operation output.

    .. seealso::

        :class:`VectorsOutputMixin`
    """


@dataclasses.dataclass(frozen=True)
class ListVectorsOutput(
    boto3_dataclass_s3vectors.type_defs.ListVectorsOutput,
    VectorsOutputMixin,
):
    """
    List vectors operation output.

    .. seealso::

        :class:`VectorsOutputMixin`
    """


class Index(BaseModel):
    """
    Represents a vector index in AWS S3 Vectors service.

    This class provides a Pythonic interface for managing vector indexes,
    including creation, vector storage, and similarity search operations.
    It handles the complexities of AWS API interactions and data format
    conversions.

    :param bucket_name: Name of the S3 vector bucket containing the index
    :param index_name: Unique name for the vector index
    :param data_type: Data type for vector embeddings (e.g., "float32")
    :param dimension: Dimensionality of the vectors (e.g., 768 for many LLM embeddings)
    :param distance_metric: Distance metric for similarity calculations (e.g., "cosine", "euclidean")

    Example:
        >>> index = Index(
        ...     bucket_name="my-vectors",
        ...     index_name="documents",
        ...     data_type="float32",
        ...     dimension=768,
        ...     distance_metric="cosine"
        ... )
        >>> # Create the index
        >>> result = index.create(s3_vectors_client)
        >>> # Store vectors
        >>> vectors = [Vector(key="doc1", data=[0.1, 0.2, 0.3])]
        >>> index.put_vectors(s3_vectors_client, vectors)
        >>> # Query similar vectors
        >>> results = index.query_vectors(s3_vectors_client, [0.1, 0.2, 0.3])
    """

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
        Create the vector index in AWS S3 Vectors service.

        This method creates a new vector index with the specified configuration.
        It handles the common case where an index with the same name already
        exists by returning None instead of raising an exception.

        :param s3_vectors_client: The AWS S3 Vectors client to use for the operation
        :param vector_bucket_arn: Optional ARN of the vector bucket. If provided,
            takes precedence over bucket_name
        :param metadata_configuration: Optional configuration for metadata fields
                that can be used for filtering

        :returns: A dictionary containing the AWS response if the index was created
            successfully, or None if the index already exists.

        Raises:
            botocore.exceptions.ClientError: For AWS errors other than index
                name conflicts (e.g., permission errors, invalid parameters).

        Example:
            >>> index = Index(
            ...     bucket_name="my-bucket",
            ...     index_name="documents",
            ...     data_type="float32",
            ...     dimension=768,
            ...     distance_metric="cosine"
            ... )
            >>> result = index.create(s3_vectors_client)
            >>> if result:
            ...     print("Index created successfully")
            ... else:
            ...     print("Index already exists")

        Reference:
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/create_index.html
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

    def delete(
        self,
        s3_vectors_client: "S3VectorsClient",
        index_arn: str = OPT,
    ):
        """
        Delete the vector index.

        .. note::

            Delete index will also delete all vectors in the index. You don't
            need to delete vectors one by one before deleting the index.

        Reference:
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/delete_index.html
        """
        kwargs = {
            "indexName": self.index_name,
            "indexArn": index_arn,
        }
        kwargs = remove_optional(**kwargs)
        if "indexArn" in kwargs:
            kwargs.pop("indexName")
        s3_vectors_client.delete_index(
            vectorBucketName=self.bucket_name,
            **kwargs,
        )

    @classmethod
    def get(
        cls,
        s3_vectors_client: "S3VectorsClient",
        vector_bucket_name: str,
        index_name: str = OPT,
        index_arn: str = OPT,
    ):
        """
        Retrieve an existing vector index from AWS S3 Vectors service.

        This method fetches the index configuration and metadata from AWS,
        allowing you to reconstruct an `Index` object for further operations.
        You can specify either the index name or the index ARN to identify
        the index.

        :param s3_vectors_client: The AWS S3 Vectors client to use for the operation
        :param vector_bucket_name: Name of the S3 vector bucket containing the index
        :param index_name: Optional name of the vector index to retrieve
        :param index_arn: Optional ARN of the vector index to retrieve

        :returns: An `Index` object representing the retrieved index

        :raises botocore.exceptions.ClientError: If the index does not exist or AWS returns an error

        Example:
            >>> index = Index.get(
            ...     s3_vectors_client,
            ...     vector_bucket_name="my-vectors",
            ...     index_name="documents"
            ... )
            >>> print(index.dimension)  # Prints the index dimension

        Reference:
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/get_index.html
        """
        try:
            res = s3_vectors_client.get_index(
                **remove_optional(
                    vectorBucketName=vector_bucket_name,
                    indexName=index_name,
                    indexArn=index_arn,
                )
            )
            res = s3vectors_caster.get_index(res)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NotFoundException":
                return None
            raise

        return cls(
            bucket_name=vector_bucket_name,
            index_name=res.index.indexName,
            data_type=res.index.dataType,
            dimension=res.index.dimension,
            distance_metric=res.index.distanceMetric,
        )

    @classmethod
    def new_for_delete(
        cls,
        bucket_name: str,
        index_name: str,
    ):
        """
        Create an Index object for deletion operations only,
        we don't need data_type, dimension, distance_metric.

        :param bucket_name: Name of the S3 vector bucket containing the index
        :param index_name: Unique name for the vector index

        :returns: An :class:`Index` object configured for deletion operations.
        """
        return cls(
            bucket_name=bucket_name,
            index_name=index_name,
            data_type="float32",  # Placeholder, not used for deletion
            dimension=1,  # Placeholder, not used for deletion
            distance_metric="cosine",  # Placeholder, not used for deletion
        )

    @classmethod
    def new_for_delete_from_list_index_response(
        cls,
        response: "boto3_dataclass_s3vectors.type_defs.ListIndexesOutput",
    ):
        """
        Create Index objects for deletion from
        :meth:`s3vectorm.bucket.Bucket.list_index` response.

        :param response: The response from the list_index operation

        :returns: A list of :class:`Index` objects configured for deletion operations.
        """
        try:
            indexes = response.indexes
        except KeyError:
            indexes = []
        return [
            cls.new_for_delete(
                bucket_name=index_summary.vectorBucketName,
                index_name=index_summary.indexName,
            )
            for index_summary in indexes
        ]

    def put_vectors(
        self,
        s3_vectors_client: "S3VectorsClient",
        vectors: list["Vector"],
    ):
        """
        Store vectors in the index.

        This method uploads a list of vectors to the S3 Vectors index,
        automatically converting each vector to the appropriate format
        required by the AWS API.

        :param s3_vectors_client: The AWS S3 Vectors client to use for the operation
        :param vectors: List of Vector objects to store in the index

        Example:
            >>> vectors = [
            ...     Vector(key="doc1", data=[0.1, 0.2, 0.3], category="documents"),
            ...     Vector(key="doc2", data=[0.4, 0.5, 0.6], category="documents")
            ... ]
            >>> index.put_vectors(s3_vectors_client, vectors)

        Reference:
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/put_vectors.html
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
    ) -> "QueryVectorsOutput":
        """
        Query the index for vectors similar to the provided query vector.

        This method performs a similarity search in the vector index, returning
        the most similar vectors based on the configured distance metric.
        It supports filtering by metadata and optional return of metadata
        and distance values.

        :param s3_vectors_client: The AWS S3 Vectors client to use for the operation
        :param data: Query vector as a list of float values
        :param top_k: Maximum number of similar vectors to return (default: 10)
        :param filter: Optional filter expression for metadata-based filtering
        :param return_metadata: Whether to include metadata in the results (default: False)
        :param return_distance: Whether to include distance values in the results (default: False)

        :returns: A QueryVectorsOutput object containing the search results

        Example:
            >>> # Basic similarity search
            >>> results = index.query_vectors(
            ...     s3_vectors_client,
            ...     data=[0.1, 0.2, 0.3],
            ...     top_k=5
            ... )
            >>> vectors = results.to_vectors(Vector)

            >>> # Search with metadata filtering
            >>> from s3vectorm.metadata import Expr
            >>> filter_expr = Expr(field="category", operator="$eq", value="documents")
            >>> results = index.query_vectors(
            ...     s3_vectors_client,
            ...     data=[0.1, 0.2, 0.3],
            ...     filter=filter_expr,
            ...     return_metadata=True,
            ...     return_distance=True
            ... )

        Reference:
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/query_vectors.html
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

    def list_vectors(
        self,
        s3_vectors_client: "S3VectorsClient",
        index_arn: str = OPT,
        segment_count: int = OPT,
        segment_index: int = OPT,
        return_data: bool = OPT,
        return_metadata: bool = OPT,
        page_size: int = 100,
        max_items: int = 9999,
    ) -> T.Generator["ListVectorsOutput", None, None]:
        """
        List all vectors in the index with pagination support.

        This method retrieves vectors from the S3 Vectors index using pagination
        to handle large result sets efficiently. It supports segmentation for
        parallel processing and optional return of vector data and metadata.

        :param s3_vectors_client: The AWS S3 Vectors client to use for the operation
        :param index_arn: Optional ARN of the vector index. If provided,
            takes precedence over index_name
        :param segment_count: Total number of segments for parallel processing
        :param segment_index: Index of the segment to retrieve (0-based)
        :param return_data: Whether to include vector data in the results
        :param return_metadata: Whether to include metadata in the results
        :param page_size: Number of vectors per page (default: 100)
        :param max_items: Maximum total number of vectors to retrieve (default: 9999)

        :yields: ListVectorsOutput objects containing paginated vector results

        Example:
            >>> for page in index.list_vectors(
            ...     s3_vectors_client,
            ...     return_data=True,
            ...     return_metadata=True,
            ...     page_size=50
            ... ):
            ...     vectors = page.as_vector_objects(Vector)
            ...     print(f"Retrieved {len(vectors)} vectors")

        Reference:
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/paginator/ListVectors.html
        """
        kwargs = {
            "vectorBucketName": self.bucket_name,
            "indexName": self.index_name,
            "indexArn": index_arn,
            "segmentCount": segment_count,
            "segmentIndex": segment_index,
            "returnData": return_data,
            "returnMetadata": return_metadata,
            "PaginationConfig": {
                "MaxItems": max_items,
                "PageSize": page_size,
            },
        }
        kwargs = remove_optional(**kwargs)
        if "indexArn" in kwargs:
            kwargs.pop("indexName")
        paginator = s3_vectors_client.get_paginator("list_vectors")
        for response in paginator.paginate(**kwargs):
            yield ListVectorsOutput(
                boto3_raw_data=response,
                data_type=self.data_type,
            )

    def delete_vectors(
        self,
        s3_vectors_client: "S3VectorsClient",
        keys: list[str],
        index_arn: str = OPT,
    ):
        """
        Delete specific vectors from the index by their keys.

        This method removes vectors from the S3 Vectors index based on their
        unique keys. This is useful for selective removal of vectors that are
        no longer needed or need to be updated.

        :param s3_vectors_client: The AWS S3 Vectors client to use for the operation
        :param keys: List of vector keys (unique identifiers) to delete
        :param index_arn: Optional ARN of the vector index. If provided,
            takes precedence over index_name

        Example:
            >>> # Delete specific vectors by their keys
            >>> keys_to_delete = ["doc1", "doc2", "doc3"]
            >>> index.delete_vectors(s3_vectors_client, keys_to_delete)

        Reference:
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/delete_vectors.html
        """
        kwargs = {
            "indexName": self.index_name,
            "indexArn": index_arn,
        }
        kwargs = remove_optional(**kwargs)
        if "indexArn" in kwargs:
            kwargs.pop("indexName")
        s3_vectors_client.delete_vectors(
            vectorBucketName=self.bucket_name,
            keys=keys,
            **kwargs,
        )

    def delete_all_vectors(
        self,
        s3_vectors_client: "S3VectorsClient",
        page_size: int = 100,
        max_items: int = 9999,
    ) -> int:
        """
        Delete all vectors in the index.

        This method provides a convenient way to delete all vectors from the index
        by first listing them with pagination and then deleting them in batches.
        This is useful for clearing an index without deleting the index structure itself.

        :param s3_vectors_client: The AWS S3 Vectors client to use for the operation
        :param page_size: Number of vectors to process per page (default: 100)
        :param max_items: Maximum total number of vectors to delete (default: 9999)

        :returns: The total number of vectors that were deleted

        Example:
            >>> deleted_count = index.delete_all_vectors(s3_vectors_client)
            >>> print(f"Deleted {deleted_count} vectors from the index")

        .. note::

            This operation may take some time for large indexes as it processes
            vectors in batches. For very large indexes, consider using segmentation
            parameters in list_vectors for parallel processing.
        """
        n_deleted = 0
        for res in self.list_vectors(
            s3_vectors_client=s3_vectors_client,
            page_size=page_size,
            max_items=max_items,
        ):
            keys = [dct["key"] for dct in res.boto3_raw_data.get("vectors", [])]
            self.delete_vectors(s3_vectors_client=s3_vectors_client, keys=keys)
            n_deleted += len(keys)
        return n_deleted
