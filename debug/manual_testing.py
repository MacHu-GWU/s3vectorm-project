# -*- coding: utf-8 -*-

import boto3
from pydantic import Field
from s3vectorm.api import (
    Bucket,
    Index,
    Vector,
    BaseMetadata,
    MetaKey,
)
from rich import print as rprint

aws_profile = "esc_app_dev_us_east_1"
# bucket_name = "esc-app-dev-s3vectorm-manual-testing"
bucket_name = "esc-app-dev-s3vectorm"
index_name = "test"

boto_ses = boto3.Session(profile_name=aws_profile)
client = boto_ses.client("s3vectors")

# ------------------------------------------------------------------------------
# Setup Bucket
# ------------------------------------------------------------------------------
bucket = Bucket(name=bucket_name)
# bucket.delete(client)
bucket.create(client)

# ------------------------------------------------------------------------------
# Reset everything
# ------------------------------------------------------------------------------
# for response in bucket.list_index(client):
#     for index in Index.new_for_delete_from_list_index_response(response):
#         rprint(f"Deleting index: {index.index_name}")
#         index.delete(client)

# ------------------------------------------------------------------------------
# Setup Index
# ------------------------------------------------------------------------------
index = Index(
    bucket_name=bucket_name,
    index_name=index_name,
    data_type="float32",
    dimension=1024,
    distance_metric="cosine",
)
# index.delete(client)
# index.create(client)
# index.delete_all_vectors(client)


# ------------------------------------------------------------------------------
# Define Vector Metadata Model
# ------------------------------------------------------------------------------
class DocChunk(Vector):
    document_id: str = Field()
    chunk_seq: int = Field()
    owner_id: str = Field()


# Intentionally make it a separate class to demonstrate inheritance
class BaseDocChunkMeta(BaseMetadata):
    document_id = MetaKey()
    chunk_seq = MetaKey()


class DocChunkMeta(BaseDocChunkMeta):
    owner_id = MetaKey()


# ------------------------------------------------------------------------------
# Insert Vectors
# ------------------------------------------------------------------------------
vectors = [
    DocChunk(
        key="doc-1#1",
        data=[0.1] * 1024,
        document_id="doc-1",
        chunk_seq=1,
        owner_id="user-1",
    ),
    DocChunk(
        key="doc-1#2",
        data=[0.1] * 1024,
        document_id="doc-1",
        chunk_seq=2,
        owner_id="user-1",
    ),
    DocChunk(
        key="doc-2#1",
        data=[0.1] * 1024,
        document_id="doc-2",
        chunk_seq=1,
        owner_id="user-2",
    ),
    DocChunk(
        key="doc-2#2",
        data=[0.1] * 1024,
        document_id="doc-2",
        chunk_seq=2,
        owner_id="user-2",
    ),
]
# index.put_vectors(client, vectors)

data = [0.1] * 1024


def query_vectors():
    # filter = DocChunkMeta.owner_id.eq("user-1")

    # filter = DocChunkMeta.chunk_seq.in_(
    #     [
    #         2,
    #     ]
    # )

    filter = DocChunkMeta.chunk_seq.eq(2) & DocChunkMeta.owner_id.eq("user-2")

    res = index.query_vectors(
        client,
        data=data,
        filter=filter,
        return_metadata=True,
        # return_distance=True,
    )

    for ith, vector in enumerate(res.as_vector_objects(DocChunk), start=1):
        print(f"--- {ith} ---")
        print(f"{vector.model_dump()}")


query_vectors()


def list_vectors():
    for res in index.list_vectors(client, return_metadata=True):
        for vector in res.as_vector_objects(DocChunk):
            print(vector.model_dump())


list_vectors()
