#!/usr/bin/env python3
"""Exact ASG/BCD formula utilities for the four-distance study.

The formulas in this module are a small public extraction of the research
objects used in the unit-square four-distance work:

    A*C = B*D = A+B-1

and the fixed-delta fiber parametrization:

    A = 2u/(1-u^2)
    B = A*(delta-1)
    C = delta - 1/A
    D = (A*delta - 1)/(A*(delta-1))
    P = (1/(A*delta), 1/delta)

All square, defect, and membership checks use Python int and Fraction only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Any


def as_fraction(value: Fraction | int | str) -> Fraction:
    """Normalize a public input into a reduced Fraction."""
    return value if isinstance(value, Fraction) else Fraction(value)


def fraction_to_str(value: Fraction) -> str:
    """Return a stable compact string for JSON/CSV output."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def is_square(n: int) -> bool:
    """Return True iff n is a non-negative perfect square."""
    if n < 0:
        raise ValueError("is_square requires n >= 0")
    root = math.isqrt(n)
    return root * root == n


def squarefree_part(n: int) -> int:
    """Return the squarefree part of a positive integer using integer math."""
    if n <= 0:
        raise ValueError("squarefree_part requires n > 0")
    result = 1
    d = 2
    while d * d <= n:
        parity = 0
        while n % d == 0:
            n //= d
            parity ^= 1
        if parity:
            result *= d
        d += 1 if d == 2 else 2
    if n > 1:
        result *= n
    return result


def slope_norm(alpha: Fraction | int | str) -> int:
    """Return a^2+b^2 for alpha=a/b in reduced form."""
    value = as_fraction(alpha)
    return value.numerator * value.numerator + value.denominator * value.denominator


def slope_defect(alpha: Fraction | int | str) -> int:
    """Return the squarefree defect of alpha as a Pythagorean slope.

    defect=1 means alpha belongs to the rational Pythagorean slope set S.
    """
    return squarefree_part(slope_norm(alpha))


def in_pythagorean_slope_set(alpha: Fraction | int | str) -> bool:
    """Return True iff sqrt(1+alpha^2) is rational."""
    return is_square(slope_norm(alpha))


def A_of_u(u: Fraction | int | str) -> Fraction:
    """Return A=2u/(1-u^2)."""
    value = as_fraction(u)
    denom = 1 - value * value
    if denom == 0:
        raise ZeroDivisionError("A_of_u is undefined for u=+/-1")
    return Fraction(2) * value / denom


def point_from_u_delta(
    u: Fraction | int | str, delta: Fraction | int | str
) -> tuple[Fraction, Fraction]:
    """Return P=(x,y)=(1/(A*delta), 1/delta)."""
    A = A_of_u(u)
    delta_value = as_fraction(delta)
    if A == 0 or delta_value == 0:
        raise ZeroDivisionError("point_from_u_delta requires A and delta nonzero")
    return (Fraction(1) / (A * delta_value), Fraction(1) / delta_value)


def love_relation_ok(A: Fraction, B: Fraction, C: Fraction, D: Fraction) -> bool:
    """Return True iff A*C = B*D = A+B-1 exactly."""
    value = A * C
    return value == B * D == A + B - 1


def classify_defects(defects: tuple[int, int, int]) -> tuple[str, int | None]:
    """Classify (defect_B, defect_C, defect_D).

    Returns (label, remaining_defect).  The near-miss label requires exactly
    two good B/C/D conditions and one remaining defect.
    """
    good_count = sum(1 for defect in defects if defect == 1)
    if good_count == 3:
        return ("true_candidate", None)
    if good_count == 2:
        remaining = next(defect for defect in defects if defect != 1)
        return ("two_good_one_bad", remaining)
    if good_count == 1:
        return ("one_good", None)
    return ("zero_good", None)


@dataclass(frozen=True)
class BCDPoint:
    """Fixed-delta ASG/BCD point with exact defects."""

    delta: Fraction
    u: Fraction
    A: Fraction
    B: Fraction
    C: Fraction
    D: Fraction
    x: Fraction
    y: Fraction
    defect_B: int
    defect_C: int
    defect_D: int
    classification: str
    remaining_defect: int | None
    love_relation_ok: bool
    point_in_unit: bool

    @property
    def defects(self) -> tuple[int, int, int]:
        return (self.defect_B, self.defect_C, self.defect_D)

    @property
    def all_good(self) -> bool:
        return self.defects == (1, 1, 1)

    @property
    def two_good_one_bad(self) -> bool:
        return self.classification == "two_good_one_bad"

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "schema_version": "asg_bcd_formula_v1",
            "delta": fraction_to_str(self.delta),
            "u": fraction_to_str(self.u),
            "A": fraction_to_str(self.A),
            "B": fraction_to_str(self.B),
            "C": fraction_to_str(self.C),
            "D": fraction_to_str(self.D),
            "x": fraction_to_str(self.x),
            "y": fraction_to_str(self.y),
            "defect_B": self.defect_B,
            "defect_C": self.defect_C,
            "defect_D": self.defect_D,
            "classification": self.classification,
            "remaining_defect": self.remaining_defect,
            "love_relation_ok": self.love_relation_ok,
            "point_in_unit": self.point_in_unit,
            "runtime_effect": "none",
            "decision": "research_only",
        }


def bcd_from_u_delta(
    u: Fraction | int | str, delta: Fraction | int | str
) -> BCDPoint:
    """Compute the exact B/C/D formula pack for a fixed delta fiber."""
    u_value = as_fraction(u)
    delta_value = as_fraction(delta)
    A = A_of_u(u_value)
    if A == 0 or delta_value == 1:
        raise ZeroDivisionError("B/C/D formulas require A != 0 and delta != 1")
    B = A * (delta_value - 1)
    C = delta_value - Fraction(1) / A
    D = (A * delta_value - 1) / (A * (delta_value - 1))
    x, y = point_from_u_delta(u_value, delta_value)
    defects = (slope_defect(B), slope_defect(C), slope_defect(D))
    classification, remaining = classify_defects(defects)
    return BCDPoint(
        delta=delta_value,
        u=u_value,
        A=A,
        B=B,
        C=C,
        D=D,
        x=x,
        y=y,
        defect_B=defects[0],
        defect_C=defects[1],
        defect_D=defects[2],
        classification=classification,
        remaining_defect=remaining,
        love_relation_ok=love_relation_ok(A, B, C, D),
        point_in_unit=(0 < x < 1 and 0 < y < 1),
    )


def forward_closure_from_A_C(
    A: Fraction | int | str, C: Fraction | int | str
) -> tuple[Fraction, Fraction]:
    """Given A,C, return B,D from A*C = B*D = A+B-1."""
    A_value = as_fraction(A)
    C_value = as_fraction(C)
    B = A_value * C_value + 1 - A_value
    if B == 0:
        raise ZeroDivisionError("D is undefined when B=0")
    D = A_value * C_value / B
    return (B, D)


def reverse_closure_from_A_D(
    A: Fraction | int | str, D: Fraction | int | str
) -> tuple[Fraction, Fraction]:
    """Given A,D, return B,C from reverse closure."""
    A_value = as_fraction(A)
    D_value = as_fraction(D)
    if A_value == 0 or D_value == 1:
        raise ZeroDivisionError("reverse closure requires A != 0 and D != 1")
    B = (A_value - 1) / (D_value - 1)
    C = D_value * (A_value - 1) / (A_value * (D_value - 1))
    return (B, C)
