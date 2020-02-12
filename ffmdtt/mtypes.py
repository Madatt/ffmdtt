from typing import List, Dict
from dataclasses import dataclass
from ffmdtt import ast

bi_types = [
    "f32",
    "s32",
    "u32",
    "s16",
    "u16",
    "s8",
    "u8",
    "void",
]

float_types = [
    "f32",
    "s32",
]

int_types = [
    "s32",
    "u32",
    "s16",
    "u16",
    "s8",
    "u8",
]


def is_int_type(typ: ast.Type):
    return typ.name in int_types


def is_float_type(typ: ast.Type):
    return typ.name in float_types


def any_pointer(typ1: ast.Type, typ2: ast.Type):
    return typ1.pointer or typ2.pointer


def ill_pointer_op(typ1: ast.Type, typ2: ast.Type):
    if typ1.pointer and typ2.pointer:
        return True

    if is_int_type(typ1) and not typ1.pointer and typ2.pointer or \
            is_int_type(typ2) and not typ2.pointer and typ1.pointer:
        return False

    return False


def is_bi_type_str(typ: str):
    if typ in bi_types:
        return True

    return False


def is_bi_type(typ: ast.Type):
    if typ.name in bi_types:
        return True

    return False


def get_higher_type(typ1: ast.Type, typ2: ast.Type):
    if typ1.pointer and not typ2.pointer:
        return typ1
    elif not typ1.pointer and typ2.pointer:
        return typ2
    elif typ1.pointer and typ2.pointer:
        raise Exception("Illegal pointer arithmetic.")

    if not is_bi_type(typ1) or not is_bi_type(typ2):
        raise Exception("Cannot determine higher type. One of them is not bi.")

    if bi_types.index(typ1.name) < bi_types.index(typ2.name):
        return typ1

    return typ2
