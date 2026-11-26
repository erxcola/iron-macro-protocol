#!/usr/bin/env python3
"""Consolida receitas de um plano semanal em lista de mercado agrupada por setor.

Entrada: JSON com lista de refeições, cada uma com `ingredientes: [{nome, gramas, unidade?}]`.
Saída: markdown agrupado por setor (hortifruti, açougue, laticínios, grãos/secos, outros).

Setorização via `references/mercado/substituicoes.md` → fallback no mapa interno.
Preços via ~/.nutri-personal/precos.json (opcional).

CLI:
  lista_mercado.py --plano path/to/semana.json [--precos ~/.nutri-personal/precos.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

SETORES = (
    "hortifruti",
    "acougue",
    "laticinios",
    "graos_secos",
    "padaria",
    "mercearia",
    "outros",
)

SETOR_PADRAO = {
    # hortifruti
    "alface": "hortifruti", "tomate": "hortifruti", "cenoura": "hortifruti",
    "cebola": "hortifruti", "alho": "hortifruti", "batata": "hortifruti",
    "batata-doce": "hortifruti", "mandioca": "hortifruti", "banana": "hortifruti",
    "maca": "hortifruti", "maçã": "hortifruti", "laranja": "hortifruti",
    "limao": "hortifruti", "limão": "hortifruti", "abacate": "hortifruti",
    "espinafre": "hortifruti", "brocolis": "hortifruti", "brócolis": "hortifruti",
    "couve": "hortifruti", "pepino": "hortifruti", "pimentao": "hortifruti",
    "mamao": "hortifruti", "mamão": "hortifruti", "morango": "hortifruti",
    "manga": "hortifruti", "abacaxi": "hortifruti", "melancia": "hortifruti",
    "berinjela": "hortifruti", "abobrinha": "hortifruti", "aipim": "hortifruti",
    # açougue / proteína animal
    "frango": "acougue", "peito de frango": "acougue", "coxa de frango": "acougue",
    "carne moida": "acougue", "carne moída": "acougue", "patinho": "acougue",
    "alcatra": "acougue", "contrafile": "acougue", "contra-filé": "acougue",
    "file mignon": "acougue", "filé mignon": "acougue", "costela": "acougue",
    "porco": "acougue", "lombo": "acougue", "linguica": "acougue",
    "peixe": "acougue", "salmao": "acougue", "salmão": "acougue",
    "tilapia": "acougue", "tilápia": "acougue", "atum fresco": "acougue",
    "sardinha fresca": "acougue", "cavala": "acougue",
    # laticínios
    "leite": "laticinios", "iogurte": "laticinios", "queijo": "laticinios",
    "requeijao": "laticinios", "ricota": "laticinios", "cottage": "laticinios",
    "manteiga": "laticinios", "creme de leite": "laticinios",
    "mussarela": "laticinios", "parmesao": "laticinios", "parmesão": "laticinios",
    # ovos ficam em laticínios por convenção de supermercado brasileiro
    "ovo": "laticinios", "ovos": "laticinios",
    # grãos e secos
    "arroz": "graos_secos", "feijao": "graos_secos", "feijão": "graos_secos",
    "lentilha": "graos_secos", "grao de bico": "graos_secos", "grão de bico": "graos_secos",
    "aveia": "graos_secos", "quinoa": "graos_secos", "macarrao": "graos_secos",
    "macarrão": "graos_secos", "farinha": "graos_secos", "tapioca": "graos_secos",
    "amendoim": "graos_secos", "castanha": "graos_secos", "nozes": "graos_secos",
    "amendoas": "graos_secos", "amêndoas": "graos_secos",
    # padaria
    "pao": "padaria", "pão": "padaria", "pao integral": "padaria",
    # mercearia (óleos, molhos, enlatados, suplementos)
    "azeite": "mercearia", "oleo": "mercearia", "óleo": "mercearia",
    "vinagre": "mercearia", "sal": "mercearia", "acucar": "mercearia",
    "açúcar": "mercearia", "mel": "mercearia", "cafe": "mercearia", "café": "mercearia",
    "atum em lata": "mercearia", "sardinha em lata": "mercearia",
    "molho de tomate": "mercearia", "whey": "mercearia", "creatina": "mercearia",
    "chocolate 70": "mercearia", "pasta de amendoim": "mercearia",
}


def _norm(nome: str) -> str:
    return nome.strip().lower()


def setor_de(nome: str) -> str:
    n = _norm(nome)
    if n in SETOR_PADRAO:
        return SETOR_PADRAO[n]
    for chave, setor in SETOR_PADRAO.items():
        if chave in n:
            return setor
    return "outros"


def consolidar(plano: dict) -> dict[str, dict[str, dict]]:
    """Agrega gramas por ingrediente por setor.

    Aceita plano no formato:
    {"refeicoes": [{"nome": "...", "ingredientes": [{"nome": "...", "gramas": 100}]}]}
    OU
    {"dias": {"segunda": {"refeicoes": [...]}, ...}}
    """
    agregado: dict[str, dict[str, dict]] = defaultdict(lambda: defaultdict(lambda: {"gramas": 0.0, "unidades": None}))

    def _comer_refeicoes(refs: list):
        for ref in refs:
            for ing in ref.get("ingredientes", []):
                nome = ing.get("nome", "").strip()
                if not nome:
                    continue
                gramas = float(ing.get("gramas", 0) or 0)
                setor = setor_de(nome)
                item = agregado[setor][_norm(nome)]
                item["nome_display"] = nome if "nome_display" not in item else item["nome_display"]
                item["gramas"] += gramas
                unidade = ing.get("unidade")
                if unidade and item["unidades"] is None:
                    item["unidades"] = unidade

    if "refeicoes" in plano:
        _comer_refeicoes(plano["refeicoes"])
    if "dias" in plano:
        for _dia, bloco in plano["dias"].items():
            _comer_refeicoes(bloco.get("refeicoes", []))

    return agregado


def renderizar(agregado: dict, precos: dict | None = None) -> str:
    linhas = ["# Lista de mercado — semana\n"]
    custo_total = 0.0
    ordem = {s: i for i, s in enumerate(SETORES)}
    setores_ordenados = sorted(agregado.keys(), key=lambda s: ordem.get(s, 99))

    for setor in setores_ordenados:
        titulo = {
            "hortifruti": "Hortifruti",
            "acougue": "Açougue / Peixaria",
            "laticinios": "Laticínios / Ovos",
            "graos_secos": "Grãos e secos",
            "padaria": "Padaria",
            "mercearia": "Mercearia / Suplementos",
            "outros": "Outros",
        }.get(setor, setor.title())
        linhas.append(f"\n## {titulo}\n")
        itens = sorted(agregado[setor].items())
        for chave, dados in itens:
            nome = dados.get("nome_display", chave)
            gramas = dados["gramas"]
            if gramas >= 1000:
                qtd = f"{gramas / 1000:.2f} kg"
            else:
                qtd = f"{int(round(gramas))} g"
            linha = f"- {nome} — {qtd}"
            if precos and chave in precos:
                preco_kg = precos[chave]
                custo = (gramas / 1000) * preco_kg
                custo_total += custo
                linha += f"  _(≈ R$ {custo:.2f})_"
            linhas.append(linha)

    if precos:
        linhas.append(f"\n---\n\n**Custo estimado total: R$ {custo_total:.2f}**")

    return "\n".join(linhas) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description="Consolida plano em lista de mercado")
    p.add_argument("--plano", required=True, type=Path, help="arquivo JSON do plano")
    p.add_argument("--precos", type=Path, help="JSON opcional {ingrediente: preço_kg_brl}")
    p.add_argument("--saida", type=Path, help="arquivo markdown de saída (default: stdout)")
    args = p.parse_args()

    plano = json.loads(args.plano.read_text(encoding="utf-8"))
    precos = None
    if args.precos and args.precos.exists():
        precos = json.loads(args.precos.read_text(encoding="utf-8"))
        precos = {_norm(k): float(v) for k, v in precos.items()}

    agregado = consolidar(plano)
    md = renderizar(agregado, precos)

    if args.saida:
        args.saida.write_text(md, encoding="utf-8")
        print(f"gravado em {args.saida}")
    else:
        sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
