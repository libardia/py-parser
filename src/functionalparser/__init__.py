"""
*A Parser for Things*

*Is a function from Strings*

*To a list of pairs of Things and Strings*

*(we're just doing one tho ok? ok)*

####

All parsers are always of the form:

parser(input: str) -> tuple[Any | None, str]

Where the first output is the parsed object, and the second output is any remaining unparsed output.

If parsing fails, the first output will be None, and the second output will be the entire input.


"""

from enum import Enum
from typing import Callable, Any

type ParseResultAny = tuple[Any | None, str]
type ParserAny = Callable[[str], ParseResultAny]

type ParseResultString = tuple[str | None, str]
type ParserString = Callable[[str], ParseResultString]

type ParseResultInt = tuple[int | None, str]
type ParserInt = Callable[[str], ParseResultInt]

type ParseResultList = tuple[list | None, str]
type ParserList = Callable[[str], ParseResultList]


class IgnoreWhitespaceType(Enum):
    """Describes where whitespace should be ignored around a given item."""
    BEFORE = 0
    AFTER = 1
    AROUND = 2


# COMBINATORS ==========================================================================================================


def star(parser: ParserAny) -> ParserList:
    """Repeats the given parser until it fails, returning a list of the results of the inner parser. Effectively
    equivalent to '*' in regex, matching zero or more.

    **NOTE:** Because it can return zero results, this parser never returns None and therefore is never considered to
    have failed."""

    def star_parser(in_str: str) -> ParseResultList:
        results = []
        result, rest = parser(in_str)
        while result is not None:
            results.append(result)
            result, rest = parser(rest)
        return results, rest

    return star_parser


def chain(*parsers: ParserAny) -> ParserList:
    """Returns a new parser that executes the given parsers one after another. If any one of the inner parsers fails,
    this parser completely fails."""

    def chain_parser(in_str: str) -> ParseResultList:
        results = []
        rest = in_str
        for p in parsers:
            result, rest = p(rest)
            if result is None:
                return None, in_str
            results.append(result)
        return results, rest

    return chain_parser


def transform(parser: ParserAny, transformer: Callable[[Any], Any]) -> ParserAny:
    """Returns a parser that performs the given transformation on the result of another parser."""

    def transform_parser(in_str: str) -> ParseResultAny:
        result, rest = parser(in_str)
        if result is not None:
            result = transformer(result)
        return result, rest

    return transform_parser


def ignore_whitespace(parser: ParserAny,
                      ignore_whitespace_type: IgnoreWhitespaceType = IgnoreWhitespaceType.BEFORE) -> ParserAny:
    """Returns a parser that is identical to the given parser, except it consumes and discards all whitespace before,
    after, or both (by default, only before)."""

    def ignore_whitespace_parser(in_str: str) -> ParseResultAny:
        rest = in_str
        if ignore_whitespace_type in (IgnoreWhitespaceType.BEFORE, IgnoreWhitespaceType.AROUND):
            _, rest = all_whitespace(rest)

        result, rest = parser(rest)

        # If result is none, just end now
        if result is None:
            return None, in_str

        if ignore_whitespace_type in (IgnoreWhitespaceType.AFTER, IgnoreWhitespaceType.AROUND):
            _, rest = all_whitespace(rest)

        return result, rest

    return ignore_whitespace_parser


# GENERATORS ===========================================================================================================

def take_n(n: int) -> ParserString:
    """Returns a parser that takes the first n characters of a string. Fails if fewer characters remain."""

    def take_n_parser(in_str: str) -> ParseResultString:
        if len(in_str) >= n:
            return in_str[:n], in_str[n:]
        return None, in_str

    return take_n_parser


def get_in(character_set: str) -> ParserString:
    """Returns a parser that takes the first character that appears in the given string."""

    def get_in_parser(in_str: str) -> tuple[str | None, str]:
        if len(in_str) > 0 and in_str[0] in character_set:
            return in_str[0], in_str[1:]
        return None, in_str

    return get_in_parser


# PARSERS ==============================================================================================================


def digit(in_str: str) -> ParseResultString:
    """Gets the first character of the string if numeric."""
    return get_in('0123456789')(in_str)


def single_whitespace(in_str: str) -> ParseResultString:
    """Gets the first character of the string if it is whitespace."""
    if len(in_str) > 0 and in_str[0].isspace():
        return in_str[0], in_str[1:]
    return None, in_str


def all_whitespace(in_str: str) -> ParseResultString:
    """Gets as much whitespace as possible from the beginning
    of the string."""
    return star(single_whitespace)(in_str)


def parse_int(in_str: str) -> ParseResultInt:
    """Parses the largest integer possible from the beginning of the input. Specifically, takes as many numeric
    characters as possible and converts that to an int."""
    digits, rest = star(digit)(in_str)
    if len(digits) > 0:
        return int(''.join(digits)), rest
    return None, in_str
