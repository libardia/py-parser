import functionalparser.parsers as p
import functionalparser.generators as g
import functionalparser.combinators as c


def main() -> None:
    print(f'{p.parse_int('test')=}')
    print(f'{p.parse_int('896847 sdfglkj')=}')


if __name__ == '__main__':
    main()
