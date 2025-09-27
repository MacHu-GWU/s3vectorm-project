# -*- coding: utf-8 -*-

import boto3
from pydantic import Field
from rich import print as rprint

from s3vectorm.bucket import Bucket
from s3vectorm.index import Index
from s3vectorm.model import Model
from s3vectorm.query import BaseMetadata, MetaKey

aws_profile = "esc_app_dev_us_east_1"
bucket_name = "esc-app-dev-s3vectorm"
index_name = "test1"

boto_ses = boto3.Session(profile_name=aws_profile)
client = boto_ses.client("s3vectors")

bucket = Bucket(name=bucket_name)
# bucket.create(client)

index = Index(
    bucket_name=bucket_name,
    index_name=index_name,
    data_type="float32",
    dimension=1024,
    distance_metric="cosine",
)
# index.create(client)


class DocChunk(Model):
    document_id: str = Field()
    chunk_seq: int = Field()
    owner_id: str = Field()


class BaseDocChunkMeta(BaseMetadata):
    document_id = MetaKey()
    chunk_seq = MetaKey()


class DocChunkMeta(BaseDocChunkMeta):
    owner_id = MetaKey()


doc_chunk = DocChunk(
    key="doc-1#1",
    data=[0.1] * 1024,
    document_id="doc-1",
    chunk_seq=1,
    owner_id="user-1",
)
# index.put_vectors(client, [doc_chunk])

data = [0.1] * 1024
filter = DocChunkMeta.owner_id.eq("user-1")
res = index.query_vectors(
    client,
    data=data,
    filter=filter,
    return_metadata=True,
)
# for vector in res.vectors:
#     rprint(f"{vector.metadata = }")
