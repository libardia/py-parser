from typing import Callable, Any

type ParseResultString = tuple[str | None, str]
type ParserString = Callable[[str], ParseResultString]

type ParseResultInt = tuple[int | None, str]
type ParserInt = Callable[[str], ParseResultInt]

type ParseResultAny = tuple[Any | None, str]
type ParserAny = Callable[[str], ParseResultAny]

type ParseResultList = tuple[list | None, str]
type ParserListAny = Callable[[str], ParseResultList]
