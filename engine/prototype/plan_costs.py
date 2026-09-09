"""Break-even arithmetic for one explicitly chosen cost unit at a time.

Callers supply measured complete costs; this module does not estimate tokens or
convert bytes/time to money. None denotes unknown, never zero. Constant recurring
cost is an assumption of this calculation, not a prediction of future workload.
"""
from decimal import Decimal, InvalidOperation
from fractions import Fraction


def _cost(value):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise ValueError('Cost must be a finite nonnegative number or None')
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError('Invalid cost') from exc
    if not number.is_finite() or number < 0:
        raise ValueError('Cost must be finite and nonnegative')
    return Fraction(number)


def break_even(creation, ordinary, planned):
    """First positive integer N with creation + N*planned < N*ordinary.

    None means unknown inputs or no finite positive-benefit reuse count.
    Fraction arithmetic avoids decimal-context rounding at integer boundaries.
    Creation includes setup; planned includes validation, execution, publication
    and amortized maintenance in the same unit as ordinary.
    """
    creation, ordinary, planned = map(_cost, (creation, ordinary, planned))
    if any(value is None for value in (creation, ordinary, planned)):
        return None
    benefit = ordinary - planned
    if benefit <= 0:
        return None
    ratio = creation / benefit
    return ratio.numerator // ratio.denominator + 1
