from functionalparser.parsetypes import ParserAny, ParseResultList, ParserListAny


def star(parser: ParserAny) -> ParserListAny:
    def star_parser(in_str: str) -> ParseResultList:
        results = []
        result, rest = parser(in_str)
        while result is not None:
            results.append(result)
            result, rest = parser(rest)
        if results:
            return results, rest
        return None, in_str
    return star_parser
