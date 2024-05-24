from typing import Callable, Any

type ParseResultAny = tuple[Any | None, str]
type ParserAny = Callable[[str], ParseResultAny]

type ParseResultString = tuple[str | None, str]
type ParserString = Callable[[str], ParseResultString]

type ParseResultInt = tuple[int | None, str]
type ParserInt = Callable[[str], ParseResultInt]

type ParseResultList = tuple[list | None, str]
type ParserList = Callable[[str], ParseResultList]
