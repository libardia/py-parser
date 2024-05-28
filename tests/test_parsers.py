from unittest import TestCase

from functionalparser import *


class TestParsers(TestCase):
    def test_digit(self):
        expectations: list[tuple[str, ParseResultString]] = []
        expectations += [(f'{i}a', (True, str(i), 'a')) for i in range(10)]
        expectations += [(f'{i}other', (True, str(i), 'other')) for i in range(10)]
        expectations += [(str(i), (True, str(i), '')) for i in range(10)]
        expectations += [
            ('', (False, None, '')),
            ('what?', (False, None, 'what?')),
        ]
        for in_str, expected in expectations:
            with self.subTest(digit.__name__,
                              in_str=in_str, expected=expected):
                self.assertEqual(digit(in_str), expected)

    def test_single_whitespace(self):
        whitespace = ' \t\n\r'
        expectations: list[tuple[str, ParseResultString]] = []
        expectations += [(ws, (True, ws, '')) for ws in whitespace]
        expectations += [(f'{ws}a', (True, ws, 'a')) for ws in whitespace]
        expectations += [(f'{ws}other', (True, ws, 'other')) for ws in whitespace]
        expectations += [
            ('', (False, None, '')),
            ('nope', (False, None, 'nope')),
        ]
        for in_str, expected in expectations:
            with self.subTest(single_whitespace.__name__,
                              in_str=in_str, expected=expected):
                self.assertEqual(single_whitespace(in_str), expected)

    def test_all_whitespace(self):
        expectations: list[tuple[str, ParseResultString]] = [
            ('   \n\ttest', (True, '   \n\t', 'test')),
            (' one', (True, ' ', 'one')),
            ('\t\ttwo', (True, '\t\t', 'two')),
            ('none', (True, '', 'none')),
            ('', (True, '', '')),
        ]
        for in_str, expected in expectations:
            with self.subTest(all_whitespace.__name__,
                              in_str=in_str, expected=expected):
                self.assertEqual(all_whitespace(in_str), expected)

    def test_parse_int(self):
        expectations: list[tuple[str, ParseResultInt]] = [
            ('0', (True, 0, '')),
            ('0a', (True, 0, 'a')),
            ('7', (True, 7, '')),
            ('12', (True, 12, '')),
            ('12 things', (True, 12, ' things')),
            ('-50', (True, -50, '')),
            ('-50 dollars', (True, -50, ' dollars')),
            ('0005', (True, 5, '')),
            ('0001505', (True, 1505, '')),
            ('-00978', (True, -978, '')),
        ]
        for in_str, expected in expectations:
            with self.subTest(parse_int.__name__,
                              in_str=in_str, expected=expected):
                self.assertEqual(parse_int(in_str), expected)
