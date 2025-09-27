# -*- coding: utf-8 -*-

"""
S3 Vector Metadata Query Framework

This module provides a framework for building type-safe query expressions
for S3 vector metadata filtering. It supports AWS S3 vector search metadata
filtering operators and allows building complex nested queries using Python
operators.

The framework is designed with the following principles:
- Type safety through dataclasses and type hints
- Pythonic query building using operator overloading (&, |)
- Support for inheritance to create hierarchical metadata models
- Clean separation between data models and query logic

Example:
    >>> class DocumentMeta(BaseMetadata):
    ...     document_id = MetaKey()
    ...     chunk_seq = MetaKey()
    ...
    >>> meta = DocumentMeta()
    >>> query = meta.document_id.eq("doc-1") & meta.chunk_seq.gt(5)
    >>> query.to_doc()
    {"$and": [{"document_id": {"$eq": "doc-1"}}, {"chunk_seq": {"$gt": 5}}]}
"""

import typing as T
import enum
import dataclasses


class OperatorEnum(str, enum.Enum):
    """
    Enumeration of supported query operators for S3 vector metadata filtering.

    These operators correspond to the AWS S3 vector metadata filtering operators
    as documented in the AWS S3 User Guide.

    Reference:
        https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-metadata-filtering.html#s3-vectors-metadata-filtering-filterable
    """

    eq = "$eq"
    ne = "$ne"
    gt = "$gt"
    gte = "$gte"
    lt = "$lt"
    lte = "$lte"
    in_ = "$in"
    nin = "$nin"
    exists = "$exists"
    and_ = "$and"
    or_ = "$or"


@dataclasses.dataclass
class Expr:
    """
    Represents a single query expression for metadata filtering.

    An expression consists of a field name, an operator, and a value.
    For example: field="document_id", operator="$eq", value="doc-1"

    Attributes:
        field: The metadata field name to filter on
        operator: The filtering operator (e.g., "$eq", "$gt", "$in")
        value: The value to compare against

    Example:
        >>> expr = Expr(field="status", operator="$eq", value="active")
        >>> expr.to_doc()
        {"status": {"$eq": "active"}}
    """
    field: str = dataclasses.field()
    operator: str = dataclasses.field()
    value: T.Any = dataclasses.field()

    def __and__(self, other: "Expr") -> "CompoundExpr":
        """
        Combine this expression with another using AND logic.

        Args:
            other: Another Expr to combine with this one

        Returns:
            A CompoundExpr representing the AND operation
        """
        return CompoundExpr(left=self, operator="$and", right=other)

    def __or__(self, other: "Expr") -> "CompoundExpr":
        """
        Combine this expression with another using OR logic.

        Args:
            other: Another Expr to combine with this one

        Returns:
            A CompoundExpr representing the OR operation
        """
        return CompoundExpr(left=self, operator="$or", right=other)

    def to_doc(self) -> dict:
        """
        Convert the expression to a dictionary format suitable for S3 filtering.

        Returns:
            A dictionary with the field as key and operator/value as nested dict
        """
        return {self.field: {self.operator: self.value}}


@dataclasses.dataclass
class CompoundExpr:
    """
    Represents a compound query expression combining multiple expressions.

    A compound expression contains two sub-expressions (left and right) combined
    with either AND or OR logic. This allows building complex nested queries.

    Attributes:
        left: The left-side expression (can be Expr or CompoundExpr)
        operator: The logical operator ("$and" or "$or")
        right: The right-side expression (can be Expr or CompoundExpr)

    Example:
        >>> expr1 = Expr(field="status", operator="$eq", value="active")
        >>> expr2 = Expr(field="priority", operator="$gt", value=5)
        >>> compound = CompoundExpr(left=expr1, operator="$and", right=expr2)
        >>> compound.to_doc()
        {"$and": [{"status": {"$eq": "active"}}, {"priority": {"$gt": 5}}]}
    """
    left: T.Union["Expr", "CompoundExpr"] = dataclasses.field()
    operator: str = dataclasses.field()  # "$and" or "$or"
    right: T.Union["Expr", "CompoundExpr"] = dataclasses.field()

    def __and__(self, other: T.Union[Expr, "CompoundExpr"]) -> "CompoundExpr":
        """
        Chain this compound expression with another using AND logic.

        Args:
            other: Another Expr or CompoundExpr to combine with this one

        Returns:
            A new CompoundExpr representing the AND operation
        """
        return CompoundExpr(left=self, operator=OperatorEnum.and_.value, right=other)

    def __or__(self, other: T.Union[Expr, "CompoundExpr"]) -> "CompoundExpr":
        """
        Chain this compound expression with another using OR logic.

        Args:
            other: Another Expr or CompoundExpr to combine with this one

        Returns:
            A new CompoundExpr representing the OR operation
        """
        return CompoundExpr(left=self, operator=OperatorEnum.or_.value, right=other)

    def to_doc(self) -> dict:
        """
        Convert the compound expression to a dictionary format for S3 filtering.

        Returns:
            A dictionary with the operator as key and list of sub-expressions as value
        """
        return {self.operator: [self.left.to_doc(), self.right.to_doc()]}


@dataclasses.dataclass
class MetaKey:
    """
    Represents a metadata field that can be used in query expressions.

    A MetaKey provides methods to create filtering expressions using various
    operators. Each method returns an Expr object that can be combined with
    other expressions to build complex queries.

    Attributes:
        name: The field name used in query expressions

    Example:
        >>> field = MetaKey(name="status")
        >>> expr = field.eq("active")
        >>> expr.to_doc()
        {"status": {"$eq": "active"}}
    """
    name: str = dataclasses.field(default="")

    def _to_expr(self, op: OperatorEnum, other: T.Any) -> Expr:
        """
        Create an Expr using this field with the given operator and value.

        Args:
            op: The operator to use
            other: The value to compare against

        Returns:
            An Expr representing the comparison
        """
        return Expr(
            field=self.name,
            operator=op.value,
            value=other,
        )

    def eq(self, other: T.Any) -> Expr:
        """Create an equality expression (field == value)."""
        return self._to_expr(op=OperatorEnum.eq, other=other)

    def ne(self, other: T.Any) -> Expr:
        """Create a not-equal expression (field != value)."""
        return self._to_expr(op=OperatorEnum.ne, other=other)

    def gt(self, other: T.Any) -> Expr:
        """Create a greater-than expression (field > value)."""
        return self._to_expr(op=OperatorEnum.gt, other=other)

    def gte(self, other: T.Any) -> Expr:
        """Create a greater-than-or-equal expression (field >= value)."""
        return self._to_expr(op=OperatorEnum.gte, other=other)

    def lt(self, other: T.Any) -> Expr:
        """Create a less-than expression (field < value)."""
        return self._to_expr(op=OperatorEnum.lt, other=other)

    def lte(self, other: T.Any) -> Expr:
        """Create a less-than-or-equal expression (field <= value)."""
        return self._to_expr(op=OperatorEnum.lte, other=other)

    def in_(self, other: T.Any) -> Expr:
        """Create an 'in' expression (field in [values])."""
        return self._to_expr(op=OperatorEnum.in_, other=other)

    def nin(self, other: T.Any) -> Expr:
        """Create a 'not in' expression (field not in [values])."""
        return self._to_expr(op=OperatorEnum.nin, other=other)

    def exists(self, other: bool) -> Expr:
        """Create an existence check expression (field exists/doesn't exist)."""
        return self._to_expr(op=OperatorEnum.exists, other=other)


class MetaClass(type):
    """
    Metaclass that scans class definitions for MetaKey fields and registers them.

    This metaclass automatically processes class definitions to:
    1. Collect MetaKey fields from base classes (supporting inheritance)
    2. Scan for annotated and non-annotated MetaKey fields in the current class
    3. Ensure all MetaKey instances have proper field names
    4. Store field information on the class for runtime access

    The metaclass enables the declarative syntax where you can define metadata
    fields as class attributes and they become queryable at runtime.
    """

    def __new__(mcs, name, bases, namespace, **kwargs):
        """
        Create a new metadata class with registered MetaKey fields.

        Args:
            mcs: The metaclass
            name: The name of the class being created
            bases: Base classes
            namespace: Class namespace containing attributes and methods
            **kwargs: Additional keyword arguments

        Returns:
            The newly created class with _model_fields attribute
        """
        # Collect all field definitions
        fields = {}

        # Collect fields from all base classes (supporting inheritance)
        for base in reversed(bases):
            if hasattr(base, "_model_fields"):
                fields.update(base._model_fields)

        # Scan current class annotations for field definitions
        if "__annotations__" in namespace:
            for field_name, field_type in namespace["__annotations__"].items():
                # Check if there's a corresponding MetaKey instance as default value
                if field_name in namespace:
                    field_value = namespace[field_name]
                    if isinstance(field_value, MetaKey):
                        # Ensure MetaKey has the correct name
                        if not field_value.name:
                            field_value.name = field_name
                        fields[field_name] = field_value

        # Scan class attributes for MetaKey instances (supports non-annotated definitions)
        for field_name, field_value in namespace.items():
            if isinstance(field_value, MetaKey) and field_name not in fields:
                # Ensure MetaKey has the correct name
                if not field_value.name:
                    field_value.name = field_name
                fields[field_name] = field_value

        # Create the class
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        # Store field information on the class
        cls._model_fields = fields

        return cls


class BaseMetadata(metaclass=MetaClass):
    """
    Base class for metadata models providing field access and query functionality.

    This class serves as the foundation for creating metadata models with queryable
    fields. It automatically manages MetaKey instances and provides runtime access
    to fields defined in the class definition.

    Features:
    - Automatic field registration through the MetaClass metaclass
    - Instance-level field access with independent MetaKey objects
    - Support for inheritance of fields from parent classes
    - Dynamic field access through __getattr__

    Example:
        >>> class DocumentMeta(BaseMetadata):
        ...     document_id = MetaKey()
        ...     status = MetaKey()
        ...
        >>> meta = DocumentMeta()
        >>> query = meta.document_id.eq("doc-1") & meta.status.eq("active")
    """

    def __init__(self):
        """
        Initialize the metadata instance with independent field copies.

        Creates a copy of each MetaKey field for this instance to avoid
        shared state between different instances of the same metadata class.
        """
        # Create field copies for each instance to avoid shared state
        for field_name, field_obj in self._model_fields.items():
            # Create a field copy ensuring each instance has independent field objects
            field_copy = MetaKey(name=field_obj.name)
            setattr(self, field_name, field_copy)

    def __getattr__(self, name):
        """
        Provide dynamic access to registered metadata fields.

        This method is called when accessing an attribute that doesn't exist
        on the instance. It checks if the requested attribute is a registered
        metadata field and creates an appropriate MetaKey instance.

        Args:
            name: The name of the attribute being accessed

        Returns:
            A MetaKey instance for the requested field

        Raises:
            AttributeError: If the requested attribute is not a registered field
        """
        # If accessing a defined field, return the corresponding MetaKey object
        if name in self._model_fields:
            # If the field doesn't exist on the instance yet, create one
            field_copy = MetaKey(name=self._model_fields[name].name)
            setattr(self, name, field_copy)
            return field_copy

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )
