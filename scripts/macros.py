#!/usr/bin/env python3
"""Mifflin-St Jeor TMB + TDEE + split de macros.

Fonte dos números: references/nutricao/evidencia.md
- Proteína 1.8–2.4 g/kg (hipertrofia/manutenção); 2.4–2.8 g/kg em cutting agressivo
- Gordura mínimo max(0.8 g/kg, 20% kcal)
- Carbo = resto

CLI:
  macros.py --sexo m --idade 30 --altura 180 --peso 85 \\
            --atividade 1.55 --objetivo cutting [--deficit 0.18] [--proteina-gkg 2.2]
"""

from __future__ import annotations

import argparse
import json
import sys

ATIVIDADE_FATORES = {
    "sedentario": 1.2,
    "leve": 1.375,
    "moderado": 1.55,
    "intenso": 1.725,
    "muito_intenso": 1.9,
}

OBJETIVO_AJUSTE = {
    "cutting": -0.18,
    "cutting_agressivo": -0.25,
    "recomp": 0.0,
    "manutencao": 0.0,
    "bulking": 0.12,
    "bulking_agressivo": 0.18,
}

OBJETIVO_PROTEINA_GKG = {
    "cutting": 2.2,
    "cutting_agressivo": 2.6,
    "recomp": 2.0,
    "manutencao": 1.8,
    "bulking": 1.8,
    "bulking_agressivo": 1.8,
}

KCAL_P = 4
KCAL_C = 4
KCAL_G = 9


def tmb_mifflin(sexo: str, peso_kg: float, altura_cm: float, idade: int) -> float:
    base = 10 * peso_kg + 6.25 * altura_cm - 5 * idade
    if sexo.lower().startswith("m"):
        return base + 5
    return base - 161


def calcular(
    sexo: str,
    idade: int,
    altura_cm: float,
    peso_kg: float,
    atividade: float | str,
    objetivo: str,
    deficit: float | None = None,
    proteina_gkg: float | None = None,
    gordura_gkg_min: float = 0.8,
) -> dict:
    if isinstance(atividade, str):
        atividade_val = ATIVIDADE_FATORES.get(atividade.lower())
        if atividade_val is None:
            raise ValueError(f"atividade inválida: {atividade}")
    else:
        atividade_val = float(atividade)

    if objetivo not in OBJETIVO_AJUSTE:
        raise ValueError(f"objetivo inválido: {objetivo}")

    tmb = tmb_mifflin(sexo, peso_kg, altura_cm, idade)
    tdee = tmb * atividade_val

    ajuste = deficit if deficit is not None else OBJETIVO_AJUSTE[objetivo]
    kcal_alvo = tdee * (1 + ajuste)

    p_gkg = proteina_gkg if proteina_gkg is not None else OBJETIVO_PROTEINA_GKG[objetivo]
    proteina_g = round(peso_kg * p_gkg)
    proteina_kcal = proteina_g * KCAL_P

    gordura_g_floor = max(peso_kg * gordura_gkg_min, kcal_alvo * 0.20 / KCAL_G)
    gordura_g = round(gordura_g_floor)
    gordura_kcal = gordura_g * KCAL_G

    carbo_kcal = kcal_alvo - proteina_kcal - gordura_kcal
    if carbo_kcal < 0:
        gordura_g = round((kcal_alvo - proteina_kcal) / KCAL_G)
        gordura_kcal = gordura_g * KCAL_G
        carbo_kcal = max(kcal_alvo - proteina_kcal - gordura_kcal, 0)
    carbo_g = round(carbo_kcal / KCAL_C)

    hidratacao_ml = round(peso_kg * 35)

    return {
        "entrada": {
            "sexo": sexo, "idade": idade, "altura_cm": altura_cm, "peso_kg": peso_kg,
            "atividade": atividade_val, "objetivo": objetivo,
            "ajuste_aplicado": round(ajuste, 3),
            "proteina_gkg_aplicada": p_gkg,
        },
        "tmb_kcal": round(tmb),
        "tdee_kcal": round(tdee),
        "calorias_alvo_kcal": round(kcal_alvo),
        "macros": {
            "proteina_g": proteina_g,
            "proteina_kcal": proteina_kcal,
            "carbo_g": carbo_g,
            "carbo_kcal": round(carbo_kcal),
            "gordura_g": gordura_g,
            "gordura_kcal": gordura_kcal,
        },
        "hidratacao_ml_dia_base": hidratacao_ml,
        "fontes": {
            "proteina": "references/nutricao/evidencia.md §1",
            "deficit": "references/nutricao/evidencia.md §2.1",
            "gordura": "references/nutricao/evidencia.md §3.1",
            "hidratacao": "references/nutricao/evidencia.md §5.1",
        },
    }


def main() -> int:
    p = argparse.ArgumentParser(description="TDEE + split de macros")
    p.add_argument("--sexo", required=True, help="m ou f")
    p.add_argument("--idade", type=int, required=True)
    p.add_argument("--altura", type=float, required=True, help="cm")
    p.add_argument("--peso", type=float, required=True, help="kg")
    p.add_argument("--atividade", default="moderado",
                   help="fator numérico ou: sedentario|leve|moderado|intenso|muito_intenso")
    p.add_argument("--objetivo", required=True,
                   choices=list(OBJETIVO_AJUSTE.keys()))
    p.add_argument("--deficit", type=float,
                   help="override explícito do ajuste (ex: -0.20 para 20%% deficit)")
    p.add_argument("--proteina-gkg", type=float,
                   help="override explícito de proteína em g/kg")

    args = p.parse_args()

    try:
        atividade = float(args.atividade)
    except ValueError:
        atividade = args.atividade

    result = calcular(
        sexo=args.sexo,
        idade=args.idade,
        altura_cm=args.altura,
        peso_kg=args.peso,
        atividade=atividade,
        objetivo=args.objetivo,
        deficit=args.deficit,
        proteina_gkg=args.proteina_gkg,
    )
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
