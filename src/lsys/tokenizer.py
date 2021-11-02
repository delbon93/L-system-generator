import re
from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    COMMENT = auto()
    VAR = auto()
    TRANSFORM = auto()
    RULE = auto()
    AXIOM = auto()
    LENGTH = auto()
    ITERATE = auto()
    BIAS = auto()
    ROTATE = auto()
    TRANSLATE = auto()
    RAD = auto()
    DEG = auto()
    ASSIGN = auto()
    OPEN_BRACKET = auto()
    CLOSE_BRACKET = auto()
    OPEN_PAREN = auto()
    CLOSE_PAREN = auto()
    NUM = auto()
    PLUS = auto()
    MINUS = auto()
    ASTERISK = auto()
    SLASH = auto()
    IDENTIFIER = auto()
    COMMA = auto()
    SEMICOLON = auto()
    EOF = auto()


_KEYWORDS = [
    TokenType.VAR, TokenType.TRANSFORM, TokenType.RULE, TokenType.AXIOM, TokenType.LENGTH, TokenType.ITERATE, 
    TokenType.BIAS, TokenType.ROTATE, TokenType.TRANSLATE, TokenType.DEG, TokenType.RAD,
]

_TOKENIZER_SPEC = [
    (r"^(//|#)", TokenType.COMMENT),
    (r"^var", TokenType.VAR),
    (r"^transform", TokenType.TRANSFORM),
    (r"^rule", TokenType.RULE),
    (r"^axiom", TokenType.AXIOM),
    (r"^length", TokenType.LENGTH),
    (r"^iterate", TokenType.ITERATE),
    (r"^bias", TokenType.BIAS),
    (r"^rotate", TokenType.ROTATE),
    (r"^translate", TokenType.TRANSLATE),
    (r"^rad", TokenType.RAD),
    (r"^deg", TokenType.DEG),
    (r"^=", TokenType.ASSIGN),
    (r"^\[", TokenType.OPEN_BRACKET),
    (r"^\]", TokenType.CLOSE_BRACKET),
    (r"^\(", TokenType.OPEN_PAREN),
    (r"^\)", TokenType.CLOSE_PAREN),
    (r"^(\d+(\.\d+)?|\.\d+)", TokenType.NUM),
    (r"^\+", TokenType.PLUS),
    (r"^-", TokenType.MINUS),
    (r"^\*", TokenType.ASTERISK),
    (r"^/", TokenType.SLASH),
    (r"^[a-zA-Z_]\w*", TokenType.IDENTIFIER),
    (r"^,", TokenType.COMMA),
    (r"^;", TokenType.SEMICOLON),
]


@dataclass
class RawToken:
    token_type: TokenType
    value: str


class Tokenizer:
    """ Lazily pulls a token from a stream """

    def initialize(self, string):
        self._string: str = string
        self._cursor: int = 0
        self._line_number: int = 1
        self._line_cursor: int = 0
        self._buffered_line_number: int = self._line_number
        self._buffered_line_cursor: int = self._line_cursor


    def has_more_tokens(self) -> bool:
        return self._cursor < len(self._string)
    

    def is_eof(self) -> bool:
        return self._cursor == len(self._string)


    def get_next_token(self) -> RawToken:
        self._buffered_line_cursor = self._line_cursor
        self._buffered_line_number = self._line_number

        if not self.has_more_tokens():
            return TokenType.EOF
        
        # get string from cursor position and remove leading whitespace
        string = self._string[self._cursor:]
        while string[0] in " \n":
            self._incr_cursor()
            if string[0] == "\n":
                self._line_number += 1
                self._line_cursor = 0
            string = string[1:]
        
        # try to read a token
        for rx, token_type in _TOKENIZER_SPEC:
            match = re.search(rx, string)
            if match:
                if token_type in _KEYWORDS:
                    # TODO rework this incredibly dirty hack!
                    token_length = len(str(token_type).split(".")[1])
                    if self._cursor + token_length < len(self._string):
                        next_char = self._string[self._cursor + token_length]
                        if self._is_id_char(next_char):
                            continue
                if token_type == TokenType.COMMENT:
                    self._advance_to_next_line()
                    return self.get_next_token()
                else:
                    self._incr_cursor(match.end() - match.start())
                    return RawToken(token_type, string[match.start():match.end()])

        raise SyntaxError(f"Unexpected token '{string[0]}' in line {self._line_number}:{self._line_cursor + 1}\n{self.get_error_excerpt()}")
    

    def _is_id_char(self, char) -> bool:
        return re.search(char, r"^[a-zA-Z0-9_]$") != None

    def _incr_cursor(self, inc=1):
        self._cursor += inc
        self._line_cursor += inc
    

    def _advance_to_next_line(self):
        while not self.is_eof() and self._string[self._cursor] != "\n":
            self._incr_cursor()


    def get_pos(self, buffered=False) -> tuple[int, int]:
        if buffered:
            return self._buffered_line_number, self._buffered_line_cursor + 1
        else:
            return self._line_number, self._line_cursor + 1


    def get_error_excerpt(self, use_buffered_pos=False) -> str:
        line_number, line_cursor = self.get_pos(buffered=use_buffered_pos)
        line = self._string.split("\n")[line_number - 1]
        indicator = " " * line_cursor + "^"
        return f"{line}\n{indicator}"

