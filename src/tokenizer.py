import re
from dataclasses import dataclass

_TOKENIZER_SPEC = [
    (r"^(//|#)", "comment"),
    (r"^var", "var"),
    (r"^transform", "transform"),
    (r"^rule", "rule"),
    (r"^axiom", "axiom"),
    (r"^length", "length"),
    (r"^iterate", "iterate"),
    (r"^bias", "bias"),
    (r"^=", "assign"),
    (r"^\[", "["),
    (r"^\]", "]"),
    (r"^\+", "+"),
    (r"^-", "-"),
    (r"^-?(\d+(\.\d+)?|\.\d+)", "num"),
    (r"^[a-zA-Z_]\w*", "id"),
    (r"^;", "eod"),
]

TOKENS_READABLE = {
    "var": "var",
    "assign": "=",
    "num": "number",
    "id": "identifier",
    "eod": ";",
}


@dataclass
class RawToken:
    token_type: str
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


    def get_next_token(self):
        self._buffered_line_cursor = self._line_cursor
        self._buffered_line_number = self._line_number

        if not self.has_more_tokens():
            return None
        
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
                if token_type == "comment":
                    self._advance_to_next_line()
                    return self.get_next_token()
                else:
                    self._incr_cursor(match.end() - match.start())
                    return RawToken(token_type, string[match.start():match.end()])

        raise SyntaxError(f"Unexpected token '{string[0]}' in line {self._line_number}:{self._line_cursor + 1}\n{self.get_error_excerpt()}")
    

    def _incr_cursor(self, inc=1):
        self._cursor += inc
        self._line_cursor += inc
    

    def _advance_to_next_line(self):
        while not self.is_eof() and self._string[self._cursor] != "\n":
            self._incr_cursor()


    def get_pos(self, buffered=False):
        if buffered:
            return self._buffered_line_number, self._buffered_line_cursor + 1
        else:
            return self._line_number, self._line_cursor + 1


    def get_error_excerpt(self, use_buffered_pos=False):
        line_number, line_cursor = self.get_pos(buffered=use_buffered_pos)
        line = self._string.split("\n")[line_number - 1]
        indicator = " " * line_cursor + "^"
        return f"{line}\n{indicator}"

    
    def get_readable(self, string):
        if string in TOKENS_READABLE.keys():
            return TOKENS_READABLE[string]
        return string
