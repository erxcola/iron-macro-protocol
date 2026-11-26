#!/usr/bin/env python3
"""DB wrapper para nutri-personal. SQLite em ~/.nutri-personal/progress.sqlite.

CLI:
  db.py init                        aplica schema (idempotente)
  db.py read --last N               últimos N registros por tabela (default medicoes)
  db.py read --table T --last N
  db.py add-medicao --data YYYY-MM-DD --peso 85.2 [--bf-min 18 --bf-max 22 ...]
  db.py add-treino --data YYYY-MM-DD --exercicio "agachamento" --series 4 --reps 8 --carga 100 [--rpe 8]
  db.py add-foto --data YYYY-MM-DD --angulo frontal --caminho /abs/path
  db.py add-plano --data-inicio YYYY-MM-DD --objetivo cutting --caminho-md /abs/path --tdee 2800 --kcal 2300 --p 180 --c 220 --g 70

API Python: import db; conn = db.connect(); db.ensure_schema(conn); ...
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path.home() / ".nutri-personal"
DB_PATH = ROOT / "progress.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS medicoes (
  id INTEGER PRIMARY KEY,
  data DATE NOT NULL,
  peso_kg REAL,
  bf_estimado_min REAL,
  bf_estimado_max REAL,
  circ_cintura_cm REAL,
  circ_quadril_cm REAL,
  circ_braco_cm REAL,
  circ_coxa_cm REAL,
  circ_peitoral_cm REAL,
  notas TEXT
);

CREATE TABLE IF NOT EXISTS treinos_executados (
  id INTEGER PRIMARY KEY,
  data DATE NOT NULL,
  exercicio TEXT NOT NULL,
  series INTEGER,
  reps INTEGER,
  carga_kg REAL,
  rpe REAL,
  notas TEXT
);

CREATE TABLE IF NOT EXISTS fotos (
  id INTEGER PRIMARY KEY,
  data DATE NOT NULL,
  angulo TEXT CHECK(angulo IN ('frontal','lateral','dorsal','outro')),
  caminho TEXT NOT NULL,
  observacoes TEXT
);

CREATE TABLE IF NOT EXISTS planos (
  id INTEGER PRIMARY KEY,
  data_inicio DATE NOT NULL,
  data_fim DATE,
  objetivo TEXT,
  caminho_md TEXT NOT NULL,
  tdee_kcal INTEGER,
  calorias_alvo INTEGER,
  proteina_g INTEGER,
  carbo_g INTEGER,
  gordura_g INTEGER
);

CREATE INDEX IF NOT EXISTS idx_medicoes_data ON medicoes(data);
CREATE INDEX IF NOT EXISTS idx_treinos_data ON treinos_executados(data);
CREATE INDEX IF NOT EXISTS idx_treinos_exercicio ON treinos_executados(exercicio);
CREATE INDEX IF NOT EXISTS idx_fotos_data ON fotos(data);
CREATE INDEX IF NOT EXISTS idx_planos_inicio ON planos(data_inicio);
"""

TABLES = ("medicoes", "treinos_executados", "fotos", "planos")


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def read_last(conn: sqlite3.Connection, table: str, n: int) -> list[dict]:
    if table not in TABLES:
        raise ValueError(f"tabela inválida: {table}")
    order_col = "data_inicio" if table == "planos" else "data"
    rows = conn.execute(
        f"SELECT * FROM {table} ORDER BY {order_col} DESC, id DESC LIMIT ?", (n,)
    ).fetchall()
    return [dict(r) for r in rows]


def add_medicao(conn: sqlite3.Connection, **kw) -> int:
    cols = (
        "data", "peso_kg", "bf_estimado_min", "bf_estimado_max",
        "circ_cintura_cm", "circ_quadril_cm", "circ_braco_cm",
        "circ_coxa_cm", "circ_peitoral_cm", "notas",
    )
    vals = [kw.get(c) for c in cols]
    cur = conn.execute(
        f"INSERT INTO medicoes ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
        vals,
    )
    conn.commit()
    return cur.lastrowid


def add_treino(conn: sqlite3.Connection, **kw) -> int:
    cols = ("data", "exercicio", "series", "reps", "carga_kg", "rpe", "notas")
    vals = [kw.get(c) for c in cols]
    cur = conn.execute(
        f"INSERT INTO treinos_executados ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
        vals,
    )
    conn.commit()
    return cur.lastrowid


def add_foto(conn: sqlite3.Connection, **kw) -> int:
    cols = ("data", "angulo", "caminho", "observacoes")
    vals = [kw.get(c) for c in cols]
    cur = conn.execute(
        f"INSERT INTO fotos ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
        vals,
    )
    conn.commit()
    return cur.lastrowid


def add_plano(conn: sqlite3.Connection, **kw) -> int:
    cols = (
        "data_inicio", "data_fim", "objetivo", "caminho_md",
        "tdee_kcal", "calorias_alvo", "proteina_g", "carbo_g", "gordura_g",
    )
    vals = [kw.get(c) for c in cols]
    cur = conn.execute(
        f"INSERT INTO planos ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
        vals,
    )
    conn.commit()
    return cur.lastrowid


def _emit(rows: list[dict]) -> None:
    json.dump(rows, sys.stdout, ensure_ascii=False, indent=2, default=str)
    sys.stdout.write("\n")


def main() -> int:
    p = argparse.ArgumentParser(description="nutri-personal DB wrapper")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="aplica schema (idempotente)")

    r = sub.add_parser("read", help="lê últimos registros")
    r.add_argument("--table", default="medicoes", choices=TABLES)
    r.add_argument("--last", type=int, default=3)

    m = sub.add_parser("add-medicao")
    m.add_argument("--data", required=True)
    m.add_argument("--peso", type=float)
    m.add_argument("--bf-min", type=float)
    m.add_argument("--bf-max", type=float)
    m.add_argument("--cintura", type=float)
    m.add_argument("--quadril", type=float)
    m.add_argument("--braco", type=float)
    m.add_argument("--coxa", type=float)
    m.add_argument("--peitoral", type=float)
    m.add_argument("--notas")

    t = sub.add_parser("add-treino")
    t.add_argument("--data", required=True)
    t.add_argument("--exercicio", required=True)
    t.add_argument("--series", type=int)
    t.add_argument("--reps", type=int)
    t.add_argument("--carga", type=float)
    t.add_argument("--rpe", type=float)
    t.add_argument("--notas")

    f = sub.add_parser("add-foto")
    f.add_argument("--data", required=True)
    f.add_argument("--angulo", required=True, choices=["frontal", "lateral", "dorsal", "outro"])
    f.add_argument("--caminho", required=True)
    f.add_argument("--observacoes")

    pl = sub.add_parser("add-plano")
    pl.add_argument("--data-inicio", required=True)
    pl.add_argument("--data-fim")
    pl.add_argument("--objetivo")
    pl.add_argument("--caminho-md", required=True)
    pl.add_argument("--tdee", type=int)
    pl.add_argument("--kcal", type=int)
    pl.add_argument("--p", type=int, help="proteína g")
    pl.add_argument("--c", type=int, help="carbo g")
    pl.add_argument("--g", type=int, help="gordura g")

    args = p.parse_args()
    conn = connect()
    ensure_schema(conn)

    if args.cmd == "init":
        print(f"schema aplicado em {DB_PATH}")
        return 0

    if args.cmd == "read":
        _emit(read_last(conn, args.table, args.last))
        return 0

    if args.cmd == "add-medicao":
        rid = add_medicao(
            conn,
            data=args.data, peso_kg=args.peso,
            bf_estimado_min=args.bf_min, bf_estimado_max=args.bf_max,
            circ_cintura_cm=args.cintura, circ_quadril_cm=args.quadril,
            circ_braco_cm=args.braco, circ_coxa_cm=args.coxa,
            circ_peitoral_cm=args.peitoral, notas=args.notas,
        )
        print(rid)
        return 0

    if args.cmd == "add-treino":
        rid = add_treino(
            conn,
            data=args.data, exercicio=args.exercicio,
            series=args.series, reps=args.reps,
            carga_kg=args.carga, rpe=args.rpe, notas=args.notas,
        )
        print(rid)
        return 0

    if args.cmd == "add-foto":
        rid = add_foto(
            conn, data=args.data, angulo=args.angulo,
            caminho=args.caminho, observacoes=args.observacoes,
        )
        print(rid)
        return 0

    if args.cmd == "add-plano":
        rid = add_plano(
            conn,
            data_inicio=args.data_inicio, data_fim=args.data_fim,
            objetivo=args.objetivo, caminho_md=args.caminho_md,
            tdee_kcal=args.tdee, calorias_alvo=args.kcal,
            proteina_g=args.p, carbo_g=args.c, gordura_g=args.g,
        )
        print(rid)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
