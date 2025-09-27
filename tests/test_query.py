# -*- coding: utf-8 -*-

from s3vectorm.query import OperatorEnum, MetaKey, BaseMetadata, Expr, CompoundExpr


class Vector1Meta(BaseMetadata):
    a = MetaKey()
    b = MetaKey()


class Vector2Meta(BaseMetadata):
    c = MetaKey()
    d = MetaKey()


class Vector3Meta(Vector1Meta, Vector2Meta):
    e = MetaKey()
    f = MetaKey()
    g = MetaKey()


class VectorMeta(Vector3Meta):
    pass


def test_basic_operators():
    """Test basic query operators"""
    # Test basic operators
    assert VectorMeta.a.eq("test").to_doc() == {"a": {"$eq": "test"}}
    assert VectorMeta.b.gt(10).to_doc() == {"b": {"$gt": 10}}
    assert VectorMeta.c.in_([1, 2, 3]).to_doc() == {"c": {"$in": [1, 2, 3]}}
    assert VectorMeta.d.ne("value").to_doc() == {"d": {"$ne": "value"}}
    assert VectorMeta.e.lte(5.5).to_doc() == {"e": {"$lte": 5.5}}
    # Verify compound query functionality
    q = VectorMeta.a.eq("a") & VectorMeta.b.eq("b")
    assert q.to_doc() == {"$and": [{"a": {"$eq": "a"}}, {"b": {"$eq": "b"}}]}


def test_simple_compound_expressions():
    """Test simple AND/OR compound expressions"""
    # Simple AND
    query = VectorMeta.a.eq("a") & VectorMeta.b.eq("b")
    expected = {"$and": [{"a": {"$eq": "a"}}, {"b": {"$eq": "b"}}]}
    assert query.to_doc() == expected

    # Simple OR
    query = VectorMeta.a.eq("a") | VectorMeta.b.eq("b")
    expected = {"$or": [{"a": {"$eq": "a"}}, {"b": {"$eq": "b"}}]}
    assert query.to_doc() == expected

    # Multiple AND chain
    query = VectorMeta.a.eq("test") & VectorMeta.b.gt(10) & VectorMeta.c.in_([1, 2])
    expected = {
        "$and": [
            {"$and": [{"a": {"$eq": "test"}}, {"b": {"$gt": 10}}]},
            {"c": {"$in": [1, 2]}},
        ]
    }
    assert query.to_doc() == expected


def test_two_level_nested_expressions():
    """Test two-level nested compound expressions"""
    # (a == "x" AND b > 10) OR (c < 5 AND d != "y")
    query = (VectorMeta.a.eq("x") & VectorMeta.b.gt(10)) | (
        VectorMeta.c.lt(5) & VectorMeta.d.ne("y")
    )
    expected = {
        "$or": [
            {"$and": [{"a": {"$eq": "x"}}, {"b": {"$gt": 10}}]},
            {"$and": [{"c": {"$lt": 5}}, {"d": {"$ne": "y"}}]},
        ]
    }
    assert query.to_doc() == expected

    # (a == 1 AND b == 2) OR (c == 3 AND d == 4) OR e == 5
    query = (
        (VectorMeta.a.eq(1) & VectorMeta.b.eq(2))
        | (VectorMeta.c.eq(3) & VectorMeta.d.eq(4))
        | VectorMeta.e.eq(5)
    )
    expected = {
        "$or": [
            {
                "$or": [
                    {"$and": [{"a": {"$eq": 1}}, {"b": {"$eq": 2}}]},
                    {"$and": [{"c": {"$eq": 3}}, {"d": {"$eq": 4}}]},
                ]
            },
            {"e": {"$eq": 5}},
        ]
    }
    assert query.to_doc() == expected


def test_three_level_nested_expressions():
    """Test three-level nested compound expressions (maximum complexity)"""
    # ((a == "x" OR b > 10) AND c < 5) OR d != "y"
    query = (
        (VectorMeta.a.eq("x") | VectorMeta.b.gt(10)) & VectorMeta.c.lt(5)
    ) | VectorMeta.d.ne("y")
    expected = {
        "$or": [
            {
                "$and": [
                    {"$or": [{"a": {"$eq": "x"}}, {"b": {"$gt": 10}}]},
                    {"c": {"$lt": 5}},
                ]
            },
            {"d": {"$ne": "y"}},
        ]
    }
    assert query.to_doc() == expected

    # (a == 1 AND (b == 2 OR c == 3)) OR (d == 4 AND e == 5)
    query = (VectorMeta.a.eq(1) & (VectorMeta.b.eq(2) | VectorMeta.c.eq(3))) | (
        VectorMeta.d.eq(4) & VectorMeta.e.eq(5)
    )
    expected = {
        "$or": [
            {
                "$and": [
                    {"a": {"$eq": 1}},
                    {"$or": [{"b": {"$eq": 2}}, {"c": {"$eq": 3}}]},
                ]
            },
            {"$and": [{"d": {"$eq": 4}}, {"e": {"$eq": 5}}]},
        ]
    }
    assert query.to_doc() == expected

    # ((a == 1 AND b == 2) OR (c == 3 AND d == 4)) AND (e == 5 OR f == 6)
    query = (
        (VectorMeta.a.eq(1) & VectorMeta.b.eq(2))
        | (VectorMeta.c.eq(3) & VectorMeta.d.eq(4))
    ) & (VectorMeta.e.eq(5) | VectorMeta.f.eq(6))
    expected = {
        "$and": [
            {
                "$or": [
                    {"$and": [{"a": {"$eq": 1}}, {"b": {"$eq": 2}}]},
                    {"$and": [{"c": {"$eq": 3}}, {"d": {"$eq": 4}}]},
                ]
            },
            {"$or": [{"e": {"$eq": 5}}, {"f": {"$eq": 6}}]},
        ]
    }
    assert query.to_doc() == expected


def test_inheritance():
    """Test field inheritance"""
    # Verify field inheritance works correctly
    assert "a" in VectorMeta._model_fields  # from Vector1Meta
    assert "c" in VectorMeta._model_fields  # from Vector2Meta
    assert "e" in VectorMeta._model_fields  # from Vector3Meta
    assert len(VectorMeta._model_fields) == 7  # a,b,c,d,e,f,g


def test_edge_cases():
    """Test edge cases and special values"""
    # Test with empty strings
    assert VectorMeta.a.eq("").to_doc() == {"a": {"$eq": ""}}

    # Test with zero values
    assert VectorMeta.b.eq(0).to_doc() == {"b": {"$eq": 0}}

    # Test with None values
    assert VectorMeta.c.eq(None).to_doc() == {"c": {"$eq": None}}

    # Test with boolean values
    assert VectorMeta.d.eq(True).to_doc() == {"d": {"$eq": True}}
    assert VectorMeta.e.eq(False).to_doc() == {"e": {"$eq": False}}


if __name__ == "__main__":
    from s3vectorm.tests import run_cov_test

    run_cov_test(
        __file__,
        "s3vectorm.query",
        preview=False,
    )
