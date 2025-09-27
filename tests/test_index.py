# -*- coding: utf-8 -*-

from s3vectorm.index import QueryVectorsOutput
from pydantic import Field
from s3vectorm.vector import Vector


class TestQueryVectorsOutput:
    def test_to_vectors(self):
        class DocChunk(Vector):
            document_id: str = Field()
            chunk_seq: int = Field()

        boto3_raw_data = {
            "vectors": [
                {
                    "key": "doc-1#1",
                    "data": {"float32": [0.1] * 1024},
                    "metadata": {
                        "document_id": "doc-1#1",
                        "chunk_seq": 1,
                    },
                }
            ]
        }
        out = QueryVectorsOutput(boto3_raw_data=boto3_raw_data, data_type="float32")
        for vector in out.as_vector_objects(DocChunk):
            assert isinstance(vector, Vector)
            _ = vector.document_id  # type hint works


if __name__ == "__main__":
    from s3vectorm.tests import run_cov_test

    run_cov_test(
        __file__,
        "s3vectorm.index",
        preview=False,
    )
