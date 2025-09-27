# -*- coding: utf-8 -*-

import typing as T
import pydantic
from pydantic import Field
from pydantic.fields import FieldInfo


def and_(*conditions):
    pass


def or_(*conditions):
    pass


class Bucket(pydantic.BaseModel):
    bucket_name: str = Field()

    def get_index(self, index_name: str) -> "Index":
        return Index(bucket_name=self.bucket_name, index_name=index_name)


class Index(pydantic.BaseModel):
    bucket_name: str = Field()
    index_name: str = Field()

    def put_vectors(
        self,
        models: T.Union[list["Model"], "Model"],
    ):
        """
        Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/put_vectors.html
        """
        if isinstance(models, list) is False:
            models = [models]
        print(
            f"Putting {len(models)} vectors into index {self.index_name} in bucket {self.bucket_name} ..."
        )

    def query_vectors(
        self,
        data: list[float],
        top_k: int = 10,
        filters=None,
    ):
        """
        Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors/client/query_vectors.html
        """
        print(
            f"Querying vectors from index {self.index_name} in bucket {self.bucket_name} ..."
        )


class Model(pydantic.BaseModel):
    key: str = Field()
    data: list[float] = Field()


# Below is an example usage of the s3vectorm class
if __name__ == "__main__":
    # from s3vectorm import Bucket, Index, Model, Field
    from rich import print as rprint

    class Chunk(Model):
        document_id: str = Field()
        chunk_seq: int = Field()

    bucket = Bucket(bucket_name="my-vector-bucket")
    index = bucket.get_index(index_name="my-index")

    chunk = Chunk(
        key="doc-1#1",
        data=[0.1, 0.2, 0.3],
        document_id="doc-1",
        chunk_seq=1,
    )
    # index.put_vectors(chunk)

    index.query_vectors(
        data=[0.1, 0.2, 0.3],
        # The Chunk.document_id should return a custom object that supports eq, ne, lt, le, gt, ge, in, not_in
        filters=Chunk.document_id.eq("doc-1"),
    )
