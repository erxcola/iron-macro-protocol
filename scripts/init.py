#!/usr/bin/env python3
"""Inicializa ~/.nutri-personal/: diretórios, SQLite schema, perfil.json vazio.

Idempotente: rodar várias vezes não destrói dados existentes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import db

BASE_ROOT = Path.home() / ".nutri-personal"
SUBDIRS = ("planos", "fotos", "receitas")


def resolve_root(perfil: str | None) -> Path:
    if not perfil or perfil == "default":
        return BASE_ROOT
    safe = "".join(c for c in perfil.strip() if c.isalnum() or c in ("-", "_"))
    if not safe:
        raise SystemExit("Nome de perfil inválido.")
    return BASE_ROOT / "profiles" / safe


def main() -> int:
    p = argparse.ArgumentParser(description="Inicializa workspace de perfil para nutri-personal")
    p.add_argument("--perfil", type=str, default=None, help="Nome do perfil (ex: joao). Padrão: perfil principal")
    p.add_argument("--listar", action="store_true", help="Lista perfis existentes")
    args = p.parse_args()

    if args.listar:
        profiles_dir = BASE_ROOT / "profiles"
        names = ["default"] if (BASE_ROOT / "perfil.json").exists() else []
        if profiles_dir.exists():
            names.extend(sorted(d.name for d in profiles_dir.iterdir() if d.is_dir()))
        print("Perfis:", ", ".join(names) if names else "(nenhum)")
        return 0

    root = resolve_root(args.perfil)
    perfil_path = root / "perfil.json"
    db_path = root / "progress.sqlite"

    root.mkdir(parents=True, exist_ok=True)
    for sub in SUBDIRS:
        (root / sub).mkdir(exist_ok=True)

    conn = db.connect(db_path)
    db.ensure_schema(conn)
    conn.close()

    if not perfil_path.exists():
        skeleton = json.loads(json.dumps(PERFIL_SKELETON))
        if args.perfil:
            skeleton["identidade"]["nome"] = args.perfil
        perfil_path.write_text(json.dumps(skeleton, indent=2, ensure_ascii=False))
        print(f"criado perfil vazio em {perfil_path}")
    else:
        print(f"perfil já existe em {perfil_path} (preservado)")

    print(f"diretórios prontos em {root}")
    print(f"schema aplicado em {db_path}")
    return 0

PERFIL_SKELETON = {
    "identidade": {
        "nome": None,
        "idade": None,
        "sexo_biologico": None,
        "altura_cm": None,
    },
    "composicao": {
        "peso_atual_kg": None,
        "peso_alvo_kg": None,
        "bf_estimado_min": None,
        "bf_estimado_max": None,
    },
    "objetivo": None,
    "nivel": None,
    "treino": {
        "dias_por_semana": None,
        "minutos_por_sessao": None,
        "equipamento": None,
    },
    "saude": {
        "lesoes": [],
        "cirurgias": [],
        "condicoes": [],
        "medicamentos": [],
    },
    "nutricao": {
        "alergias": [],
        "restricoes": [],
        "aversoes": [],
        "orcamento_semanal_brl": None,
    },
    "rotina": {
        "sono_horas": None,
        "trabalho": None,
        "estresse": None,
    },
    "analise_inicial": None,
    "integracoes": {
        "hevy": {
            "ativo": False,
            "ultimo_sync": None,
        },
    },
}


if __name__ == "__main__":
    sys.exit(main())
