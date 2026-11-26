#!/usr/bin/env python3
"""Sync de treinos do Hevy Pro para o SQLite local.

API: https://api.hevyapp.com/v1
Auth: header `api-key: <chave>` (chave vem de HEVY_API_KEY ou ~/.nutri-personal/hevy.key).
Nunca loga nem imprime a chave.

Endpoints usados:
  GET /v1/workouts?page=N&pageSize=10        lista paginada
  GET /v1/workouts/count                     total (para saber quantas páginas)

Mapeia cada set de cada exercício para uma linha em treinos_executados.
Dedupe simples: (data, exercicio, series, reps, carga_kg) — se já existe linha com os
cinco iguais na mesma data, pula. Não é perfeito mas evita spam em re-sync.

CLI:
  hevy_sync.py                     puxa últimas 10 sessões (1 página)
  hevy_sync.py --paginas 5         puxa 5 páginas
  hevy_sync.py --desde 2026-10-01  para no primeiro treino anterior à data
  hevy_sync.py --dry-run           baixa e mostra o que inseriria, sem gravar
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import db

HEVY_BASE = "https://api.hevyapp.com/v1"
KEY_FILE = Path.home() / ".nutri-personal" / "hevy.key"


def _load_key() -> str:
    key = os.environ.get("HEVY_API_KEY")
    if key:
        return key.strip()
    if KEY_FILE.exists():
        key = KEY_FILE.read_text().strip()
        if key:
            return key
    print(
        "erro: chave Hevy não encontrada. "
        f"defina HEVY_API_KEY ou crie {KEY_FILE} com a chave (uma linha, sem aspas).",
        file=sys.stderr,
    )
    sys.exit(2)


def _request(path: str, api_key: str, params: dict | None = None) -> dict:
    url = f"{HEVY_BASE}{path}"
    if params:
        from urllib.parse import urlencode
        url = f"{url}?{urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={
            "api-key": api_key,
            "accept": "application/json",
            "user-agent": "nutri-personal-sync/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="replace")[:500]
        print(f"erro HTTP {e.code} em {path}: {msg}", file=sys.stderr)
        raise
    except urllib.error.URLError as e:
        print(f"erro de rede em {path}: {e.reason}", file=sys.stderr)
        raise


def _parse_date(s: str | None) -> str | None:
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return s[:10]


def _ja_existe(conn, data_iso: str, exercicio: str, series: int, reps: int | None, carga: float | None) -> bool:
    row = conn.execute(
        """
        SELECT 1 FROM treinos_executados
        WHERE data = ? AND exercicio = ?
          AND IFNULL(series,-1) = IFNULL(?,-1)
          AND IFNULL(reps,-1)   = IFNULL(?,-1)
          AND IFNULL(carga_kg,-1) = IFNULL(?,-1)
        LIMIT 1
        """,
        (data_iso, exercicio, series, reps, carga),
    ).fetchone()
    return row is not None


def _mapear_workout(wk: dict) -> list[dict]:
    """Transforma 1 workout Hevy em N linhas treinos_executados (1 por set)."""
    data_iso = _parse_date(wk.get("start_time") or wk.get("created_at") or wk.get("updated_at"))
    if not data_iso:
        return []
    notas_treino = wk.get("title") or wk.get("name") or ""
    linhas = []
    for ex in wk.get("exercises", []):
        exercicio = ex.get("title") or ex.get("name") or ex.get("exercise_template", {}).get("title")
        if not exercicio:
            continue
        sets = ex.get("sets", []) or []
        for idx, s in enumerate(sets, start=1):
            if s.get("type") in ("warmup", "warm_up"):
                continue
            reps = s.get("reps")
            carga = s.get("weight_kg")
            if carga is None:
                carga = s.get("weight")
            rpe = s.get("rpe")
            linhas.append({
                "data": data_iso,
                "exercicio": exercicio,
                "series": idx,
                "reps": int(reps) if reps is not None else None,
                "carga_kg": float(carga) if carga is not None else None,
                "rpe": float(rpe) if rpe is not None else None,
                "notas": notas_treino or None,
            })
    return linhas


def sincronizar(paginas: int, desde: date | None, dry_run: bool) -> tuple[int, int]:
    api_key = _load_key()
    conn = db.connect()
    db.ensure_schema(conn)

    inseridos = 0
    pulados = 0
    parar = False

    for page in range(1, paginas + 1):
        if parar:
            break
        try:
            resp = _request("/workouts", api_key, {"page": page, "pageSize": 10})
        except Exception:
            break

        workouts = resp.get("workouts") or resp.get("data") or []
        if not workouts:
            break

        for wk in workouts:
            data_iso = _parse_date(wk.get("start_time") or wk.get("created_at"))
            if desde and data_iso and data_iso < desde.isoformat():
                parar = True
                break

            for linha in _mapear_workout(wk):
                if _ja_existe(
                    conn,
                    linha["data"], linha["exercicio"],
                    linha["series"], linha["reps"], linha["carga_kg"],
                ):
                    pulados += 1
                    continue
                if dry_run:
                    print(
                        f"[dry] {linha['data']} {linha['exercicio']} "
                        f"s{linha['series']} x{linha['reps']} @ {linha['carga_kg']}kg"
                    )
                else:
                    db.add_treino(conn, **linha)
                inseridos += 1

    conn.close()

    perfil_path = Path.home() / ".nutri-personal" / "perfil.json"
    if perfil_path.exists() and not dry_run:
        try:
            perfil = json.loads(perfil_path.read_text())
            perfil.setdefault("integracoes", {}).setdefault("hevy", {})
            perfil["integracoes"]["hevy"]["ativo"] = True
            perfil["integracoes"]["hevy"]["ultimo_sync"] = datetime.now().isoformat(timespec="seconds")
            perfil_path.write_text(json.dumps(perfil, indent=2, ensure_ascii=False))
        except (json.JSONDecodeError, OSError):
            pass

    return inseridos, pulados


def main() -> int:
    p = argparse.ArgumentParser(description="Sync treinos Hevy → SQLite local")
    p.add_argument("--paginas", type=int, default=1, help="quantas páginas de 10 puxar")
    p.add_argument("--desde", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
                   help="para no primeiro treino anterior a esta data (YYYY-MM-DD)")
    p.add_argument("--dry-run", action="store_true", help="mostra sem gravar")
    args = p.parse_args()

    inseridos, pulados = sincronizar(args.paginas, args.desde, args.dry_run)
    acao = "simularia inserir" if args.dry_run else "inseridos"
    print(f"{acao}: {inseridos} sets | pulados (já existentes): {pulados}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
