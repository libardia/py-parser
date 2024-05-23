'''Functions that return parsers.'''

from typing import Callable


def take_n(n: int) -> Callable:
    '''Returns a parser that takes the first n characters of a string. Fails
    if fewer characters remain.'''
    def take_n_parser(input: str) -> tuple[str | None, str]:
        if len(input) >= n:
            return input[:n], input[n:]
        return None, input
    return take_n_parser


def get_in(character_set: str) -> Callable:
    def get_in_parser(input: str) -> tuple[str | None, str]:
        if len(input) > 0 and input[0] in character_set:
            return input[0], input[1:]
        return None, input
    return get_in_parser
