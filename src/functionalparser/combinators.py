from typing import Callable, Any


def star(parser: Callable) -> Callable:
    def star_parser(input: str) -> tuple[list[Any] | None, str]:
        results = []
        result, rest = parser(input)
        while result is not None:
            results.append(result)
            result, rest = parser(rest)
        if results:
            return results, rest
        return None, input
    return star_parser
