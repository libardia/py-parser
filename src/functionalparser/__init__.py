"""
*A Parser for Things*

*Is a function from Strings*

*To a list of pairs of Things and Strings*

*(we're just doing one tho ok? ok)*

####

All parsers (except 'finalize', see docs) are always of the form:

parser(input: str) -> tuple[Optional[Any], str]

Where the first output is the parsed object, and the second output is any remaining unparsed output.

If parsing fails, the first output will be None, and the second output will be the entire input.


"""

from enum import Enum
from typing import Callable, Any, Optional

type ParseResultAny = tuple[Optional[Any], str]
type ParserAny = Callable[[str], ParseResultAny]

type ParseResultString = tuple[Optional[str], str]
type ParserString = Callable[[str], ParseResultString]

type ParseResultInt = tuple[Optional[int], str]
type ParserInt = Callable[[str], ParseResultInt]

type ParseResultList = tuple[Optional[list], str]
type ParserList = Callable[[str], ParseResultList]


class IgnoreWhitespaceType(Enum):
    """Describes where whitespace should be ignored around a given item."""
    BEFORE = 0
    AFTER = 1
    AROUND = 2


# COMBINATORS ==========================================================================================================


def star(parser: ParserAny) -> ParserList:
    """Returns a parser that repeats the given parser until it fails, returning a list of the results of the inner
    parser. Effectively equivalent to '*' in regex, matching zero or more.

    **NOTE:** Because it can return zero results, the new parser returns an empty list rather than None and therefore is
    never considered to have failed.
    :param parser: The parser to be acted on.
    :returns: A new parser, whose result is a (possibly empty) list holding the same type as the result of the input
    parser. Never has None as a result."""

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
    this parser completely fails.
    :param parsers: Any number of input parsers of any type. They will be executed in the order provided in the
    arguments.
    :returns: A new parser, whose result is a list holding the results of each input parser in order, or None if any of
    the input parsers failed."""

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
    """Returns a parser that performs the given transformation on the result of another parser.
    :param parser: The parser to be acted on.
    :param transformer: A callable taking one argument and returning a value. This will be applied to the result of the
    input parser.
    :returns: A new parser, whose result is the result of the input parser after transformation. Fails when the input
    parser fails."""

    def transform_parser(in_str: str) -> ParseResultAny:
        result, rest = parser(in_str)
        if result is not None:
            result = transformer(result)
        return result, rest

    return transform_parser


def ignore_whitespace(parser: ParserAny,
                      ignore_whitespace_type: IgnoreWhitespaceType = IgnoreWhitespaceType.BEFORE) -> ParserAny:
    """Returns a parser that is identical to the given parser, except it consumes and discards all whitespace before,
    after, or both (by default, only before). This is achieved using the all_whitespace parser.
    :param parser: The parser to be acted on.
    :param ignore_whitespace_type: An enum describing where whitespace should be ignored.
    :returns: A new parser, whose result is only the result of the input parser, with leading and/or trailing whitespace
    excluded."""

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


def finalize(parser: ParserAny, *, allow_unparsed_remaining: bool = False) -> Callable[[str], Optional[Any]]:
    """Returns a parser that returns *ONLY* the result (or None if the input parser failed), and throws an error if any
    unparsed input remains. Optionally, this error can be disabled.
    :param parser: The parser to be acted on.
    :param allow_unparsed_remaining: Keyword argument only. If True, no error is thrown if unparsed input remains after
    the input parser has been executed. Defaults to False.
    :returns: A parser whose only return value is the result of the input parser (or None if the input parser failed),
    and possibly throws a ValueError if unparsed input remains."""

    def finalize_parser(in_str: str) -> Optional[Any]:
        result, rest = parser(in_str)
        if result is not None and len(rest) != 0 and not allow_unparsed_remaining:
            raise ValueError(f'')
        return result

    return finalize_parser


# GENERATORS ===========================================================================================================

def take_n(n: int) -> ParserString:
    """Returns a parser that takes the first n characters of the input. Fails if fewer characters remain.
    :param n: The number of characters to take from the input.
    :returns: A new parser."""

    def take_n_parser(in_str: str) -> ParseResultString:
        if len(in_str) >= n:
            return in_str[:n], in_str[n:]
        return None, in_str

    return take_n_parser


def get_in(character_set: str) -> ParserString:
    """Returns a parser that takes the first character, if it appears in the given string.
    :param character_set: The list of characters that the output parser should consider.
    :returns: A new parser."""

    def get_in_parser(in_str: str) -> ParseResultString:
        if len(in_str) > 0 and in_str[0] in character_set:
            return in_str[0], in_str[1:]
        return None, in_str

    return get_in_parser


# PARSERS ==============================================================================================================


def digit(in_str: str) -> ParseResultString:
    """Gets the first character of the string if numeric.
    :param in_str: The input string being parsed.
    :returns: A tuple whose first element is the result of the parser, and whose second input is the remaining unparsed
    input. If this parser fails, its first element will be None and its second element will be the entire input."""
    return get_in('0123456789')(in_str)


def single_whitespace(in_str: str) -> ParseResultString:
    """Gets the first character of the string if it is whitespace.
    :param in_str: The input string being parsed.
    :returns: A tuple whose first element is the result of the parser, and whose second input is the remaining unparsed
    input. If this parser fails, its first element will be None and its second element will be the entire input."""
    if len(in_str) > 0 and in_str[0].isspace():
        return in_str[0], in_str[1:]
    return None, in_str


def all_whitespace(in_str: str) -> ParseResultString:
    """Gets as much whitespace as possible from the beginning of the string.
    :param in_str: The input string being parsed.
    :returns: A tuple whose first element is the result of the parser, and whose second input is the remaining unparsed
    input. If this parser fails, its first element will be None and its second element will be the entire input."""
    return star(single_whitespace)(in_str)


def parse_int(in_str: str) -> ParseResultInt:
    """Parses an integer from the beginning of the input.
    :param in_str: The input string being parsed.
    :returns: A tuple whose first element is the result of the parser, and whose second input is the remaining unparsed
    input. If this parser fails, its first element will be None and its second element will be the entire input."""
    digits, rest = star(digit)(in_str)
    if len(digits) > 0:
        return int(''.join(digits)), rest
    return None, in_str
