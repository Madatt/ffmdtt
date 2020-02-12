import re
from dataclasses import dataclass
from typing import List
from ffmdtt import mtoken

patterns = [
    ("Names", "([a-zA-Z_][a-zA-Z_0-9]*)"),
    ("Number", "([+-]?([0-9]*[.])?[0-9]+)"),
    ("Symbol", "([\\+\\-\\*;\\(\\)])")
]

comp = re.compile("")


class Tokenizer:
    def __init__(self, inp: str):
        self.buffer: str = inp

        self.syntax = [
            r"[a-zA-Z_][a-zA-Z_0-9]*",
            r"[-]?[0-9]+",
            r"[-]?[0-9]+[.][0-9]+",

            r"\+",
            r"\-",
            r"\*",
            r"/",
            r"=",

            r"\(",
            r"\)",
            r"{",
            r"}",
            r";",
        ]

        self.syntax2 = r'(' + r'|'.join(self.syntax) + r')'
        self.pat = re.compile(self.syntax2)

        self.output_raw = re.findall(self.syntax2, self.buffer)
        self.output = [mtoken.MToken(t, "") for t in self.output_raw]


