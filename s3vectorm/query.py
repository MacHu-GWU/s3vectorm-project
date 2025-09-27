# -*- coding: utf-8 -*-

import typing as T
import enum
import dataclasses


class OperatorEnum(str, enum.Enum):
    """
    Ref:

    - https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-metadata-filtering.html#s3-vectors-metadata-filtering-filterable
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
    field: str = dataclasses.field()
    operator: str = dataclasses.field()
    value: T.Any = dataclasses.field()

    def __and__(self, other: "Expr") -> "CompoundExpr":
        """支持 & 操作符进行 AND 逻辑"""
        return CompoundExpr(left=self, operator="$and", right=other)

    def __or__(self, other: "Expr") -> "CompoundExpr":
        """支持 | 操作符进行 OR 逻辑"""
        return CompoundExpr(left=self, operator="$or", right=other)

    def to_doc(self) -> dict:
        return {self.field: {self.operator: self.value}}


@dataclasses.dataclass
class CompoundExpr:
    left: T.Union["Expr", "CompoundExpr"] = dataclasses.field()
    operator: str = dataclasses.field()  # "$and" or "$or"
    right: T.Union["Expr", "CompoundExpr"] = dataclasses.field()

    def __and__(self, other: T.Union[Expr, "CompoundExpr"]) -> "CompoundExpr":
        """支持链式 AND 操作"""
        return CompoundExpr(left=self, operator=OperatorEnum.and_.value, right=other)

    def __or__(self, other: T.Union[Expr, "CompoundExpr"]) -> "CompoundExpr":
        """支持链式 OR 操作"""
        return CompoundExpr(left=self, operator=OperatorEnum.or_.value, right=other)

    def to_doc(self) -> dict:
        return {self.operator: [self.left.to_doc(), self.right.to_doc()]}


@dataclasses.dataclass
class MetaKey:
    name: str = dataclasses.field(default="")

    def _to_expr(self, op: OperatorEnum, other: T.Any) -> Expr:
        return Expr(
            field=self.name,
            operator=op.value,
            value=other,
        )

    def eq(self, other: T.Any) -> Expr:
        return self._to_expr(op=OperatorEnum.eq, other=other)

    def ne(self, other: T.Any) -> Expr:
        return self._to_expr(op=OperatorEnum.ne, other=other)

    def gt(self, other: T.Any) -> Expr:
        return self._to_expr(op=OperatorEnum.gt, other=other)

    def gte(self, other: T.Any) -> Expr:
        return self._to_expr(op=OperatorEnum.gte, other=other)

    def lt(self, other: T.Any) -> Expr:
        return self._to_expr(op=OperatorEnum.lt, other=other)

    def lte(self, other: T.Any) -> Expr:
        return self._to_expr(op=OperatorEnum.lte, other=other)

    def in_(self, other: T.Any) -> Expr:
        return self._to_expr(op=OperatorEnum.in_, other=other)

    def nin(self, other: T.Any) -> Expr:
        return self._to_expr(op=OperatorEnum.nin, other=other)

    def exists(self, other: bool) -> Expr:
        return self._to_expr(op=OperatorEnum.exists, other=other)


class MetaClass(type):
    """元类：扫描类定义中的 MetaKey 注解，创建查询字段"""

    def __new__(mcs, name, bases, namespace, **kwargs):
        # 收集所有字段定义
        fields = {}

        # 从所有基类收集字段（支持继承）
        for base in reversed(bases):
            if hasattr(base, "_model_fields"):
                fields.update(base._model_fields)

        # 扫描当前类的注解和字段定义
        if "__annotations__" in namespace:
            for field_name, field_type in namespace["__annotations__"].items():
                # 检查是否有对应的 MetaKey 实例作为默认值
                if field_name in namespace:
                    field_value = namespace[field_name]
                    if isinstance(field_value, MetaKey):
                        # 确保 MetaKey 有正确的名称
                        if not field_value.name:
                            field_value.name = field_name
                        fields[field_name] = field_value

        # 扫描类属性中的 MetaKey 实例（支持无注解的定义）
        for field_name, field_value in namespace.items():
            if isinstance(field_value, MetaKey) and field_name not in fields:
                # 确保 MetaKey 有正确的名称
                if not field_value.name:
                    field_value.name = field_name
                fields[field_name] = field_value

        # 创建类
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        # 将字段信息保存到类上
        cls._model_fields = fields

        # print(f"✅ {name} 注册的字段: {list(fields.keys())}")

        return cls


class BaseMetadata(metaclass=MetaClass):
    """基础模型类：提供字段访问和查询功能"""

    def __init__(self):
        # 为每个实例创建字段副本，避免共享状态
        for field_name, field_obj in self._model_fields.items():
            # 创建字段的副本，确保每个实例都有独立的字段对象
            field_copy = MetaKey(name=field_obj.name)
            setattr(self, field_name, field_copy)

    def __getattr__(self, name):
        # 如果访问的是已定义的字段，返回对应的 MetaKey 对象
        if name in self._model_fields:
            # 如果实例上还没有这个字段，创建一个
            field_copy = MetaKey(name=self._model_fields[name].name)
            setattr(self, name, field_copy)
            return field_copy

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )
