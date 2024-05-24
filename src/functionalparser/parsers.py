"""
*A Parser for Things*

*Is a function from Strings*

*To a list of pairs of Things and Strings*

*(we're just doing one tho ok? ok)*

###############################################

All parsers are always of the form:

parser(input: str) -> tuple[Any | None, str]

Where the first output is the parsed object, and the second output is any remaining unparsed output.

If parsing fails, the first output will be None, and the second output will be the entire input.
"""

from functionalparser.combinators import star
from functionalparser.generators import get_in
from functionalparser.parsetypes import ParseResultString, ParseResultInt


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
