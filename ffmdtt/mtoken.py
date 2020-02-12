from dataclasses import dataclass


@dataclass
class MToken:
    value: str
    token_type: str


@dataclass
class Name(MToken):
    token_type: str = "Name"


@dataclass
class Keyword(MToken):
    token_type: str = "Keyword"


@dataclass
class Int(MToken):
    token_type: str = "Float"


@dataclass
class Float(MToken):
    token_type: str = "Int"


@dataclass
class Symbol(MToken):
    token_type: str = "Symbol"
