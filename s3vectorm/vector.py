# -*- coding: utf-8 -*-

"""
S3 Vector Data Model

This module provides the Vector class for representing vector data in the S3 Vectors
service. Vectors contain embedding data along with metadata and support conversion
to various formats required by AWS S3 Vectors operations.

The Vector class serves as the core data structure for storing and manipulating
vector embeddings, with built-in methods for format conversion and metadata
extraction.

Example:
    >>> vector = Vector(
    ...     key="document-1",
    ...     data=[0.1, 0.2, 0.3],
    ...     distance=0.95
    ... )
    >>> put_format = vector.to_put_vectors_dict("float32")
    >>> metadata = vector.to_metadata_dict()
"""

import typing as T
from pydantic import BaseModel, Field

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3vectors.literals import DataTypeType
    from mypy_boto3_s3vectors.type_defs import PutInputVectorTypeDef


class Vector(BaseModel):
    """
    Represents a vector with embedding data and associated metadata.

    This class models a vector data structure suitable for storage and retrieval
    in AWS S3 Vectors service. It includes the vector's unique identifier,
    embedding data, distance metric, and supports additional metadata fields
    through Pydantic's dynamic field capabilities.

    Attributes:
        key: Unique identifier for the vector
        data: Optional list of float values representing the vector embedding
        distance: Optional distance metric (typically set during query operations)

    Examples:
        >>> # Create a vector with embedding data
        >>> vector = Vector(
        ...     key="doc-123",
        ...     data=[0.1, 0.2, 0.3, 0.4],
        ...     distance=0.95
        ... )

        >>> # Create a vector without embedding data (for metadata-only operations)
        >>> metadata_vector = Vector(
        ...     key="doc-456",
        ...     category="documents",
        ...     status="active"
        ... )

    References:
        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/list_vectors.html
        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/put_vectors.html
        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/query_vectors.html
    """

    key: str = Field()
    data: list[float] | None = Field(default=None)
    distance: float | None = Field(default=None)

    def to_put_vectors_dict(
        self,
        data_type: "DataTypeType",
    ) -> "PutInputVectorTypeDef":
        """
        Convert the vector to the format required for AWS S3 put_vectors operation.

        This method transforms the vector into the dictionary format expected by
        the AWS S3 Vectors put_vectors API. It separates the key, embedding data,
        and metadata into the appropriate structure while excluding the distance
        field (which is only relevant for query results).

        Args:
            data_type: The data type for the vector embedding (e.g., "float32", "int8")

        Returns:
            A dictionary formatted for the put_vectors API containing:
            - key: The vector's unique identifier
            - data: Dictionary with data_type as key and embedding as value
            - metadata: All additional fields except key, data, and distance

        Example:
            >>> vector = Vector(
            ...     key="doc-1",
            ...     data=[0.1, 0.2, 0.3],
            ...     category="documents"
            ... )
            >>> result = vector.to_put_vectors_dict("float32")
            >>> print(result)
            {
                "key": "doc-1",
                "data": {"float32": [0.1, 0.2, 0.3]},
                "metadata": {"category": "documents"}
            }
        """
        dct = self.model_dump()
        dct.pop("distance")
        return {
            "key": dct.pop("key"),
            "data": {
                data_type: dct.pop("data"),
            },
            "metadata": dct,
        }

    def to_metadata_dict(self):
        """
        Extract metadata fields excluding core vector attributes.

        This method returns only the additional metadata fields associated with
        the vector, excluding the core attributes (key, data, distance) that are
        handled separately in AWS S3 Vectors operations.

        Returns:
            A dictionary containing only the metadata fields

        Example:
            >>> vector = Vector(
            ...     key="doc-1",
            ...     data=[0.1, 0.2, 0.3],
            ...     distance=0.95,
            ...     category="documents",
            ...     status="active"
            ... )
            >>> metadata = vector.to_metadata_dict()
            >>> print(metadata)
            {"category": "documents", "status": "active"}
        """
        dct = self.model_dump()
        dct.pop("key")
        dct.pop("data")
        dct.pop("distance")
        return dct
