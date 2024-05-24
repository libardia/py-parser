"""Functions that return parsers."""

from functionalparser.parsetypes import ParserString, ParseResultString


def take_n(n: int) -> ParserString:
    """Returns a parser that takes the first n characters of a string. Fails
    if fewer characters remain."""
    def take_n_parser(in_str: str) -> ParseResultString:
        if len(in_str) >= n:
            return in_str[:n], in_str[n:]
        return None, in_str
    return take_n_parser


def get_in(character_set: str) -> ParserString:
    def get_in_parser(in_str: str) -> tuple[str | None, str]:
        if len(in_str) > 0 and in_str[0] in character_set:
            return in_str[0], in_str[1:]
        return None, in_str
    return get_in_parser
