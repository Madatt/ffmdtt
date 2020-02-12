from typing import List, Dict
from ffmdtt import mtoken
from ffmdtt import ast
from ffmdtt import operators
from ffmdtt import mtypes


def is_float(x: str):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True


def is_int(x: str):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b


class Parser:
    def __init__(self):
        self.buffer: List[mtoken.Name] = []
        self.root: ast.Root = ast.Root({}, [], None, 0, {})
        self.root.parent = self.root
        self.current_block: ast.Block = self.root

    def peek(self, n: int = 0) -> mtoken.MToken:
        if len(self.buffer) - n <= 0:
            return mtoken.MToken("None", "None")
        return self.buffer[n]

    def pop(self) -> mtoken.MToken:
        if len(self.buffer) <= 0:
            return mtoken.MToken("None", "None")
        return self.buffer.pop(0)

    def eat(self, val: str, token_type: str = "None"):
        val2 = self.pop().value
        if val2 is None or val2 != val or (val2 and token_type != "None"):
            raise Exception("Unexpected token: '" + str(val2) + "', expected: '" + val + "'.")

    def parse_return(self):
        self.eat("return")
        return ast.Return(self.parse_expr())

    def parse_term(self):
        if self.peek().value == "(":
            self.pop()
            e = self.parse_expr()
            self.eat(")")
            return e

        if self.peek(1).value == "(":
            return self.parse_fun_call()
        if self.peek().value == ";":
            return ast.ExpressionEmpty(ast.Type("void", 0))

        t = self.peek()
        if is_int(t.value):
            self.pop()
            return ast.Int(ast.Type("u32", 0), int(t.value))
        if is_float(t.value):
            self.pop()
            return ast.Float(ast.Type("f32", 0), float(t.value))

        n = self.pop().value

        if not self.current_block.has_var(n) and not self.current_block.has_arg(n):
            raise Exception("Var '" + n + "' is not defined.")

        return ast.VarCall(ast.Type("void", 0), n)

    def parse_expr2(self):
        e = self.parse_term()
        s1 = self.peek()
        while s1.value in operators.operators_high:
            s1 = self.peek()
            if s1.value == "*":
                self.pop()
                e = ast.BinaryOp(ast.Type("void", 0), "mul", e, self.parse_term())

                if mtypes.any_pointer(e.arg1.expr_type, e.arg2.expr_type):
                    raise Exception("Illegal pointer arithmetic")
            elif s1.value == "/":
                self.pop()
                e = ast.BinaryOp(ast.Type("void", 0), "div", e, self.parse_term())

                if mtypes.any_pointer(e.arg1.expr_type, e.arg2.expr_type):
                    raise Exception("Illegal pointer arithmetic")
        return e

    def parse_expr(self):
        e = self.parse_expr2()
        s1 = self.peek()
        while s1.value in operators.operators_low:
            s1 = self.peek()
            if s1.value == "+":
                self.pop()
                e = ast.BinaryOp(ast.Type("void", 0), "add", e, self.parse_expr2())

                if mtypes.ill_pointer_op(e.arg1.expr_type, e.arg2.expr_type):
                    raise Exception("Illegal pointer arithmetic")
            elif s1.value == "-":
                self.pop()
                e = ast.BinaryOp(ast.Type("void", 0), "sub", e, self.parse_expr2())

                if mtypes.ill_pointer_op(e.arg1.expr_type, e.arg2.expr_type):
                    raise Exception("Illegal pointer arithmetic")

        self.determine_expr_type(e)
        return e

    def determine_expr_type(self, e: ast.Expression):
        if isinstance(e, ast.VarCall):
            if self.current_block.has_var(e.name):
                e.expr_type = self.current_block.get_var(e.name).var_type
            elif isinstance(self.current_block, ast.Function) and self.current_block.has_arg(e.name):
                e.expr_type = self.current_block.get_arg(e.name).var_type
            else:
                raise Exception("Cannot determine type of the variable '" + e.name + "'.")
        elif isinstance(e, ast.FunctionCall):
            if self.root.has_function(e.name):
                e.expr_type = self.root.functions[e.name].fun_type
            else:
                raise Exception("Cannot determine type of the function '" + e.name + "'.")
        elif isinstance(e, ast.BinaryOp):
            self.determine_expr_type(e.arg1)
            self.determine_expr_type(e.arg2)
            e.expr_type = mtypes.get_higher_type(e.arg1.expr_type, e.arg2.expr_type)

    def parse_fun_call(self):
        n = self.pop().value

        if not self.root.has_function(n):
            raise Exception("Undefined reference to function '" + n + "'.")

        args: List[ast.Expression] = []
        self.eat("(")
        while True:
            args.append(self.parse_expr())
            if self.peek().value == ")":
                break

            self.eat(";")
        self.eat(")")

        return ast.FunctionCall(ast.Type("void", 0), n, args)

    def parse_block(self):
        ii: int = self.current_block.start_index
        self.eat("{")
        nxt = self.peek()
        nxt2 = self.peek(1)

        while nxt.value != "}":
            print(nxt.value + " " + nxt2.value)
            if nxt.value == "return":
                r = self.parse_return()
                self.current_block.statements.append(r)
                self.eat(";")
            elif nxt.value == "if":
                self.pop()
                self.eat("(")
                ex = self.parse_expr()
                self.eat(")")
                b = ast.If({}, [], self.current_block, ii, ex)
                self.current_block = b
                self.parse_block()
                self.current_block = b.parent
                self.current_block.statements.append(b)
            elif nxt2.value == "(":
                f = self.parse_fun_call()
                self.current_block.statements.append(f)
                self.eat(";")
            elif nxt2.value == "=":
                vs = self.parse_var_set()
                self.current_block.statements.append(vs)
                self.eat(";")
            else:
                v = self.parse_var_dec()
                v.index = ii
                ii += 1
                if self.current_block.has_var(v.name):
                    raise Exception("Var '" + v.name + "' already declared.")

                self.current_block.add_var(v)
                if self.peek().value == "=":
                    self.pop()
                    e = self.parse_expr()
                    self.current_block.statements.append(ast.VarSet(v.name, e))
                self.eat(";")
            nxt = self.peek()
            nxt2 = self.peek(1)

        self.eat("}")
        return self.current_block

    def parse_var_set(self):
        n = self.pop().value
        self.eat("=")
        e = self.parse_expr()
        return ast.VarSet(n, e)

    def parse_var_dec(self):
        t = self.parse_type()
        n = self.pop().value
        return ast.Var(n, t, 0)

    def parse_type(self):
        n = ast.Type(self.pop().value, 0)
        if not mtypes.is_bi_type(n):
            raise Exception("Undefined type '" + n.name + "'.")

        while self.peek().value == "*":
            self.pop()
            n.pointer += 1

        return n

    def parse_fun(self) -> ast.Function:
        ii: int = 0
        t = self.parse_type()
        n = self.pop().value
        f = ast.Function({}, [], self.root, 0, n, t, {}, 0)

        self.eat("(")

        while True:
            if self.peek().value == ")":
                break

            v = self.parse_var_dec()
            if f.has_arg(v.name):
                raise Exception("Arg '" + v.name + "' already declared.")
            v.index = ii
            ii += 1
            f.args[v.name] = v

            if self.peek().value == ")":
                break

            self.eat(";")

        self.eat(")")

        self.current_block = f
        self.parse_block()
        self.current_block = f.parent
        return f

    def parse(self):
        while self.peek().token_type != "None":
            if self.peek().value == "def":
                self.eat("def")
                f = self.parse_fun()
                self.root.functions[f.name] = f
