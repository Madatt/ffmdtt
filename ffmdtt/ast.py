from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class AST:
    pass


@dataclass
class Type(AST):
    name: str
    pointer: int


@dataclass
class FunctionType(Type):
    arg_types: List[Type]


@dataclass
class Var(AST):
    name: str
    var_type: Type
    index: int


@dataclass
class Block(AST):
    local_vars: Dict[str, Var]
    statements: List[AST]
    parent: any
    start_index: int

    def has_var(self, n: str):
        if n in self.local_vars:
            return True

        return self.parent.has_var(n)

    def has_arg(self, n: str):
        return self.parent.has_arg(n)

    def get_var(self, n: str):
        if n in self.local_vars:
            return self.local_vars[n]

        return self.parent.get_var(n)

    def get_arg(self, n: str):
        return self.parent.get_arg(n)

    def in_function(self):
        return self.parent.in_function()

    def add_var(self, v: Var):
        self.parent.add_var(v)

    def get_parent_fun(self):
        return self.parent.get_parent_fun()


@dataclass
class Function(Block):
    name: str
    fun_type: Type
    args: Dict[str, Var]
    local_vars = {}
    statements = []
    labels: int

    def has_var(self, n: str):
        return n in self.local_vars

    def has_arg(self, n: str):
        return n in self.args

    def get_var(self, n: str):
        return self.local_vars[n]

    def get_arg(self, n: str):
        return self.args[n]

    def in_function(self):
        return True

    def add_var(self, v: Var):
        self.local_vars[v.name] = v

    def get_parent_fun(self):
        return self


@dataclass
class Root(Block):
    functions: Dict[str, Function]

    def has_function(self, n: str):
        return n in self.functions


@dataclass
class Expression(AST):
    expr_type: Type
    pass


@dataclass
class ExpressionEmpty(Expression):
    pass


@dataclass
class Int(Expression):
    value: int


@dataclass
class Float(Expression):
    value: float


@dataclass
class VarCall(Expression):
    name: str


@dataclass
class BinaryOp(Expression):
    name: str
    arg1: Expression
    arg2: Expression


@dataclass
class VarSet(AST):
    name: str
    expr: Expression


@dataclass
class Return(AST):
    expr: Expression


@dataclass
class FunctionCall(Expression):
    name: str
    args: List[Expression]


@dataclass
class If(Block):
    expr: Expression
