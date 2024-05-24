"""Functions that combine or otherwise modify parsers to create new ones."""

from typing import Callable, Any

from functionalparser.parsetypes import ParserAny, ParseResultList, ParserList, ParseResultAny


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
