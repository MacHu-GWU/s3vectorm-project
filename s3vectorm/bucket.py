# -*- coding: utf-8 -*-

"""
S3 Vector Bucket Management

This module provides functionality for managing S3 vector buckets, including
bucket creation with proper error handling. It integrates with the AWS S3 Vectors
service to provide a Pythonic interface for bucket operations.

The module handles common AWS operations such as bucket creation and provides
appropriate error handling for scenarios like bucket name conflicts.

Example:
    >>> bucket = Bucket(name="my-vector-bucket")
    >>> result = bucket.create(s3_vectors_client)
"""

import typing as T

import boto3_dataclass_s3vectors.type_defs
import botocore.exceptions
from pydantic import BaseModel, Field

from func_args.api import OPT, remove_optional


if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3vectors import S3VectorsClient
    from boto3_dataclass_s3vectors.type_defs import EncryptionConfiguration


class Bucket(BaseModel):
    """
    Represents an S3 vector bucket for storing and managing vector data.

    This class provides a Pydantic model for S3 vector buckets with methods
    to create buckets in AWS S3 Vectors service. It handles common operations
    and error scenarios gracefully.

    Attributes:
        name: The name of the vector bucket

    Example:
        >>> bucket = Bucket(name="my-vector-bucket")
        >>> result = bucket.create(s3_vectors_client)
        >>> if result is not None:
        ...     print("Bucket created successfully")
        ... else:
        ...     print("Bucket already exists")
    """

    name: str = Field()

    def create(
        self,
        s3_vectors_client: "S3VectorsClient",
        encryption_configuration: "EncryptionConfiguration" = OPT,
    ) -> dict[str, T.Any] | None:
        """
        Create the vector bucket in AWS S3 Vectors service.

        This method attempts to create a new S3 vector bucket with the specified
        name and optional encryption configuration. It handles the common case
        where a bucket with the same name already exists by returning None
        instead of raising an exception.

        :param s3_vectors_client: The AWS S3 Vectors client to use for the operation
        :param encryption_configuration: Optional encryption settings for the bucket.
            If not provided, default encryption will be used.

        :returns: A dictionary containing the AWS response if the bucket was created
            successfully, or None if the bucket already exists.

        Raises:
            botocore.exceptions.ClientError: For AWS errors other than bucket
                name conflicts (e.g., permission errors, invalid bucket names).

        Example:
            >>> bucket = Bucket(name="my-new-bucket")
            >>> client = boto3.client('s3vectors')
            >>> result = bucket.create(client)
            >>> if result:
            ...     print(f"Created bucket: {result}")
            ... else:
            ...     print("Bucket already exists")

        Reference:
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/create_vector_bucket.html
        """
        try:
            return s3_vectors_client.create_vector_bucket(
                vectorBucketName=self.name,
                **remove_optional(
                    encryptionConfiguration=encryption_configuration,
                ),
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ConflictException":
                return None
            raise

    def delete(
        self,
        s3_vectors_client: "S3VectorsClient",
        vector_bucket_arn: str = OPT,
    ):
        """
        .. note::

            You have to delete all indexes in bucket before you can delete the bucket.

        Reference:
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/delete_vector_bucket.html
        """
        kwargs = {
            "vectorBucketName": self.name,
            "vectorBucketArn": vector_bucket_arn,
        }
        kwargs = remove_optional(**kwargs)
        if "vectorBucketArn" in kwargs:
            kwargs.pop("vectorBucketName")
        return s3_vectors_client.delete_vector_bucket(**kwargs)

    def list_index(
        self,
        s3_vectors_client: "S3VectorsClient",
        vector_bucket_arn: str = OPT,
        prefix: str = OPT,
        page_size: int = 100,
        max_items: int = 9999,
    ) -> T.Generator[
        boto3_dataclass_s3vectors.type_defs.ListIndexesOutput,
        None,
        None,
    ]:
        """
        List all indexes in the vector bucket with pagination support.

        This method retrieves all vector indexes within the bucket using pagination
        to handle buckets with many indexes efficiently. It supports filtering by
        index name prefix.

        :param s3_vectors_client: The AWS S3 Vectors client to use for the operation
        :param vector_bucket_arn: Optional ARN of the vector bucket. If provided,
            takes precedence over bucket name
        :param prefix: Optional prefix to filter index names
        :param page_size: Number of indexes per page (default: 100)
        :param max_items: Maximum total number of indexes to retrieve (default: 9999)

        :yields: Dict responses containing paginated index results

        Example:
            >>> bucket = Bucket(name="my-bucket")
            >>> for page in bucket.list_index(
            ...     s3_vectors_client,
            ...     prefix="document-",
            ...     page_size=50
            ... ):
            ...     indexes = page.get("indexes", [])
            ...     print(f"Found {len(indexes)} indexes")

        Reference:
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/paginator/ListIndexes.html
        """
        kwargs = {
            "vectorBucketName": self.name,
            "vectorBucketArn": vector_bucket_arn,
            "prefix": prefix,
            "PaginationConfig": {
                "MaxItems": max_items,
                "PageSize": page_size,
            },
        }
        kwargs = remove_optional(**kwargs)
        if "vectorBucketArn" in kwargs:
            kwargs.pop("vectorBucketName")
        paginator = s3_vectors_client.get_paginator("list_indexes")
        for res in paginator.paginate(**kwargs):
            res = boto3_dataclass_s3vectors.type_defs.ListIndexesOutput(res)
            yield res
