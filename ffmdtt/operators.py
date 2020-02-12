from ffmdtt import ast

operators_high = [
    "*",
    "/"
]

operators_low = [
    "+",
    "-"
]

ari_operators = [
    "add",
    "sub",
    "div",
    "mul",
]

log_operators = [
    "and",
    "or",
    "xor",
]


def is_ari_op(op: ast.BinaryOp):
    return op.name in ari_operators
