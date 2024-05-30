from typing import Type
from unittest import TestCase

from functionalparser import *


def tp_take(in_str: str) -> ParseResultString:
    """Defined here completely independently of the module for testing purposes."""
    if len(in_str) > 0:
        return True, in_str[0], in_str[1:]
    return False, None, in_str


def tp_get(prefix: str) -> ParserString:
    """Defined here completely independently of the module for testing purposes."""

    def tp_get_parser(in_str: str) -> ParseResultString:
        if in_str.startswith(prefix):
            return True, prefix, in_str[len(prefix):]
        return False, None, in_str

    return tp_get_parser


def tp_int(in_str: str) -> ParseResultInt:
    """Defined here completely independently of the module for testing purposes."""
    if len(in_str) == 0:
        return False, None, in_str

    try:
        return True, int(in_str[0]), in_str[1:]
    except ValueError:
        return False, None, in_str


def tp_noop(succeed: bool) -> ParserNone:
    """Defined here completely independently of the module for testing purposes."""
    return lambda x: (succeed, None, x)


class TestCombinators(TestCase):
    def test_star(self):
        expectations: list[tuple[ParserString, str, ParseResultList]] = [
            (tp_take, 'test', (True, ['t', 'e', 's', 't'], '')),
            (tp_take, 'abc', (True, ['a', 'b', 'c'], '')),
            (tp_take, 'a', (True, ['a'], '')),
            (tp_take, '', (True, [], '')),
            (tp_get('test'), 'test hello', (True, ['test'], ' hello')),
            (tp_get('a'), 'bbb', (True, [], 'bbb')),
            (tp_get('a'), 'aabbb', (True, ['a', 'a'], 'bbb')),
            (tp_get('ab'), 'ababbbb', (True, ['ab', 'ab'], 'bbb')),
        ]
        for parser, in_str, expected in expectations:
            with self.subTest(star.__name__,
                              parser=parser, in_str=in_str, expected=expected):
                self.assertEqual(star(parser)(in_str), expected)

    def test_optional(self):
        expectations: list[tuple[ParserString, str, ParseResultList]] = [
            (tp_take, '', (True, None, '')),
            (tp_take, 'a', (True, 'a', '')),
            (tp_get('test'), 'testtest', (True, 'test', 'test')),
            (tp_get('test'), 'hellotest', (True, None, 'hellotest')),
            (tp_get('a'), 'ab', (True, 'a', 'b')),
            (tp_get('a'), 'ba', (True, None, 'ba')),
        ]
        for parser, in_str, expected in expectations:
            with self.subTest(optional.__name__,
                              parser=parser, in_str=in_str, expected=expected):
                self.assertEqual(optional(parser)(in_str), expected)

    def test_chain(self):
        expectations: list[tuple[list[ParserString], Optional[bool], str, ParseResultList]] = [
            ([tp_take, tp_get('test')], False, 'atestb', (True, ['a', 'test'], 'b')),
            ([tp_take, tp_get('test')], False, 'atest', (True, ['a', 'test'], '')),
            ([tp_take, tp_get('test')], False, 'ab', (False, None, 'ab')),
            ([tp_get('a'), tp_get('b'), tp_get('c')], False, 'abc', (True, ['a', 'b', 'c'], '')),
            ([tp_get('a'), tp_noop(True), tp_get('b')], True, 'abc', (True, ['a', 'b'], 'c')),
            ([tp_get('a'), tp_noop(True), tp_get('b')], False, 'abc', (True, ['a', None, 'b'], 'c')),
            ([tp_get('a'), tp_noop(True), tp_get('b')], None, 'abc', (True, ['a', None, 'b'], 'c')),
            ([tp_get('a'), tp_get('b'), tp_get('c')], False, 'abc.', (True, ['a', 'b', 'c'], '.')),
            ([tp_get('a'), tp_get('b'), tp_get('c')], False, '_bc.', (False, None, '_bc.')),
            ([tp_get('a'), tp_get('b'), tp_get('c')], False, 'a_c.', (False, None, 'a_c.')),
            ([tp_get('a'), tp_get('b'), tp_get('c')], False, 'ab_.', (False, None, 'ab_.')),
        ]
        for parsers, skip_none, in_str, expected in expectations:
            with self.subTest(chain.__name__,
                              parsers=parsers, skip_none=skip_none, in_str=in_str, expected=expected):
                if skip_none is None:
                    self.assertEqual(chain(*parsers)(in_str), expected)
                else:
                    self.assertEqual(chain(*parsers, skip_none_result=skip_none)(in_str), expected)
        with self.subTest('when called with no args, ValueError is raised'):
            self.assertRaises(ValueError, chain)

    def test_transform(self):
        expectations: list[tuple[ParserAny, Callable, str, ParseResultAny]] = [
            (tp_get('test test'), lambda x: x.split(' '), 'test test and more', (True, ['test', 'test'], ' and more')),
            (tp_get('test'), lambda x: x * 2, 'test test and more', (True, 'testtest', ' test and more')),
            (tp_take, lambda x: int(x) * 2, '4ab', (True, 8, 'ab')),
            (tp_take, lambda x: int(x) * 2, '0ab', (True, 0, 'ab')),
            (tp_take, lambda x: int(x) * 2, '1', (True, 2, '')),
            (tp_take, lambda x: list(range(int(x))), '5tests', (True, [0, 1, 2, 3, 4], 'tests')),
            (tp_take, lambda x: list(range(int(x))), '5tests', (True, [0, 1, 2, 3, 4], 'tests')),
        ]
        for parser, transformer, in_str, expected in expectations:
            with self.subTest(transform.__name__,
                              parser=parser, transformer=transformer, in_str=in_str, expected=expected):
                self.assertEqual(transform(parser, transformer)(in_str), expected)
        with self.subTest('when transformer raises error, fails without error'):
            in_str = 'test'
            self.assertEqual((False, None, in_str), transform(tp_take, lambda x: int(x))(in_str))

    def test_ignore_whitespace(self):
        wb = '  \t '
        infix = 'test'
        wa = ' \n    \t\r\n'
        full = wb + infix + wa
        expectations: list[tuple[ParserString, str, ParseResultString]] = [
            (ignore_whitespace(tp_get(infix), IgnoreWhitespaceType.AROUND), full, (True, infix, '')),
            (ignore_whitespace(tp_get(infix), IgnoreWhitespaceType.BEFORE), full, (True, infix, wa)),
            (ignore_whitespace(tp_get(infix), IgnoreWhitespaceType.AFTER), full, (False, None, full)),
            (ignore_whitespace(tp_get(infix), IgnoreWhitespaceType.AFTER), infix + wa, (True, infix, '')),
            (ignore_whitespace(tp_get(infix)), full, (True, infix, wa)),
        ]
        for parser, in_str, expected in expectations:
            with self.subTest(ignore_whitespace.__name__,
                              parser=parser, in_str=in_str, expected=expected):
                self.assertEqual(parser(in_str), expected)

    def test_finalize(self):
        expectations: list[tuple[ParserAny, bool, str, Optional[Any], Optional[Type[Exception]]]] = [
            (tp_int, False, '3', 3, None),
            (tp_int, True, '3_ignore_this', 3, None),
            (tp_int, False, '3_this_is_bad', None, ValueError),
            (tp_int, True, 'what?', None, ValueError),
            (tp_int, False, 'what?', None, ValueError),
            (tp_get('test'), False, 'test', 'test', None),
            (tp_get('test'), True, 'test fine', 'test', None),
            (tp_get('test'), False, 'test nope', None, ValueError),
            (tp_get('test'), True, 'bad', None, ValueError),
            (tp_get('test'), False, 'bad', None, ValueError),
        ]
        for parser, allow_remaining, in_str, expected, exception in expectations:
            with self.subTest(finalize.__name__,
                              parser=parser, allow_remaining=allow_remaining, in_str=in_str, expected=expected,
                              exception=exception):
                if exception:
                    self.assertRaises(exception, finalize(parser, allow_unparsed_remaining=allow_remaining), in_str)
                else:
                    self.assertEqual(finalize(parser, allow_unparsed_remaining=allow_remaining)(in_str), expected)

    def test_any_of(self):
        expectations: list[tuple[list[ParserAny], Optional[bool], str, ParseResultAny]] = [
            ([tp_get('test'), tp_int, tp_take], True, 'test and more', (True, 'test', ' and more')),
            ([tp_get('test'), tp_int, tp_take], True, '5 and more', (True, 5, ' and more')),
            ([tp_get('test'), tp_int, tp_take], True, '? and more', (True, '?', ' and more')),
            ([tp_get('test'), tp_int, tp_get('other')], True, '? and more', (False, None, '? and more')),
            ([tp_get('test'), tp_int, tp_get('other')], False, '? and more', (True, None, '? and more')),
            ([tp_get('test')], True, 'test and more', (True, 'test', ' and more')),
            ([tp_get('test')], False, 'test and more', (True, 'test', ' and more')),
            ([tp_get('test')], True, '? and more', (False, None, '? and more')),
            ([tp_get('test')], False, '? and more', (True, None, '? and more')),
        ]
        for parsers, at_least_one, in_str, expected in expectations:
            with self.subTest(any_of.__name__,
                              parsers=parsers, at_least_one=at_least_one, in_str=in_str, expected=expected):
                if at_least_one is not None:
                    self.assertEqual(any_of(*parsers, at_least_one=at_least_one)(in_str), expected)
                else:
                    self.assertEqual(any_of(*parsers)(in_str), expected)
        with self.subTest('when called with no args, ValueError is raised'):
            self.assertRaises(ValueError, any_of)
        for at_least_one in (True, False):
            with self.subTest(f'when called with no parsers and at_least_one={at_least_one}, ValueError is raised'):
                self.assertRaises(ValueError, any_of, at_least_one=at_least_one)

    def test_fails(self):
        expectations: list[tuple[ParserAny, str, bool]] = [
            (tp_take, '', True),
            (tp_take, 'g', False),
            (tp_take, 'ggh', False),
            (tp_int, '5', False),
            (tp_int, 'guh', True),
        ]
        for parser, in_str, expected in expectations:
            with self.subTest(fails.__name__,
                              parser=parser, in_str=in_str, expected=expected):
                self.assertEqual(fails(parser)(in_str), (expected, None, in_str))
