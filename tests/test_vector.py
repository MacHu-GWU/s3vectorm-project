# -*- coding: utf-8 -*-

from s3vectorm.vector import Vector


def test_vector_creation():
    """Test basic Vector creation and attributes"""
    vector = Vector(key="test-key", data=[1.0, 2.0, 3.0])
    assert vector.key == "test-key"
    assert vector.data == [1.0, 2.0, 3.0]
    assert vector.distance is None


def test_vector_with_distance():
    """Test Vector creation with distance"""
    vector = Vector(key="test-key", data=[1.0, 2.0, 3.0], distance=0.5)
    assert vector.key == "test-key"
    assert vector.data == [1.0, 2.0, 3.0]
    assert vector.distance == 0.5


def test_to_put_vectors_dict():
    """Test to_put_vectors_dct method"""
    vector = Vector(key="test-key", data=[1.0, 2.0, 3.0], distance=0.5)
    result = vector.to_put_vectors_dict("float32")
    expected = {"key": "test-key", "data": {"float32": [1.0, 2.0, 3.0]}, "metadata": {}}
    assert result == expected


def test_to_put_vectors_dict_no_distance():
    """Test to_put_vectors_dct method without distance"""
    vector = Vector(key="test-key", data=[1.0, 2.0, 3.0])
    result = vector.to_put_vectors_dict("float32")
    expected = {"key": "test-key", "data": {"float32": [1.0, 2.0, 3.0]}, "metadata": {}}
    assert result == expected


def test_to_metadata_dict():
    """Test to_metadata_dict method"""
    vector = Vector(key="test-key", data=[1.0, 2.0, 3.0], distance=0.5)
    result = vector.to_metadata_dict()
    expected = {}
    assert result == expected


def test_to_metadata_dict_no_distance():
    """Test to_metadata_dict method without distance"""
    vector = Vector(key="test-key", data=[1.0, 2.0, 3.0])
    result = vector.to_metadata_dict()
    expected = {}
    assert result == expected


def test_pydantic_model_dump():
    """Test that Vector works as a Pydantic model"""
    vector = Vector(key="test-key", data=[1.0, 2.0, 3.0], distance=0.5)
    dump = vector.model_dump()
    expected = {"key": "test-key", "data": [1.0, 2.0, 3.0], "distance": 0.5}
    assert dump == expected


if __name__ == "__main__":
    from s3vectorm.tests import run_cov_test

    run_cov_test(
        __file__,
        "s3vectorm.vector",
        preview=False,
    )
