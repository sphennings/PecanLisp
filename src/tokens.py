from dataclasses import dataclass
from enum import Enum, auto


class UnexpectedCharacterException(Exception):
    pass


class TokenType(Enum):
    LPAREN = auto()
    RPAREN = auto()
    SYMBOL = auto()
    NUMBER = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: float | str | None
    line: int

    def __repr__(self) -> str:
        repr = f"{self.type.name} line: {self.line}, lexeme: {self.lexeme}"
        if self.literal is not None:
            repr = repr + f" literal: {self.literal}"
        return repr


class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        while not self.is_at_end():
            # We're at the beginning of a lexeme
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        c = self.advance()
        if c == "(":
            self.add_token(TokenType.LPAREN)
        elif c == ")":
            self.add_token(TokenType.RPAREN)
        elif c in " \r\t":
            pass
        elif c == "\n":
            self.line += 1
        elif c.isdigit():
            self.number()
        else:
            self.symbol()

    def number(self):
        while self.peek().isdigit():
            self.advance()

        # Look for a fractional part
        if self.peek() == "." and self.peek_next().isdigit():
            # Consume the '.'
            self.advance()

        while self.peek().isdigit():
            self.advance()

        self.add_token(TokenType.NUMBER, float(self.source[self.start : self.current]))

    def symbol(self):
        while self.peek() not in ") \n" and not self.is_at_end():
            self.advance()

        self.add_token(TokenType.SYMBOL, self.source[self.start : self.current])

    def is_at_end(self):
        return self.current >= len(self.source)

    def advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        return c

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"

        return self.source[self.current]

    def peek_next(self) -> str:
        if (self.current + 1) >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def add_token(self, token_type: TokenType, literal: str | float | None = None):
        text = self.source[self.start : self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))
