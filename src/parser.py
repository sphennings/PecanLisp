from tokens import Token, TokenType
from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC, abstractmethod
from collections.abc import Sequence


# Expressions are either a number, a symbol, or a collection of one or more expressions


class ExpressionType(Enum):
    NUMBER = auto()
    SYMBOL = auto()
    LIST = auto()


@dataclass
class S_Expression(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass


class Collection(S_Expression):
    def __init__(self, value: list[S_Expression], token: Token | None = None):
        self.type = ExpressionType.LIST
        self.value = value
        self.token = token

    def __str__(self) -> str:
        return f'( {" ".join([str(x) for x in self.value])} )'

    def __getitem__(self, key):
        return self.value[key]

    def __len__(self) -> int:
        return len(self.value)

    def __eq__(self, other) -> bool:
        return self.value == other


class Atom(S_Expression):
    def __init__(
        self,
        expression_type: ExpressionType,
        value: float | str,
        token: Token | None = None,
    ):
        self.type = expression_type
        self.value = value
        self.token = token

    def __eq__(self, other):
        return self.value == other

    def __bool__(self) -> bool:
        return bool(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)


class ParseError(Exception):
    pass


def parse(tokens: list[Token]) -> list[S_Expression]:
    parser = Parser(tokens)
    return parser.parse()


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> list[S_Expression]:
        expressions: list[S_Expression] = []
        while not self.is_at_end():
            expressions.append(self.expression())
        return expressions

    def expression(self):
        #        breakpoint()
        t = self.pop()
        match t.type:
            case TokenType.LPAREN:
                return self.collection()
            case TokenType.NUMBER:
                return Atom(ExpressionType.NUMBER, t.literal, t)
            case TokenType.SYMBOL:
                return Atom(ExpressionType.SYMBOL, t.literal, t)
            case _:
                raise ParseError(f"Unexpected Token: {t}")

    def collection(self):
        collection = []
        while not self.is_at_end() and self.peek().type != TokenType.RPAREN:
            collection.append(self.expression())

        # Pop the terminal RParenT
        if self.is_at_end():
            raise ParseError(f"Missing ')' after expression")
        _ = self.pop()

        return Collection(collection, None)

    def pop(self) -> Token:
        return self.tokens.pop(0)

    def peek(self) -> Token:
        return self.tokens[0]

    def is_at_end(self):
        return self.peek().type == TokenType.EOF
