from functionalparser.combinators import chain, transform
from functionalparser.parsers import parse_int, all_whitespace


def main() -> None:
    print(f'{parse_int('test')=}')
    print(f'{parse_int('896847 stuff')=}')
    two_ints = transform(
        chain(
            parse_int, all_whitespace, parse_int
        ),
        lambda x: [x[i] for i in (0, 2)]
    )
    print(f'{two_ints('00034 230')=}')


if __name__ == '__main__':
    main()
