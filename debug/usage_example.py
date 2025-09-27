# -*- coding: utf-8 -*-

import typing as T
import pydantic
from pydantic import Field
from pydantic.fields import FieldInfo


def and_(*conditions):
    pass


def or_(*conditions):
    pass


class QueryField:
    """支持 ORM 风格查询的字段对象"""
    def __init__(self, field_name: str, field_info: FieldInfo):
        self.field_name = field_name
        self.field_info = field_info

    def eq(self, value):
        return None

    def ne(self, value):
        return None

    def lt(self, value):
        return None

    def le(self, value):
        return None

    def gt(self, value):
        return None

    def ge(self, value):
        return None

    def gte(self, value):
        return self.ge(value)

    def in_(self, values):
        return None

    def not_in(self, values):
        return None


class OrmModelMeta(type(pydantic.BaseModel)):
    """元类，用于处理类级别的属性访问"""

    def __getattr__(cls, name):
        # 避免在 pydantic 内部属性上递归
        if name.startswith('__pydantic') or name.startswith('_'):
            raise AttributeError(f"'{cls.__name__}' object has no attribute '{name}'")

        # 直接使用 object.__getattribute__ 来避免递归
        try:
            fields = cls.model_fields
            # fields = object.__getattribute__(cls, '__pydantic_fields__')
            if name in fields:
                return QueryField(name, fields[name])
        except AttributeError:
            pass

        raise AttributeError(f"'{cls.__name__}' object has no attribute '{name}'")


class OrmModel(pydantic.BaseModel, metaclass=OrmModelMeta):
    """支持 ORM 风格查询的 Pydantic 模型基类"""
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


class Model(OrmModel):
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
    # print(chunk.model_dump())
    # index.put_vectors(chunk)

    # 测试类级别访问和查询方法
    print("=== 测试 ORM 查询功能 ===")
    print(f"Chunk.document_id 类型: {type(Chunk.document_id)}")
    print(f"Chunk.document_id.field_name: {Chunk.document_id.field_name}")
    print(f"Chunk.document_id.eq('doc-1') 返回: {Chunk.document_id.eq('doc-1')}")
    print(f"Chunk.document_id.gte(1) 返回: {Chunk.document_id.gte(1)}")
    print(f"Chunk.chunk_seq.lt(10) 返回: {Chunk.chunk_seq.lt(10)}")

    # 测试实例访问是否正常
    print(f"chunk.document_id 实例值: {chunk.document_id}")
    print(f"chunk.chunk_seq 实例值: {chunk.chunk_seq}")

    # 确认 Pydantic 功能正常
    print(f"Chunk.model_fields.keys(): {list(Chunk.model_fields.keys())}")

    index.query_vectors(
        data=[0.1, 0.2, 0.3],
        # The Chunk.document_id should return a custom object that supports eq, ne, lt, le, gt, ge, in, not_in
        filters=Chunk.document_id.eq("doc-1"),
    )
