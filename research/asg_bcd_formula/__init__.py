"""Public exact-arithmetic ASG/BCD formula helpers.

This package is intentionally research-only.  It contains no trading runtime,
exchange client, credentials, order logic, or position management.
"""

from .formula import (
    BCDPoint,
    A_of_u,
    bcd_from_u_delta,
    classify_defects,
    forward_closure_from_A_C,
    fraction_to_str,
    in_pythagorean_slope_set,
    is_square,
    love_relation_ok,
    point_from_u_delta,
    reverse_closure_from_A_D,
    slope_defect,
    slope_norm,
    squarefree_part,
)

__all__ = [
    "BCDPoint",
    "A_of_u",
    "bcd_from_u_delta",
    "classify_defects",
    "forward_closure_from_A_C",
    "fraction_to_str",
    "in_pythagorean_slope_set",
    "is_square",
    "love_relation_ok",
    "point_from_u_delta",
    "reverse_closure_from_A_D",
    "slope_defect",
    "slope_norm",
    "squarefree_part",
]
