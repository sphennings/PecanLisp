"""Tokens

This module defines the tokens datatype and how to scan source code
into tokens

"""

from dataclasses import dataclass
from enum import Enum, auto


class UnexpectedCharacterException(Exception):
    """An unexpected character was encounterd while scanning the
    soruce code"""


class TokenType(Enum):
    """The types of tokens in pecan lisp"""

    LPAREN = auto()
    RPAREN = auto()
    SYMBOL = auto()
    NUMBER = auto()
    EOF = auto()


@dataclass
class Token:
    """Dataclass for tokens in pecan lisp"""

    type: TokenType
    lexeme: str
    literal: float | str | None
    line: int

    def __repr__(self) -> str:
        representation = f"{self.type.name} line: {self.line}, lexeme: {self.lexeme}"
        if self.literal is not None:
            representation = representation + f" literal: {self.literal}"
        return representation


def scan(src: str) -> list[Token]:
    """Takes a source string and produces a list of tokens"""
    scanner = Scanner(src)
    return scanner.scan()


class Scanner:
    """The class that actually does the scanning"""

    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan(self):
        """Start scanning the source"""
        while not self.is_at_end():
            # We're at the beginning of a lexeme
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        """Consumes the next character and creates a token if necessary"""
        # TODO: Use structural pattern matching instead
        char = self.advance()
        if char == "(":
            self.add_token(TokenType.LPAREN)
        elif char == ")":
            self.add_token(TokenType.RPAREN)
        elif char in " \r\t":
            pass
        elif char == "\n":
            self.line += 1
        elif char.isdigit():
            self.number()
        else:
            self.symbol()

    def number(self):
        """Consumes numeric characters to create a single number token"""
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
        """Consumes characters to creats a single symbol token"""
        while self.peek() not in ") \n" and not self.is_at_end():
            self.advance()

        self.add_token(TokenType.SYMBOL, self.source[self.start : self.current])

    def is_at_end(self):
        """Checks to see if we're at the end of the source or not"""
        return self.current >= len(self.source)

    def advance(self) -> str:
        """Returns the current character, then advances one character"""
        char = self.source[self.current]
        self.current += 1
        return char

    def peek(self) -> str:
        """Returns the current character without advancing"""
        if self.is_at_end():
            return "\0"

        return self.source[self.current]

    def peek_next(self) -> str:
        """Returns the next character without advancing"""
        if (self.current + 1) >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def add_token(self, token_type: TokenType, literal: str | float | None = None):
        """Creates a  token of the appropriate type and adds it to the list of tokens"""
        text = self.source[self.start : self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))
