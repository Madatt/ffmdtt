from typing import List, Dict
from dataclasses import dataclass
from ffmdtt import mtoken
from ffmdtt import ast
from ffmdtt import operators
from ffmdtt import parser
from ffmdtt import bytecode
from ffmdtt import mtypes


def compile_fun(f: ast.Function):
    bc: List[bytecode.Code] = [
        bytecode.Label("Label", f.name)
    ]
    bc += compile_fun_local_vars(f)
    bc += compile_block(f)
    return bc


def compile_fun_local_vars(f: ast.Function):
    bc: List[bytecode.Code] = [
        bytecode.gen_bytecode1("alloc", -1, str(len(f.local_vars.keys())), 8)
    ]

    return bc


def compile_block(f: ast.Block):
    bc: List[bytecode.Code] = []

    for st in f.statements:
        if isinstance(st, ast.VarSet):
            bc += compile_var_set(f, st)
        elif isinstance(st, ast.Return):
            bc += compile_return(f, st)
        elif isinstance(st, ast.If):
            bc += compile_if(st)

    return bc


def compile_if(b: ast.If):
    bc: List[bytecode.Code] = []
    n = b.get_parent_fun().name + "_" + str(b.get_parent_fun().labels)
    b.get_parent_fun().labels += 1

    bc += compile_expr(b, b.expr)
    bc += compile_type_coer(b, b.expr.expr_type, ast.Type("int", 0))

    bc.append(
        bytecode.gen_bytecode1("if_not", -1, n, 8)
    )

    bc += compile_block(b)

    bc.append(
        bytecode.Label("Label", n)
    )

    return bc


def compile_var_set(b: ast.Block, vs: ast.VarSet):
    bc: List[bytecode.Code] = []

    bc += compile_expr(b, vs.expr)

    if b.has_var(vs.name):
        bc += compile_type_coer(b, vs.expr.expr_type, b.get_var(vs.name).var_type)

        bc.append(
            bytecode.gen_bytecode1("set", -1, str(b.get_var(vs.name).index), 8)
        )
    elif b.has_arg(vs.name):
        bc += compile_type_coer(b, vs.expr.expr_type, b.get_arg(vs.name).var_type)

        bc.append(
            bytecode.gen_bytecode1("set_a", -1, str(b.get_arg(vs.name).index), 8)
        )
    return bc


def compile_var_call(b: ast.Block, vc: ast.VarCall):
    bc: List[bytecode.Code] = []

    if b.has_var(vc.name):
        bc.append(
            bytecode.gen_bytecode1("load", -1, str(b.get_var(vc.name).index), 8)
        )
    elif b.has_arg(vc.name):
        bc.append(
            bytecode.gen_bytecode1("load_a", -1, str(b.get_arg(vc.name).index), 8)
        )
    return bc


def compile_return(b: ast.Block, r: ast.Return):
    bc: List[bytecode.Code] = []

    bc += compile_expr(b, r.expr)
    bc += compile_type_coer(b, r.expr.expr_type, b.get_parent_fun().fun_type)
    bc.append(
        bytecode.gen_bytecode0("ret", -1)
    )

    return bc


def compile_expr(b: ast.Block, e: ast.Expression):
    bc: List[bytecode.Code] = []

    if isinstance(e, ast.VarCall):
        bc += compile_var_call(b, e)
    elif isinstance(e, ast.BinaryOp):
        bc += compile_expr(b, e.arg1)
        bc += compile_type_coer(b, e.arg1.expr_type, e.expr_type)
        bc += compile_expr(b, e.arg2)
        bc += compile_type_coer(b, e.arg2.expr_type, e.expr_type)
        bc += compile_bin_op(b, e)
    return bc


def compile_bin_op(b: ast.Block, e: ast.BinaryOp):
    bc: List[bytecode.Code] = []

    if operators.is_ari_op(e):
        if e.expr_type.pointer:
            bc.append(
                bytecode.gen_bytecode0("u32" + e.name, -1)
            )
        else:
            bc.append(
                bytecode.gen_bytecode0(e.expr_type.name + e.name, -1)
            )

    return bc


def compile_type_coer(b: ast.Block, e: ast.Type, t: ast.Type):
    bc: List[bytecode.Code] = []

    if mtypes.is_float_type(e) and not e.pointer and not t.pointer and mtypes.is_int_type(t):
        bc.append(
            bytecode.gen_bytecode0("ftoi", -1)
        )
    elif mtypes.is_int_type(e) and not e.pointer and not t.pointer and mtypes.is_float_type(t):
        bc.append(
            bytecode.gen_bytecode0("itof", -1)
        )

    return bc


def debug_print_bytecode(bc: List[bytecode.Code]):
    for b in bc:
        if isinstance(b, bytecode.Label):
            print(b.label + ":")
        elif isinstance(b, bytecode.Bytecode):
            print("    " + b.name + "    " + b.arg1 + "    " + b.arg2)
