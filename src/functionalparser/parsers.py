'''
All parsers are always of the form:

`parser(input: str) -> tuple[Any | None, str]`

Where the first output is the parsed object, and the second output is any remaining unparsed output.

If parsing fails, the first output will be `None`, and the second output will be the entire input.
'''

##################################################
##################################################
###            A Parser for Things             ###
###         Is a function from Strings         ###
###  To a list of pairs of Things and Strings  ###
###     (we're just doing one tho ok? ok)      ###
##################################################
##################################################

from functionalparser.combinators import star
from functionalparser.generators import get_in


def digit(input: str) -> tuple[str | None, str]:
    '''Gets the first character of the string if numeric.'''
    return get_in('0123456789')(input)



def parse_int(input: str) -> tuple[int | None, str]:
        digits, rest = star(digit)(input)
        if digits is not None:
            return int(''.join(digits)), rest
        return None, input
