from dataclasses import dataclass
from typing import List
from ffmdtt import tokenizer
from ffmdtt import parser
from ffmdtt import mtoken
from ffmdtt import generator

test_str: str = "def f32 add_mul(f32 arg1; u32 arg2)" \
                "{" \
                "u32 c = arg1 * (arg1 + arg2);" \
                "u32 h = c; " \
                "if( c ) {" \
                "u32 f = h + c;" \
                "c = c + c;" \
                "if(f) {" \
                "return f;" \
                "}" \
                "}" \
                "return c;" \
                "}"


test_str2 = open("test.msl").read()

tknz = tokenizer.Tokenizer(test_str2)

print(tknz.output)
prs: parser.Parser = parser.Parser()
prs.buffer = tknz.output
prs.parse()
print(prs.root.functions)
print()
generator.debug_print_bytecode(generator.compile_fun(prs.root.functions["add_mul"]))
