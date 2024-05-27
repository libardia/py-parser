"""
*A Parser for Things*

*Is a function from Strings*

*To a list of pairs of Things and Strings*

*(we're just doing one tho ok? ok)*

####

All parsers (except ``finalize``, see docs) are always of the form:

parser(input: str) -> tuple[bool, Optional[Any], str]

Where the first output is a boolean representing if the parser succeeded, the second is the parsed object, and the
 third is any remaining unparsed output.

If parsing fails, the second output will be ``None``, and the third output will be the entire input.
"""

from enum import Enum
from typing import Callable, Any, Optional

type ParserAny = Callable[[str], ParseResultAny]
type ParseResultAny = tuple[bool, Optional[Any], str]

type ParserString = Callable[[str], ParseResultString]
type ParseResultString = tuple[bool, Optional[str], str]

type ParserInt = Callable[[str], ParseResultInt]
type ParseResultInt = tuple[bool, Optional[int], str]

type ParserList = Callable[[str], ParseResultList]
type ParseResultList = tuple[bool, Optional[list], str]

type ParserFinalized = Callable[[str], Optional[Any]]
type ParseResultFinalized = Optional[Any]


class IgnoreWhitespaceType(Enum):
    """Describes where whitespace should be ignored around a given item."""
    BEFORE = 0
    AFTER = 1
    AROUND = 2


# COMBINATORS ==========================================================================================================


def star(parser: ParserAny) -> ParserList:
    """Returns a parser that repeats the given parser until it fails, returning a list of the results of the inner
    parser. Effectively equivalent to '*' in regex, matching zero or more.

    **NOTE:** Because it can return zero results, the new parser is never considered to have failed.
    :param parser: The parser to be acted on.
    :returns: A new parser, whose result is a (possibly empty) list holding the same type as the result of the input
     parser. Always returns True as the status."""

    def star_parser(in_str: str) -> ParseResultList:
        results = []
        success, result, rest = parser(in_str)
        while success:
            results.append(result)
            success, result, rest = parser(rest)
        return True, results, rest

    return star_parser


def optional(parser: ParserAny) -> ParserAny:
    """Returns a new parser that is identical to the input parser, but is always considered to have succeeded.
    :param parser: The parser to be acted on.
    :returns: A new parser, which always returns ``True`` as its success status, but otherwise is identical to the input
     parser."""

    def optional_parser(in_str: str) -> ParseResultAny:
        _, result, rest = parser(in_str)
        return True, result, rest

    return optional_parser


def chain(*parsers: ParserAny) -> ParserList:
    """Returns a new parser that executes the given parsers one after another. If any one of the inner parsers fails,
    this parser completely fails. Throws ``ValueError`` if no parsers are passed.
    :param parsers: Any number of input parsers of any type. They will be executed in the order provided in the
     arguments.
    :returns: A new parser, whose result is a list holding the results of each input parser in order, or ``None`` if
     any of the input parsers failed."""
    if len(parsers) == 0:
        raise ValueError('Must pass at least one parser to chain.')

    def chain_parser(in_str: str) -> ParseResultList:
        results = []
        rest = in_str
        for p in parsers:
            success, result, rest = p(rest)
            if not success:
                return False, None, in_str
            results.append(result)
        return True, results, rest

    return chain_parser


def transform(parser: ParserAny, transformer: Callable[[Any], Any]) -> ParserAny:
    """Returns a parser that performs the given transformation on the result of another parser.
    :param parser: The parser to be acted on.
    :param transformer: A callable taking one argument and returning a value. This will be applied to the result of the
     input parser.
    :returns: A new parser, whose result is the result of the input parser after transformation. Fails when the input
     parser fails."""

    def transform_parser(in_str: str) -> ParseResultAny:
        success, result, rest = parser(in_str)
        if success:
            try:
                result = transformer(result)
            except Exception:
                return False, None, in_str
        return success, result, rest

    return transform_parser


def ignore_whitespace(parser: ParserAny,
                      ignore_whitespace_type: IgnoreWhitespaceType = IgnoreWhitespaceType.BEFORE) -> ParserAny:
    """Returns a parser that is identical to the given parser, except it consumes and discards all whitespace before,
    after, or both (by default, only before). This is achieved using the ``all_whitespace`` parser.
    :param parser: The parser to be acted on.
    :param ignore_whitespace_type: An enum describing where whitespace should be ignored.
    :returns: A new parser, whose result is only the result of the input parser, with leading and/or trailing whitespace
     excluded."""

    def ignore_whitespace_parser(in_str: str) -> ParseResultAny:
        rest = in_str
        if ignore_whitespace_type in (IgnoreWhitespaceType.BEFORE, IgnoreWhitespaceType.AROUND):
            _, _, rest = all_whitespace(rest)

        success, result, rest = parser(rest)

        # If it failed, just end now
        if not success:
            return False, None, in_str

        if ignore_whitespace_type in (IgnoreWhitespaceType.AFTER, IgnoreWhitespaceType.AROUND):
            _, _, rest = all_whitespace(rest)

        return True, result, rest

    return ignore_whitespace_parser


def finalize(parser: ParserAny, *, allow_unparsed_remaining: bool = False) -> ParserFinalized:
    """Returns a parser that returns *ONLY* the result and throws an error if either the parse failed or any unparsed
    input remains. Optionally, unparsed input may be allowed.
    :param parser: The parser to be acted on.
    :param allow_unparsed_remaining: Keyword argument only. If ``True``, no error is thrown if unparsed input remains
     after the input parser has been executed. Defaults to ``False``.
    :returns: A parser whose only return value is the result of the input parser, and possibly throws a ``ValueError``
     if the input cannot be parsed or if unparsed input remains."""

    def finalize_parser(in_str: str) -> Optional[Any]:
        success, result, rest = parser(in_str)
        if not success:
            raise ValueError(f'Input could not be parsed: {in_str!r}')
        if len(rest) != 0 and not allow_unparsed_remaining:
            raise ValueError(f'Unparsed input remained in a finalized parser: result={result!r}, rest={rest!r}')
        return result

    return finalize_parser


# GENERATORS ===========================================================================================================

def take_n(n: int) -> ParserString:
    """Returns a parser that takes the first n characters of the input. Fails if fewer characters remain.
    :param n: The number of characters to take from the input.
    :returns: A new parser."""

    def take_n_parser(in_str: str) -> ParseResultString:
        if len(in_str) >= n:
            return True, in_str[:n], in_str[n:]
        return False, None, in_str

    return take_n_parser


def get_char_in(character_set: str) -> ParserString:
    """Returns a parser that takes the first character, if it appears in the given string.
    :param character_set: The list of characters that the output parser should consider.
    :returns: A new parser."""

    def get_in_parser(in_str: str) -> ParseResultString:
        if len(in_str) > 0 and in_str[0] in character_set:
            return True, in_str[0], in_str[1:]
        return False, None, in_str

    return get_in_parser


def get(prefix: str) -> ParserString:
    """Returns a parser that extracts the given string from the beginning of the input, if present.
    :param prefix: The string to search for.
    :returns: A parser that extracts the given string from the beginning of the input, if present."""

    def get_parser(in_str: str) -> ParseResultString:
        if in_str.startswith(prefix):
            return True, prefix, in_str[len(prefix):]
        return False, None, in_str

    return get_parser


# PARSERS ==============================================================================================================


def digit(in_str: str) -> ParseResultString:
    """Gets the first character of the string if numeric.
    :param in_str: The input string being parsed.
    :returns: A tuple whose first element is a boolean representing if the parser succeeded, the second element is the
     result of the parser, and the third element is the remaining unparsed input. If this parser fails, its second
     element will be ``None`` and its third element will be the entire input."""
    return get_char_in('0123456789')(in_str)


def single_whitespace(in_str: str) -> ParseResultString:
    """Gets the first character of the string if it is whitespace.
    :param in_str: The input string being parsed.
    :returns: A tuple whose first element is a boolean representing if the parser succeeded, the second element is the
     result of the parser, and the third element is the remaining unparsed input. If this parser fails, its second
     element will be ``None`` and its third element will be the entire input."""
    if len(in_str) > 0 and in_str[0].isspace():
        return True, in_str[0], in_str[1:]
    return False, None, in_str


def all_whitespace(in_str: str) -> ParseResultString:
    """Gets as much whitespace as possible (including none) from the beginning of the string.
    :param in_str: The input string being parsed.
    :returns: A tuple whose first element is a boolean representing if the parser succeeded (which is always ``True`` in
     this case), the second element is the result of the parser, and the third element is the
     remaining unparsed input."""
    return transform(star(single_whitespace), lambda x: ''.join(x))(in_str)


def parse_int(in_str: str) -> ParseResultInt:
    """Parses an integer from the beginning of the input.
    :param in_str: The input string being parsed.
    :returns: A tuple whose first element is a boolean representing if the parser succeeded, the second element is the
     result of the parser, and the third element is the remaining unparsed input. If this parser fails, its second
     element will be ``None`` and its third element will be the entire input."""

    def int_transformer(parse_result: list) -> Optional[int]:
        sign, digits = parse_result
        collected = ''
        if sign == '-':
            collected += sign
        collected += ''.join(digits)
        try:
            return int(collected)
        except ValueError:
            return None

    int_parser = transform(
        chain(
            optional(get('-')), star(digit)
        ),
        int_transformer
    )
    return int_parser(in_str)
