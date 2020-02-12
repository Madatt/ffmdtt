from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Code:
    name: str


@dataclass
class Bytecode(Code):
    id: int
    arg1: str
    arg2: str
    arg1_s: int
    arg2_s: int


@dataclass
class Label(Code):
    label: str


def gen_bytecode0(name: str, id: int):
    return Bytecode(
        name,
        id,
        "",
        "",
        0,
        0
    )


def gen_bytecode1(name: str, id: int, arg1: str, arg1_s: int):
    return Bytecode(
        name,
        id,
        arg1,
        "",
        arg1_s,
        0
    )
