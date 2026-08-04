#!/usr/bin/env python3
"""Reproduz a investigação preliminar das âncoras físicas.

Gera os números citados na Seção 3.4 da proposta e a Figura 3.1. Executar:

    python scripts/verify_physics_anchors.py --n 40 --seed 42

Toda estatística impressa aqui é rastreável a esta execução; nenhum número do
texto tem outra origem. Ver Apêndice B da proposta.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.touchstone import (  # noqa: E402
    cavity_modes,
    low_frequency_slope,
    mil_to_m,
    parse_touchstone,
    plate_capacitance,
    self_impedance,
)

logger = logging.getLogger("verify_physics")

DATASET = Path(__file__).resolve().parents[1] / (
    "6_layer_pcb_based_pdn_with_two_arrays_LHS_mar_2023"
)
N_PORTS = 36
A_MIL, B_MIL = 5800.0, 4000.0
N_LOW = 8  # pontos usados na região quase-estática (f < 25 MHz)


def analyse_one(row: dict[str, str]) -> dict[str, float]:
    """Extrai as grandezas de verificação de uma configuração."""
    eps_r = float(row["PERMITTIVITY"])
    height_m = mil_to_m(float(row["TDIEL"]))
    path = DATASET / "variation" / f"simu_{row['simu_index']}.s36p"

    net = parse_touchstone(path, n_ports=N_PORTS)
    z_abs = np.abs(self_impedance(net))
    freq = net.freq

    lo = slice(0, N_LOW)
    c_extracted = float(np.mean(1 / (2 * np.pi * freq[lo] * z_abs[lo])))
    c_analytic = plate_capacitance(
        eps_r, mil_to_m(A_MIL), mil_to_m(B_MIL), height_m
    )

    return {
        "simu_index": int(row["simu_index"]),
        "eps_r": eps_r,
        "h_mil": float(row["TDIEL"]),
        "slope_low": low_frequency_slope(freq, z_abs, N_LOW),
        "c_extracted": c_extracted,
        "c_analytic": c_analytic,
        "c_ratio": c_extracted / c_analytic,
        "f_null_hz": float(freq[int(np.argmin(z_abs))]),
        "z_max_ohm": float(z_abs.max()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=40, help="tamanho da amostra")
    parser.add_argument("--seed", type=int, default=42, help="semente aleatória")
    parser.add_argument("--out", type=Path, default=Path("experiments/physics_anchors.json"))
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if not DATASET.exists():
        logger.error("base não encontrada em %s", DATASET)
        return 1

    rows = list(csv.DictReader((DATASET / "parameter.csv").open()))
    rng = np.random.default_rng(args.seed)
    sample = rng.choice(len(rows), size=min(args.n, len(rows)), replace=False)

    records = [analyse_one(rows[i]) for i in sample]
    slope = np.array([r["slope_low"] for r in records])
    ratio = np.array([r["c_ratio"] for r in records])
    corr = float(
        np.corrcoef(
            np.log10([r["c_analytic"] for r in records]),
            np.log10([r["c_extracted"] for r in records]),
        )[0, 1]
    )

    logger.info("amostra: n=%d, semente=%d\n", len(records), args.seed)
    logger.info("R1  inclinação log-log em f < 25 MHz  (capacitivo ideal = -1)")
    logger.info("      média %+.3f  desvio %.3f  faixa [%+.3f ; %+.3f]",
                slope.mean(), slope.std(), slope.min(), slope.max())
    logger.info("      -> R1 %s", "CONFIRMADA" if abs(slope.mean() + 1) < 0.05 else "REFUTADA")

    logger.info("\nR2  escala da capacitância  C_extraída / C_analítica")
    logger.info("      mediana %.2f  faixa [%.2f ; %.2f]  correlação log-log r=%.2f",
                np.median(ratio), ratio.min(), ratio.max(), corr)
    logger.info("      -> R2 TENDÊNCIA APENAS: usar fator gamma estimado, não o valor analítico")

    logger.info("\nR5  localização modal  (ver PHYSICS_SPEC.md: REFUTADA)")
    a_m, b_m = mil_to_m(A_MIL), mil_to_m(B_MIL)
    for eps in (2.5, 4.5):
        modes = cavity_modes(eps, a_m, b_m, 1e9)
        logger.info("      eps_r=%.1f -> %d modos na banda, primeiro em %.0f MHz",
                    eps, modes.size, modes[0] / 1e6)
    logger.info("      não impor como restrição: os modos não produzem máximos em Z11")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(
        {"seed": args.seed, "n": len(records), "records": records,
         "summary": {"slope_mean": float(slope.mean()), "slope_std": float(slope.std()),
                     "ratio_median": float(np.median(ratio)), "corr_log": corr}},
        indent=2))
    logger.info("\nregistro salvo em %s", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
