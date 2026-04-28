from fractions import Fraction

import pytest

from research.four_distance.slope_tools import (
    INF,
    in_S,
    is_square,
    squarefree_part,
    v_p_fraction,
)


def test_is_square_exact():
    assert is_square(0)
    assert is_square(1)
    assert is_square(2601)
    assert not is_square(833)
    with pytest.raises(ValueError):
        is_square(-1)


def test_squarefree_part_known_values():
    assert squarefree_part(833) == 17
    assert squarefree_part(210970) == 730
    assert squarefree_part(49 * 17) == 17


def test_v_p_fraction():
    assert v_p_fraction(Fraction(45, 52), 3) == 2
    assert v_p_fraction(Fraction(416, 867), 3) == -1
    assert v_p_fraction(Fraction(0), 3) == INF


def test_in_S_known_values():
    assert in_S(Fraction(8, 15))
    assert in_S(Fraction(28, 45))
    assert in_S(Fraction(7, 24))
    assert not in_S(Fraction(1, 4))
    assert in_S(Fraction(15, 8))
    assert in_S(Fraction(87, 416))
    assert in_S(Fraction(451, 780))
    assert not in_S(Fraction(451, 87))

