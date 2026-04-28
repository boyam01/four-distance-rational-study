from fractions import Fraction

from research.four_distance.slope_tools import in_S, verify_seed


def test_seed_17_verification():
    seed = verify_seed(52, 45, 24)
    slopes = seed.slopes
    assert seed.first_three_square is True
    assert seed.true_solution is False
    assert seed.defect == 17
    assert seed.mcc.live is False
    assert slopes.A == Fraction(8, 15)
    assert slopes.B == Fraction(28, 45)
    assert slopes.C == Fraction(7, 24)
    assert slopes.D == Fraction(1, 4)
    assert slopes.D_in_S is False
    assert slopes.love_relation_ok is True
    assert slopes.delta_relations_ok is True
    assert slopes.delta == Fraction(13, 6)
    assert slopes.point_from_delta == (Fraction(45, 52), Fraction(6, 13))


def test_seed_730_verification():
    seed = verify_seed(867, 416, 780)
    slopes = seed.slopes
    assert seed.first_three_square is True
    assert seed.true_solution is False
    assert seed.defect == 730
    assert seed.mcc.live is True
    assert slopes.A == Fraction(15, 8)
    assert slopes.B == Fraction(87, 416)
    assert slopes.C == Fraction(451, 780)
    assert slopes.D == Fraction(451, 87)
    assert slopes.D_in_S is False
    assert slopes.love_relation_ok is True
    assert slopes.delta_relations_ok is True
    assert slopes.delta == Fraction(289, 260)
    assert slopes.point_from_delta == (Fraction(416, 867), Fraction(260, 289))


def test_seed_s_membership():
    assert in_S(Fraction(8, 15))
    assert in_S(Fraction(28, 45))
    assert in_S(Fraction(7, 24))
    assert not in_S(Fraction(1, 4))
    assert in_S(Fraction(15, 8))
    assert in_S(Fraction(87, 416))
    assert in_S(Fraction(451, 780))
    assert not in_S(Fraction(451, 87))

