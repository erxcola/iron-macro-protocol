#!/usr/bin/env python3
"""Inicializa ~/.nutri-personal/: diretórios, SQLite schema, perfil.json vazio.

Idempotente: rodar várias vezes não destrói dados existentes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import db

ROOT = Path.home() / ".nutri-personal"
SUBDIRS = ("planos", "fotos", "receitas")
PERFIL = ROOT / "perfil.json"

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


def main() -> int:
    ROOT.mkdir(parents=True, exist_ok=True)
    for sub in SUBDIRS:
        (ROOT / sub).mkdir(exist_ok=True)

    conn = db.connect()
    db.ensure_schema(conn)
    conn.close()

    if not PERFIL.exists():
        PERFIL.write_text(json.dumps(PERFIL_SKELETON, indent=2, ensure_ascii=False))
        print(f"criado perfil vazio em {PERFIL}")
    else:
        print(f"perfil já existe em {PERFIL} (preservado)")

    print(f"diretórios prontos em {ROOT}")
    print(f"schema aplicado em {db.DB_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
