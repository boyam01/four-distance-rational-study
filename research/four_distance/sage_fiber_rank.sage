#!/usr/bin/env sage
# Sage-first genus-one fiber rank/generator attempt.
#
# This script is intentionally conservative.  It records every successful Sage
# construction step and marks point generation as skipped when Sage does not
# expose an inverse morphism back to the quartic model.

import argparse
import csv
import os
from pathlib import Path

from sage.all import (
    EllipticCurve_from_cubic,
    HyperellipticCurve,
    PolynomialRing,
    ProjectiveSpace,
    QQ,
    factor,
    lcm,
    proof,
)


DEFAULT_DELTAS = ["289/260", "13/6"]
DEFAULT_FIBERS = ["B", "C", "D"]


def frac_text_to_qq(text):
    return QQ(text)


def qq_to_text(value):
    value = QQ(value)
    if value.denominator() == 1:
        return str(value.numerator())
    return "%s/%s" % (value.numerator(), value.denominator())


def expression_for(label, delta, u):
    A = 2 * u / (1 - u**2)
    if label == "B":
        return A * (delta - 1)
    if label == "C":
        return delta - 1 / A
    if label == "D":
        return (A * delta - 1) / (A * (delta - 1))
    raise ValueError("unknown fiber label %s" % label)


def build_curve_row(delta_text, label):
    R = PolynomialRing(QQ, "u")
    u = R.gen()
    delta = frac_text_to_qq(delta_text)
    expr = expression_for(label, delta, u)
    num = expr.numerator()
    den = expr.denominator()
    F_raw = num**2 + den**2
    denominator_lcm = lcm([coeff.denominator() for coeff in F_raw.coefficients()] or [1])
    F = factor(denominator_lcm * F_raw)
    return {
        "delta": delta_text,
        "fiber": label,
        "curve_label": "%s_fiber" % label,
        "polynomial": str(F).replace("^", "**"),
        "known_basepoints": known_basepoints(delta_text, label),
    }


def known_basepoints(delta_text, label):
    if delta_text == "289/260":
        if label == "B":
            return "u=3/5,W=85,source=hardcoded_seed_730"
        if label == "C":
            return "u=3/5,W=901/5,source=hardcoded_seed_730"
        if label == "D":
            return "u=15/26,W=2125/26,source=hardcoded_from_C_orbit"
        return ""
    if delta_text == "13/6":
        if label == "B":
            return "u=1/4,W=53/16,source=hardcoded_seed_17"
        if label == "C":
            return "u=1/4,W=25/16,source=hardcoded_seed_17"
        return ""
    return ""


def rational_square_root(value):
    value = QQ(value)
    if value < 0:
        return None
    num = value.numerator()
    den = value.denominator()
    if not num.is_square() or not den.is_square():
        return None
    return QQ(num.sqrt()) / QQ(den.sqrt())


def _basepoint_key(item):
    return item.get("u", ""), item.get("W", "")


def _basepoints_to_text(basepoints):
    parts = []
    for item in basepoints:
        text = "u=%s,W=%s" % (item["u"], item["W"])
        if item.get("source"):
            text += ",source=%s" % item["source"]
        parts.append(text)
    return ";".join(parts)


def _parse_basepoint_dicts(text):
    output = []
    if not text:
        return output
    for item in text.split(";"):
        fields = {}
        for part in item.strip().split(","):
            if "=" in part:
                key, value = part.split("=", 1)
                fields[key.strip()] = value.strip()
        if "u" in fields and "W" in fields:
            output.append(
                {
                    "u": fields["u"],
                    "W": fields["W"],
                    "source": fields.get("source", "known_basepoint"),
                }
            )
    return output


def _merge_basepoint(existing, new_item):
    new_key = _basepoint_key(new_item)
    for item in existing:
        if _basepoint_key(item) == new_key:
            sources = set(filter(None, item.get("source", "").split("+")))
            sources.update(filter(None, new_item.get("source", "").split("+")))
            item["source"] = "+".join(sorted(sources))
            return
    existing.append(new_item)


def discover_basepoints_from_verified(rows, verified_csv):
    verified_path = Path(verified_csv)
    discovered = {}
    warnings = {}
    if not verified_path.exists():
        return discovered, warnings

    curve_by_key = {(row["delta"], row["fiber"]): row for row in rows}
    with verified_path.open("r", newline="", encoding="utf-8") as handle:
        for item in csv.DictReader(handle):
            delta = item.get("delta", "")
            u_text = item.get("u", "")
            if not u_text or u_text.startswith("omitted_fraction"):
                continue
            for fiber, defect_field in (("B", "defect_B"), ("C", "defect_C"), ("D", "defect_D")):
                if item.get(defect_field) != "1":
                    continue
                row = curve_by_key.get((delta, fiber))
                if row is None:
                    continue
                try:
                    R = PolynomialRing(QQ, "u")
                    u = R.gen()
                    F = R(row["polynomial"].replace("**", "^"))
                    u_value = QQ(u_text)
                    W = rational_square_root(F(u_value))
                except Exception as exc:
                    warnings.setdefault((delta, fiber), []).append(
                        "WARNING could not test u=%s from verified candidate: %s" % (u_text, exc)
                    )
                    continue
                if W is None:
                    warnings.setdefault((delta, fiber), []).append(
                        "WARNING verified candidate u=%s did not square on %s_fiber" % (u_text, fiber)
                    )
                    continue
                discovered.setdefault((delta, fiber), []).append(
                    {
                        "u": qq_to_text(u_value),
                        "W": qq_to_text(W),
                        "source": "discovered_from_verified_candidate",
                    }
                )
    return discovered, warnings


def augment_curve_basepoints(rows, args):
    discovered, warnings = discover_basepoints_from_verified(rows, args.verified_csv)
    for row in rows:
        key = (row["delta"], row["fiber"])
        basepoints = []
        for item in _parse_basepoint_dicts(known_basepoints(row["delta"], row["fiber"])):
            _merge_basepoint(basepoints, item)
        for item in _parse_basepoint_dicts(row.get("known_basepoints", "")):
            _merge_basepoint(basepoints, item)
        for item in discovered.get(key, []):
            _merge_basepoint(basepoints, item)
        row["known_basepoints"] = _basepoints_to_text(basepoints)
        row["basepoint_warnings"] = ";".join(warnings.get(key, []))
    return rows


def load_curve_rows(args):
    rows = []
    curve_csv = Path(args.curves_csv)
    if args.all and curve_csv.exists():
        delta_filter = set(args.delta or [])
        with curve_csv.open("r", newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if delta_filter and row["delta"] not in delta_filter:
                    continue
                label = row["curve_label"].replace("_fiber", "")
                rows.append(
                    {
                        "delta": row["delta"],
                        "fiber": label,
                        "curve_label": row["curve_label"],
                        "polynomial": row["polynomial"],
                        "known_basepoints": row.get("known_basepoints", ""),
                    }
                )
        return augment_curve_basepoints(rows, args)

    deltas = args.delta or DEFAULT_DELTAS
    fibers = DEFAULT_FIBERS if args.all else [args.fiber]
    for delta in deltas:
        for label in fibers:
            rows.append(build_curve_row(delta, label))
    return augment_curve_basepoints(rows, args)


def parse_known_points(text):
    points = []
    if not text:
        return points
    for item in text.split(";"):
        item = item.strip()
        if not item:
            continue
        fields = {}
        for part in item.split(","):
            if "=" in part:
                key, value = part.split("=", 1)
                fields[key.strip()] = value.strip()
        if "u" in fields and "W" in fields:
            points.append((fields["u"], fields["W"], fields.get("source", "known_basepoint")))
    return points


def _homogenize_degree_three(poly, X, M, Z):
    total = 0
    for powers, coeff in poly.dict().items():
        x_power, m_power = powers
        z_power = 3 - x_power - m_power
        if z_power < 0:
            raise ValueError("plane cubic term has degree > 3")
        total += coeff * X**x_power * M**m_power * Z**z_power
    return total


def _plane_cubic_from_quartic(F, u0, W0):
    R2 = PolynomialRing(QQ, ("x", "m"))
    x, m = R2.gens()
    Fx = F(x)
    line = W0 + m * (x - u0)
    numerator = Fx - line**2
    cubic_affine, remainder = numerator.quo_rem(x - u0)
    if remainder != 0:
        raise ArithmeticError("quartic basepoint did not divide secant cubic")
    P2 = ProjectiveSpace(QQ, 2, names=("X", "M", "Z"))
    X, M, Z = P2.coordinate_ring().gens()
    cubic = _homogenize_degree_three(cubic_affine, X, M, Z)
    tangent_slope = F.derivative()(u0) / (2 * W0)
    basepoint = (u0, tangent_slope, QQ(1))
    return cubic, basepoint, P2


def _map_minimal_point_to_u(point, inverse_to_cubic, min_to_raw, u0, W0):
    raw_point = min_to_raw(point)
    cubic_point = inverse_to_cubic(raw_point)
    coords = list(cubic_point)
    if len(coords) != 3 or coords[2] == 0:
        return None
    u_value = QQ(coords[0] / coords[2])
    slope = QQ(coords[1] / coords[2])
    W_value = QQ(W0 + slope * (u_value - u0))
    return u_value, W_value


def _append_generated_points(point_rows, row, generated, source, n_text):
    for u_value, W_value in generated:
        point_rows.append(
            {
                "delta": row["delta"],
                "fiber": row["fiber"],
                "curve_label": row["curve_label"],
                "u": qq_to_text(u_value),
                "W": qq_to_text(W_value),
                "source": source,
                "n": n_text,
                "status": "generated_point",
            }
        )


def analyze_curve(row, args):
    R = PolynomialRing(QQ, "u")
    u = R.gen()
    F = R(row["polynomial"].replace("**", "^"))
    output = dict(row)
    output.update(
        {
            "method_used": "",
            "elliptic_curve": "",
            "rank": "",
            "rank_bounds": "",
            "rank_bounds_before": "",
            "rank_bounds_after": "",
            "rank_certified": "",
            "torsion": "",
            "generators": "",
            "extra_generators_found": "",
            "saturation_status": "",
            "integral_model": "",
            "cremona_label": "",
            "combo_bound": "",
            "combinations_checked": "",
            "point_generation_status": "",
            "error": "",
        }
    )
    point_rows = []
    known_points = parse_known_points(row.get("known_basepoints", ""))
    try:
        C = HyperellipticCurve(F)
        output["method_used"] = "HyperellipticCurve"
        try:
            J = C.jacobian()
            output["method_used"] += "+Jacobian"
            try:
                output["rank_bounds"] = str(J.rank_bounds())
            except Exception as exc:
                output["rank_bounds"] = "unavailable:%s" % exc
            try:
                gens = J.gens()
                output["generators"] = str(gens)
            except Exception as exc:
                output["generators"] = "unavailable:%s" % exc
        except Exception as exc:
            output["method_used"] += ";jacobian_failed:%s" % exc

        point_generation_count = 0
        if known_points:
            u0 = QQ(known_points[0][0])
            W0 = QQ(known_points[0][1])
            try:
                proof.arithmetic(False)
                cubic, cubic_basepoint, _space = _plane_cubic_from_quartic(F, u0, W0)
                phi = EllipticCurve_from_cubic(cubic, cubic_basepoint, morphism=True)
                raw_curve = phi.codomain()
                minimal_curve = raw_curve.minimal_model()
                raw_to_min = raw_curve.isomorphism_to(minimal_curve)
                min_to_raw = ~raw_to_min
                inverse_to_cubic = phi.inverse()
                output["method_used"] += "+PlaneCubic+EllipticCurve_from_cubic"
                output["elliptic_curve"] = str(raw_curve)
                output["integral_model"] = str(minimal_curve)
                try:
                    output["cremona_label"] = str(minimal_curve.cremona_label())
                except Exception as exc:
                    output["cremona_label"] = "unavailable:%s" % exc
                try:
                    output["torsion"] = str(minimal_curve.torsion_subgroup())
                except Exception as exc:
                    output["torsion"] = "unavailable:%s" % exc
                try:
                    output["rank_bounds"] = str(minimal_curve.rank_bounds())
                    output["rank_bounds_before"] = output["rank_bounds"]
                except Exception as exc:
                    output["rank_bounds"] = "unavailable:%s" % exc
                try:
                    output["rank"] = str(minimal_curve.rank(algorithm="pari"))
                except Exception as exc:
                    output["rank"] = "unavailable:%s" % exc
                try:
                    gens = minimal_curve.gens()
                    output["generators"] = str(gens)
                except Exception as exc:
                    gens = []
                    output["generators"] = "unavailable:%s" % exc
                if args.rank_diagnostic:
                    try:
                        diagnostic_gens = minimal_curve.gens(
                            verbose=1, lim1=20, lim3=20, limtriv=20, maxprob=200
                        )
                        output["extra_generators_found"] = "yes" if len(diagnostic_gens) > len(gens) else "no"
                        if len(diagnostic_gens) > len(gens):
                            gens = diagnostic_gens
                            output["generators"] = str(gens)
                    except Exception as exc:
                        output["extra_generators_found"] = "unavailable:%s" % exc
                    try:
                        output["rank_bounds_after"] = str(minimal_curve.rank_bounds())
                        output["rank_bounds"] = output["rank_bounds_after"]
                    except Exception as exc:
                        output["rank_bounds_after"] = "unavailable:%s" % exc
                    try:
                        output["saturation_status"] = str(minimal_curve.saturation(gens))
                    except Exception as exc:
                        output["saturation_status"] = "unavailable:%s" % exc
                else:
                    output["rank_bounds_after"] = output["rank_bounds"]
                    output["extra_generators_found"] = "not_run"
                    output["saturation_status"] = "not_run"
                if output["rank"] and output["rank_bounds"].startswith("("):
                    output["rank_certified"] = (
                        "yes" if output["rank_bounds"] == "(%s, %s)" % (output["rank"], output["rank"]) else "no"
                    )
                seen_u = set()
                combinations_checked = 0
                if len(gens) >= 2:
                    output["combo_bound"] = str(args.combo_bound)
                    G1, G2 = gens[0], gens[1]
                    multiples_1 = {a: a * G1 for a in range(-args.combo_bound, args.combo_bound + 1)}
                    multiples_2 = {b: b * G2 for b in range(-args.combo_bound, args.combo_bound + 1)}
                    for a in range(-args.combo_bound, args.combo_bound + 1):
                        for b in range(-args.combo_bound, args.combo_bound + 1):
                            if a == 0 and b == 0:
                                continue
                            combinations_checked += 1
                            try:
                                mapped = _map_minimal_point_to_u(
                                    multiples_1[a] + multiples_2[b], inverse_to_cubic, min_to_raw, u0, W0
                                )
                            except Exception:
                                mapped = None
                            if mapped is None:
                                continue
                            u_value, W_value = mapped
                            key = qq_to_text(u_value)
                            if key in seen_u:
                                continue
                            seen_u.add(key)
                            point_rows.append(
                                {
                                    "delta": row["delta"],
                                    "fiber": row["fiber"],
                                    "curve_label": row["curve_label"],
                                    "u": key,
                                    "W": qq_to_text(W_value),
                                    "source": "combo:%s,%s" % (a, b),
                                    "n": "%s,%s" % (a, b),
                                    "status": "generated_point",
                                }
                            )
                            point_generation_count += 1
                elif len(gens) == 1:
                    for n in range(-args.max_multiple, args.max_multiple + 1):
                        if n == 0:
                            continue
                        combinations_checked += 1
                        try:
                            mapped = _map_minimal_point_to_u(
                                n * gens[0], inverse_to_cubic, min_to_raw, u0, W0
                            )
                        except Exception:
                            mapped = None
                        if mapped is None:
                            continue
                        u_value, W_value = mapped
                        key = qq_to_text(u_value)
                        if key in seen_u:
                            continue
                        seen_u.add(key)
                        point_rows.append(
                            {
                                "delta": row["delta"],
                                "fiber": row["fiber"],
                                "curve_label": row["curve_label"],
                                "u": key,
                                "W": qq_to_text(W_value),
                                "source": "sage_generator_0",
                                "n": str(n),
                                "status": "generated_point",
                            }
                        )
                        point_generation_count += 1
                output["combinations_checked"] = str(combinations_checked)
                output["point_generation_status"] = "generated:%s" % point_generation_count
            except Exception as exc:
                output["point_generation_status"] = "elliptic_conversion_failed:%s" % exc
        else:
            output["point_generation_status"] = "no_known_basepoint"

        # Always pass through known quartic basepoints as u candidates.
        for u_text, W_text, source in known_points:
            point_rows.append(
                {
                    "delta": row["delta"],
                    "fiber": row["fiber"],
                    "curve_label": row["curve_label"],
                    "u": u_text,
                    "W": W_text,
                    "source": source,
                    "n": "0",
                    "status": "known_point",
                }
            )
    except Exception as exc:
        output["error"] = str(exc)
        output["point_generation_status"] = "curve_failed"
    return output, point_rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--delta", action="append")
    parser.add_argument("--fiber", choices=DEFAULT_FIBERS, default="B")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--max-multiple", type=int, default=100)
    parser.add_argument("--combo-bound", type=int, default=2)
    parser.add_argument("--rank-diagnostic", action="store_true")
    parser.add_argument("--strategic-only", action="store_true")
    parser.add_argument("--sieve-primes", type=int, default=0)
    parser.add_argument("--curves-csv", default="research/four_distance/data/fiber_secant_curves.csv")
    parser.add_argument("--verified-csv", default="research/four_distance/data/sage_fiber_verified_candidates.csv")
    parser.add_argument("--output-curves", default="research/four_distance/data/sage_fiber_curves.csv")
    parser.add_argument("--output-points", default="research/four_distance/data/sage_fiber_points.csv")
    args = parser.parse_args()

    curve_rows = []
    point_rows = []
    for row in load_curve_rows(args):
        curve_row, points = analyze_curve(row, args)
        curve_rows.append(curve_row)
        point_rows.extend(points)

    Path(args.output_curves).parent.mkdir(parents=True, exist_ok=True)
    curve_fields = [
        "delta",
        "fiber",
        "curve_label",
        "polynomial",
        "known_basepoints",
        "method_used",
        "elliptic_curve",
        "rank",
        "rank_bounds",
        "rank_bounds_before",
        "rank_bounds_after",
        "rank_certified",
        "torsion",
        "generators",
        "extra_generators_found",
        "saturation_status",
        "integral_model",
        "cremona_label",
        "combo_bound",
        "combinations_checked",
        "point_generation_status",
        "basepoint_warnings",
        "error",
    ]
    with open(args.output_curves, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=curve_fields)
        writer.writeheader()
        writer.writerows(curve_rows)

    point_fields = ["delta", "fiber", "curve_label", "u", "W", "source", "n", "status"]
    with open(args.output_points, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=point_fields)
        writer.writeheader()
        writer.writerows(point_rows)

    print("wrote %s" % args.output_curves)
    print("wrote %s" % args.output_points)


if __name__ == "__main__":
    main()
