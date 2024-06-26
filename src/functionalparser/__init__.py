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

type ParserNone = Callable[[str], ParseResultNone]
type ParseResultNone = tuple[bool, None, str]

type ParserFinalized = Callable[[str], ParseResultFinalized]
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
     parser. Always returns ``True`` as the status."""

    def star_parser(in_str: str) -> ParseResultList:
        results = []
        success, result, rest = parser(in_str)
        while success:
            results.append(result)
            success, result, rest = parser(rest)
        return True, results, rest

    return star_parser


def star_join(parser: ParserString) -> ParserString:
    """Returns a parser that repeats the given string parser until it fails, returning a string of the results of the
    inner parser joined together. Effectively equivalent to '*' in regex, matching zero or more.

    **NOTE:** Because it can match zero results, the new parser is never considered to have failed.
    :param parser: The parser to be acted on.
    :returns: A new parser, whose result is a (possibly empty) string. Always returns ``True`` as the status."""

    def star_join_parser(in_str: str) -> ParseResultString:
        joined_result = ''
        success, result, rest = parser(in_str)
        while success:
            joined_result += result
            success, result, rest = parser(rest)
        return True, joined_result, rest

    return star_join_parser


def optional(parser: ParserAny) -> ParserAny:
    """Returns a new parser that is identical to the input parser, but is always considered to have succeeded.
    :param parser: The parser to be acted on.
    :returns: A new parser, which always returns ``True`` as its success status, but otherwise is identical to the input
     parser."""

    def optional_parser(in_str: str) -> ParseResultAny:
        _, result, rest = parser(in_str)
        return True, result, rest

    return optional_parser


def chain(*parsers: ParserAny, skip_none_result: bool = False) -> ParserList:
    """Returns a new parser that executes the given parsers one after another. If any one of the inner parsers fails,
    this parser completely fails. Throws ``ValueError`` if no parsers are passed.
    :param parsers: Any number of input parsers of any type. They will be executed in the order provided in the
     arguments.
    :param skip_none_result: If ``True``, when a parser succeeds but returns ``None``, that won't be included in the
     result list of chain. Defaults to ``True``.
    :returns: A new parser, whose result is a list holding the results of each input parser in order, or ``None`` if
     any of the input parsers failed."""
    if len(parsers) == 0:
        raise ValueError(f'Must pass at least one parser to {chain.__name__}.')

    def chain_parser(in_str: str) -> ParseResultList:
        results = []
        rest = in_str
        for p in parsers:
            success, result, rest = p(rest)
            if not success:
                return False, None, in_str
            if result is not None or not skip_none_result:
                results.append(result)
        return True, results, rest

    return chain_parser


def chain_join(*parsers: ParserString) -> ParserString:
    """Returns a new parser that executes the given string parsers one after another, returning the results joined as a
    single new string. If any one of the inner parsers fails, this parser completely fails. Throws ``ValueError`` if no
    parsers are passed.
    :param parsers: Any number of input parsers of any type. They will be executed in the order provided in the
     arguments.
    :returns: A new parser, whose result is a string of the results of each input parser in order joined together, or
     ``None`` if any of the input parsers failed."""
    if len(parsers) == 0:
        raise ValueError(f'Must pass at least one parser to {chain_join.__name__}.')

    def chain_parser_join(in_str: str) -> ParseResultString:
        joined_result = ''
        rest = in_str
        for p in parsers:
            success, result, rest = p(rest)
            if not success:
                return False, None, in_str
            if result is not None:
                joined_result += result
        return True, joined_result, rest

    return chain_parser_join


def any_of(*parsers: ParserAny, at_least_one: bool = True):
    """Returns a parser that executes each given parser in order, and returns the results from the first one that
    succeeds. If none succeed, this parser fails, unless ``at_least_one`` is set to ``False``.
    :param parsers: Any number of input parsers of any type. They will be executed in the order provided in the
     arguments.
    :param at_least_one: If ``True``, the returned parser fails if none of the input parsers succeed. If ``False``, it
     will succeed anyway. Defaults to ``True``."""
    if len(parsers) == 0:
        raise ValueError(f'Must pass at least one parser to {any_of.__name__}.')

    def any_of_parser(in_str: str) -> ParseResultAny:
        for parser in parsers:
            success, result, rest = parser(in_str)
            if success:
                return success, result, rest
        return not at_least_one, None, in_str

    return any_of_parser


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


def fails(parser: ParserAny) -> ParserNone:
    """Returns a parser that succeeds if the input parser fails. As a consequence, this parser always returns no result
    and the entire input string.
    :param parser: The parser to be acted on.
    :returns: A parser that returns nothing, but succeeds when the input parser fails, and vice-versa."""

    def fails_parser(in_str: str) -> ParseResultNone:
        success, _, _ = parser(in_str)
        return not success, None, in_str

    return fails_parser


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


def eof(in_str: str) -> ParseResultNone:
    """"Parses" EOF. That is, succeeds if the input string is empty. Never returns a result.
    :param in_str: The input string being parsed.
    :returns: A tuple whose first element is a boolean representing if the parser succeeded, the second element is
     ``None``, and the third element is the unparsed input."""
    return in_str == '', None, in_str


def noop(in_str: str) -> ParseResultNone:
    """Does nothing, but succeeds.
    :param in_str: The input string being parsed.
    :returns: A tuple of: ``True``, ``None``, ``in_str``"""
    return True, None, in_str


def parse_int(in_str: str) -> ParseResultInt:
    """Parses an integer from the beginning of the input.
    :param in_str: The input string being parsed.
    :returns: A tuple whose first element is a boolean representing if the parser succeeded, the second element is the
     result of the parser, and the third element is the remaining unparsed input. If this parser fails, its second
     element will be ``None`` and its third element will be the entire input."""
    int_parser = transform(
        chain_join(
            any_of(get('-'), get('+'), at_least_one=False),
            star_join(digit)
        ),
        int
    )
    return int_parser(in_str)
