from unittest import TestCase

from functionalparser import *


class TestGenerators(TestCase):
    def test_take_n(self):
        expectations: list[tuple[int, str, ParseResultString]] = [
            (5, 'aaaaabbb', (True, 'aaaaa', 'bbb')),
            (3, 'aaaaabbb', (True, 'aaa', 'aabbb')),
            (1, 'test', (True, 't', 'est')),
            (4, 'test', (True, 'test', '')),
            (1, '', (False, None, '')),
            (5, 'aaa', (False, None, 'aaa')),
        ]
        for n, in_str, expected in expectations:
            with self.subTest(take_n.__name__,
                              n=n, in_str=in_str, expected=expected):
                self.assertEqual(take_n(n)(in_str), expected)

    def test_get_char_in(self):
        expectations: list[tuple[str, str, ParseResultString]] = [
            ('abc', 'a...', (True, 'a', '...')),
            ('abc', 'b...', (True, 'b', '...')),
            ('abc', 'c...', (True, 'c', '...')),
            ('abc', '?...', (False, None, '?...')),
            ('abc', 'a', (True, 'a', '')),
        ]
        for charset, in_str, expected in expectations:
            with self.subTest(get_char_in.__name__,
                              charset=charset, in_str=in_str, expected=expected):
                self.assertEqual(get_char_in(charset)(in_str), expected)

    def test_get(self):
        expectations: list[tuple[str, str, ParseResultString]] = [
            ('abc', 'abc', (True, 'abc', '')),
            ('abc', 'abc...', (True, 'abc', '...')),
            ('test', 'test message', (True, 'test', ' message')),
            ('test', 'bad message', (False, None, 'bad message')),
        ]
        for prefix, in_str, expected in expectations:
            with self.subTest(get.__name__,
                              prefix=prefix, in_str=in_str, expected=expected):
                self.assertEqual(get(prefix)(in_str), expected)
