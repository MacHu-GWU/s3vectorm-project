# -*- coding: utf-8 -*-

import dataclasses
import typing as T


class OperatorEnum:
    eq = "$eq"
    ne = "$ne"
    gt = "$gt"
    gte = "$gte"
    lt = "$lt"
    lte = "$lte"
    in_ = "$in"


@dataclasses.dataclass
class Expr:
    field: str = dataclasses.field()
    operator: str = dataclasses.field()
    value: T.Any = dataclasses.field()


@dataclasses.dataclass
class Field:
    name: str = dataclasses.field()

    def eq(self, other: T.Any) -> Expr:
        ...
        return Expr(
            field=self.name,
            operator=OperatorEnum.eq,
            value=other,
        )


class BaseMetaModel:
    pass


class BaseModel(metaclass=BaseMetaModel):
    pass


# below is user code
if __name__ == "__main__":
    class DocumentChunkBaseModel(BaseModel):
        document_id: str = Field()
        chunk_seq: int = Field()

    class DocumentChunkModel(BaseModel):
        owner_id: str = Field()

    doc_chunk_model = DocumentChunkModel()

    expr = doc_chunk_model.document_id.eq("doc-1")
    assert isinstance(expr, Expr)

    expr = doc_chunk_model.chunk_seq.eq(1)
    assert isinstance(expr, Expr)

    expr = doc_chunk_model.owner_id.eq("alice")
    assert isinstance(expr, Expr)
