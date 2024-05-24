from functools import partial

from functionalparser import parse_int, chain, ignore_whitespace as iw, finalize, IgnoreWhitespaceType


def main() -> None:
    iw_around = partial(iw, ignore_whitespace_type=IgnoreWhitespaceType.AROUND)

    print(f'{parse_int('test')=}')
    print(f'{parse_int('896847 stuff')=}')
    two_ints = finalize(chain(
        iw(parse_int), iw_around(parse_int)
    ))
    print(f'{two_ints(' 00034 230 ')=}')


if __name__ == '__main__':
    main()
