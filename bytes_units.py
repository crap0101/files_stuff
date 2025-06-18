
from decimal import Decimal
from math import trunc
import operator
import re


###########
# CLASSES #
###########

class MetaBytes(type):
    def __new__(cls, name, bases, dct):
        def eq (self, other):
            return self.BASE == other.BASE and self.UNIT_SYMBOLS == other.UNIT_SYMBOLS
        c = super().__new__(cls, name, bases, dct)
        c.__eq__ = eq
        c.__str__ = lambda self: name
        for exp, u in enumerate(c.UNIT_SYMBOLS):
            c.EXP_SYM[u] = c.BASE ** exp
        for u in c.UNIT_SYMBOLS:
            setattr(c, u, u)
        return c

class SIBytes(metaclass=MetaBytes):
    BASE = 1000
    SYMBOL = "B"
    UNIT_SYMBOLS = ("B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB", "RB", "QB")
    EXP_SYM: dict[str,int] = {}


class IECBytes(metaclass=MetaBytes):
    BASE = 1024
    SYMBOL = "B"
    UNIT_SYMBOLS = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB", "RiB", "QiB")
    EXP_SYM: dict[str,int] = {}

class MEMBytes(metaclass=MetaBytes):
    BASE = 1024
    SYMBOL = "B"
    UNIT_SYMBOLS = ("B", "KB", "MB", "GB", "TB")
    EXP_SYM: dict[str,int] = {}


#####################
# UTILITY FUNCTIONS #
#####################

def format_num (n, decs='2'):
    """Get rid of some annoiyng outputs in scientific notation of string.format()"""
    import math
    decimal = '0' if trunc(n) == n else decs
    return '{:.{}f}'.format(n, decimal)

# unused... keep here anyway :)
def decimals_threshold (n, precision=4):
    """...to consider equals two numbers under a certain precision"""
    exp = 10 ** precision
    n = abs(n)
    r =  (n - int(n)) * exp
    return True if (n - int(n)) * exp < 1 else False

def nearest_mapval (value, mapping, cmpfunc=None):
    """
    Finds the *value*'s nearest value inside *mapping*.
    Return a pair with the the associated key and the
    distance between the given *value* and the found one.
    *cmpfunc* is the comparison function between *value* and
    the mapping's values as `func(mapping_value, value)` and
    must returns something that can be sorted(). If None,
    use a default cmp func which returns abs(mapping_value - value).
    """
    d = {}
    if cmpfunc is None:
        def cmpfunc (a, b):
            return abs(a - b)
    for k, v in mapping.items():
        d[k] = cmpfunc(v, value)
    return sorted(d.items(),key=lambda p:p[1])[0]


def string_to_bytes (string: str,
                     standard: MetaBytes = SIBytes,
                     with_suffix: bool = False) -> int|tuple[int,str,bool]:
    """
    Returns the number of bytes (as integer) represented by *string*.
    NOTE: float values may be truncated... at some point :D
    *standard* is the class used to do the conversion (MEMBytes, IECBytes,
    SIBytes, the latter is the default).
    If *with_suffix* is a true value, returns a tuple of (bytes, "suffix", got_suffix),
    the latter a bool indicating if the input *string* already contains a suffix.
    Raises ValueError if something went wrong.
    """
    def get_bytes (match, exp_value):
        numstr, suffix = match.groups()
        if re.fullmatch('\d+', numstr):
            conv = int
        else:
            conv = float
        try:
            return int(conv(numstr) * exp_value)
        except ValueError:
            raise ValueError(f'string <{string}>: wrong value: <{numstr}>') from None
        except OverflowError:
            raise ValueError('<{}> is too big!'.format(numstr)) from None
    # find the unit
    for suffix, exp_value in reversed(standard.EXP_SYM.items()):
        if match := re.fullmatch('(.+?)({})'.format(suffix), string):
            b = get_bytes(match, exp_value)
            return (b, suffix, True) if with_suffix else b
    else:
        # NOTE: bare numbers without suffix
        try:
            b = int(float(string))
            return (b, standard.SYMBOL, False) if with_suffix else b
        except ValueError:
            raise ValueError(f'wrong value: <{string}>') from None
    #raise ValueError(f'string {string}: unknown unit suffix') # should never happens


class BytesUnit:
    """
    Numeric methods:
        Supported operations:
            +, -, *, **, /, //, %, and the relatives augmented arithmetic assignments.
            Also supports +, - and abs() unary arithmetic operations.
            Also implements the built-in function round() and math functions floor() and ceil().
        Applied to two BytesUnit objects, the resultant object retains the symbol
        and the standard class of the first operand.
        These operations can also be applied with ints, which are treathen as a
        BytesUnit of the same unit, so:
          >>> BytesUnit(2,'TiB') * 3
          6TiB
          >>> 
        __r*__ methods called only for non BytesUnit objects.
    """
    BYTES_CLASSES = (SIBytes, IECBytes, MEMBytes) 
    def __init__ (self,
                  value:    int|float|str,
                  unit:     str|None = None,
                  standard: MetaBytes = IECBytes):
        if standard not in self.BYTES_CLASSES:
            raise ValueError(f'Unknown standard value: {standard}')

        if (unit is not None) and (unit not in standard.UNIT_SYMBOLS):
            raise ValueError(f'Unknown unit: "{unit}"')

        self._standard = standard
        self._symbol = unit
        self._value = None

        # transform string value, with an optional suffix (assumed "B" otherwise)
        if isinstance(value, str):
            try:
                _bytes, _symbol, _got_suffix = string_to_bytes(value, self._standard, True)
                if self._symbol is None:
                    self._symbol = _symbol
                    self._value = _bytes / self._standard.EXP_SYM[self._symbol]
                elif _got_suffix:
                    raise TypeError(f"Double unit indication: '{unit}' and '{value}'")
                else:
                    # no byte suffix in the string
                    self._value = _bytes
            except ValueError:
                try:
                    int(float(value))
                    self._value = float(value)
                except OverflowError:
                    raise ValueError(f'<{value}> is too big!') from None
                except ValueError:
                    raise ValueError(f'wrong value: <{value}>') from None
            except TypeError as e:
                raise e
        elif isinstance(value, int):
            self._value = value
        else:
            # got a non string number, anything for which int() and float()
            # can be applied, checks for owerflows.
            try:
                int(float(value))
                self._value = float(value)
            except OverflowError:
                raise ValueError(f'<{value}> is too big!') from None
        if self._symbol is None:
            self._symbol =self._standard.SYMBOL

    @property
    def bytes (self):
        return self._value * self.exp
    @property
    def value (self):
        return self._value
    @property
    def exp (self):
        return self.standard.EXP_SYM[self.symbol]
    @property
    def symbol (self):
        return self._symbol
    @symbol.setter
    def symbol (self, sym):
        """
        Changes the unit symbol to *sym* (a bytes unit of the same standard).
        >>> yy == BytesUnit(2, 'TiB')
        >>> yy
        2TiB
        >>> yy.symbol = 'GiB'
        >>> yy
        2048GiB
        """
        if sym not in self.standard.UNIT_SYMBOLS:
            raise ValueError(f'Unknown symbol "{sym}"')
        if sym != self._symbol:
            self._value = self.bytes / self.standard.EXP_SYM[sym]
            self._symbol = sym
    @property
    def standard (self):
        return self._standard
    def __str__ (self):
        """NOTE: may be an approximation of the real value."""
        try:
            return f'{format_num(self.value)}{self.symbol}'
        except OverflowError: # too big for a float...
            try:
                return f'{self.value}{self.symbol}'
            except ValueError: # too big to be printed
                return '{:.2g}{}'.format(Decimal(self.value), self.symbol)
    __repr__ = __str__

    ######################
    # comparison methods #
    ######################
    def __eq__ (self, other):
        """Compare equals with istances of BytesUnit with the same value and bytes class."""
        try:
            return self.standard == other.standard and self.bytes == other.bytes
        except (AttributeError, TypeError):
            return False
    def __ne__ (self, other):
        return not (self == other)
    def __lt__ (self, other):
        try:
            return self.standard == other.standard and self.bytes < other.bytes
        except (AttributeError, TypeError):
            raise TypeError(f"'<' not supported between instances of"
                            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'") from None
    def __le__ (self, other):
        try:
            return self.standard == other.standard and self.bytes <= other.bytes
        except (AttributeError, TypeError):
            raise TypeError(f"'<=' not supported between instances of"
                            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'") from None
    def __gt__ (self, other):
        try:
            return self.standard == other.standard and self.bytes > other.bytes
        except (AttributeError, TypeError):
            raise TypeError(f"'>' not supported between instances of"
                            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'") from None
    def __ge__ (self, other):
        try:
            return self.standard == other.standard and self.bytes >= other.bytes
        except (AttributeError, TypeError):
            raise TypeError(f"'>=' not supported between instances of"
                            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'") from None  

    ###################
    # numeric methods #
    ###################
    def __add__ (self, other):
        try:
            if isinstance(other, (int, float)):
                return BytesUnit(self.value + other, self.symbol, self.standard)
            else:
                return BytesUnit(self.value + (other.bytes / self.exp), self.symbol, self.standard)
        except (AttributeError, TypeError) as e:
            raise TypeError(f"not supported operand type(s) for +:"
                            f"'{self.__class__.__name__}' and '{other.__class__.__name__}': {e}") from None  
    def __radd__ (self, other):
        try:
            return BytesUnit(other + self.value, self.symbol, self.standard)
        except (AttributeError, TypeError) as e:
            raise TypeError(f"__radd__: not supported operand type(s) for +:"
                            f"'{self.__class__.__name__}' and '{other.__class__.__name__}': {e}") from None
    def __truediv__ (self, other):
        try:
            if isinstance(other, (int, float)):
                return BytesUnit(self.value / other, self.symbol, self.standard)
            else:
                return BytesUnit(self.value / (other.bytes / self.exp), self.symbol, self.standard)
        except (AttributeError, TypeError):
            raise TypeError(f"not supported operand type(s) for /:"
                            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'") from None
    def __rtruediv__ (self, other):
        try:
            return BytesUnit(other / self.value, self.symbol, self.standard)
        except (AttributeError, TypeError):
            raise TypeError(f"not supported operand type(s) for /:"
                            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'") from None
    def __floordiv__ (self, other):
        try:
            if isinstance(other, (int, float)):
                return BytesUnit(self.value // other, self.symbol, self.standard)
            else:
                return BytesUnit(self.value // (other.bytes / self.exp), self.symbol, self.standard)
        except (AttributeError, TypeError):
            raise TypeError(f"not supported operand type(s) for /:"
                            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'") from None
    def __rfloordiv__ (self, other):
        try:
            return BytesUnit(other // self.value, self.symbol, self.standard)
        except (AttributeError, TypeError):
            raise TypeError(f"not supported operand type(s) for /:"
                            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'") from None
    def __mod__ (self, other):
        try:
            if isinstance(other, (int, float)):
                return BytesUnit(self.value % other, self.symbol, self.standard)
            else:
                return BytesUnit(self.value % (other.bytes / self.exp), self.symbol, self.standard)
        except (AttributeError, TypeError):
            raise TypeError(f"not supported operand type(s) for %:"
                            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'") from None
    def __rmod__ (self, other):
        try:
            return BytesUnit(other % self.value, self.symbol, self.standard)
        except (AttributeError, TypeError):
            raise TypeError(f"not supported operand type(s) for %:"
                            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'") from None
    def __mul__ (self, other):
        try:
            if isinstance(other, (int, float)):
                return BytesUnit(self.value * other, self.symbol, self.standard)
            else:
                return BytesUnit(self.value * (other.bytes / self.exp), self.symbol, self.standard)
        except (AttributeError, TypeError):
            raise TypeError(f"not supported operand type(s) for *:"
                            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'") from None
    def __rmul__ (self, other):
        try:
            return BytesUnit(other * self.value, self.symbol, self.standard)
        except (AttributeError, TypeError):
            raise TypeError(f"not supported operand type(s) for *:"
                            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'") from None
    def __pow__ (self, other):
        try:
            if isinstance(other, (int, float)):
                return BytesUnit(self.value ** other, self.symbol, self.standard)
            else:
                return BytesUnit(self.value ** (other.bytes / self.exp), self.symbol, self.standard)
        except (AttributeError, TypeError):
            raise TypeError(f"not supported operand type(s) for **:"
                            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'") from None
    def __sub__ (self, other):
        """
        NOTE: negative values doesn't make soo much sense in this context,
        nevertheless can be useful in some situations, so negative byte values are allowed.
        """
        try:
            if isinstance(other, (int, float)):
                return BytesUnit(self.value - other, self.symbol, self.standard)
            else:
                return BytesUnit(self.value - (other.bytes / self.exp), self.symbol, self.standard)
        except (AttributeError, TypeError):
            raise TypeError(f"not supported operand type(s) for -:"
                            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'") from None
    def __rsub__ (self, other):
        try:
            return BytesUnit(other - self.value, self.symbol, self.standard)
        except (AttributeError, TypeError):
            raise TypeError(f"not supported operand type(s) for -:"
                            f"'{self.__class__.__name__}' and '{other.__class__.__name__}'") from None
    #########################
    # Numeric unary methods #
    #########################
    def __neg__ (self):
        print("NEG")
        return BytesUnit(- self.value, self.symbol, self.standard)
    def __pos__ (self):
        print("POS")
        return BytesUnit(+ self.value, self.symbol, self.standard)
    def __abs__ (self):
        return BytesUnit(abs(self.value), self.symbol, self.standard)

    ##########################
    # Other numberic methods #
    ##########################
    def __round__ (self, digs=None):
        return BytesUnit(round(self.value, digs), self.symbol, self.standard)
    def __trunc__ (self):
        return BytesUnit(trunc(self.value), self.symbol, self.standard)
    def __floor__ (self):
        return BytesUnit(math.floor(self.value), self.symbol, self.standard)
    def __ceil__ (self):
        return BytesUnit(math.ceil(self.value), self.symbol, self.standard)

    def convert(self, standard, unit=None):
        """
        Returns another BytesUnit, converting self to another
        *standard* MetaBytes class with the given *unit*.
        If *unit* is None, tries to get the best corresponding unit,
        closer to the original.
        """
        if unit is None:
            unit, _ = nearest_mapval(self.exp, standard.EXP_SYM)
        b = BytesUnit(self.bytes, standard=standard)
        b.symbol = unit
        return b
