from functionalparser import parse_int, chain, ignore_whitespace as iw, finalize, IgnoreWhitespaceType


def main() -> None:
    print(f'{parse_int('test')=}')
    print(f'{parse_int('896847 stuff')=}')
    two_ints = finalize(chain(
        iw(parse_int), iw(parse_int, IgnoreWhitespaceType.AROUND)
    ))
    print(f'{two_ints(' 00034 230 ')=}')


if __name__ == '__main__':
    main()
