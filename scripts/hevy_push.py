#!/usr/bin/env python3
"""Push de rotinas de treino para o Hevy Pro via API v1.

API: https://api.hevyapp.com/v1
Auth: header `api-key: <chave>` (HEVY_API_KEY ou ~/.nutri-personal/hevy.key).

Endpoints usados:
  GET  /v1/exercise_templates?page=N&pageSize=100   cache local de templates
  POST /v1/routines                                 cria rotina no app Hevy

Formato de entrada (--file rotina.json):
{
  "title": "Push A — Hipertrofia",
  "notes": "Foco em amplitude alongada e 1-2 RIR",
  "folder_id": null,
  "exercises": [
    {
      "name": "Incline Dumbbell Bench Press",
      "rest_seconds": 120,
      "notes": "Pausa leve no alongamento",
      "sets": [
        {"type": "warmup", "weight_kg": 16, "reps": 10},
        {"type": "normal", "weight_kg": 28, "rep_range": {"start": 8, "end": 12}}
      ]
    }
  ]
}
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

HEVY_BASE = "https://api.hevyapp.com/v1"
DATA_DIR = Path.home() / ".nutri-personal"
KEY_FILE = DATA_DIR / "hevy.key"
CACHE_FILE = DATA_DIR / "hevy_templates.json"


def _load_key() -> str:
    key = os.environ.get("HEVY_API_KEY")
    if key:
        return key.strip()
    if KEY_FILE.exists():
        text = KEY_FILE.read_text(encoding="utf-8").strip()
        if text:
            return text
    raise SystemExit(
        f"erro: chave Hevy não encontrada. Defina HEVY_API_KEY ou crie {KEY_FILE}."
    )


def _request(method: str, path: str, api_key: str, body: dict | None = None) -> dict:
    url = f"{HEVY_BASE}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {
        "api-key": api_key,
        "accept": "application/json",
        "user-agent": "nutri-personal-push/1.0",
    }
    if data is not None:
        headers["content-type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="replace")[:500]
        raise SystemExit(f"erro HTTP {e.code} em {method} {path}: {msg}")


def fetch_templates(api_key: str, refresh: bool = False) -> list[dict]:
    if CACHE_FILE.exists() and not refresh:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))

    templates: list[dict] = []
    page = 1
    while True:
        resp = _request("GET", f"/exercise_templates?page={page}&pageSize=100", api_key)
        batch = resp.get("exercise_templates") or []
        if not batch:
            break
        templates.extend(batch)
        page_count = resp.get("page_count") or 1
        if page >= page_count:
            break
        page += 1

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(templates, ensure_ascii=False, indent=2), encoding="utf-8")
    return templates


def resolve_template_id(name: str, templates: list[dict]) -> tuple[str, str]:
    by_lower = {t["title"].lower(): t for t in templates if "title" in t and "id" in t}
    if name.lower() in by_lower:
        t = by_lower[name.lower()]
        return t["id"], t["title"]

    matches = difflib.get_close_matches(name.lower(), list(by_lower.keys()), n=1, cutoff=0.55)
    if matches:
        t = by_lower[matches[0]]
        return t["id"], t["title"]

    raise SystemExit(f"Template não encontrado no Hevy para '{name}'. Use --search para listar.")


def build_payload(spec: dict, templates: list[dict]) -> dict:
    exercises_out = []
    for ex in spec.get("exercises", []):
        if ex.get("exercise_template_id"):
            tid = ex["exercise_template_id"]
            matched_name = ex.get("name", tid)
        else:
            tid, matched_name = resolve_template_id(ex["name"], templates)
            if matched_name.lower() != ex["name"].lower():
                print(f"[match] '{ex['name']}' -> '{matched_name}' ({tid})")

        sets_out = []
        for s in ex.get("sets", []):
            set_obj: dict = {"type": s.get("type", "normal")}
            if s.get("weight_kg") is not None:
                set_obj["weight_kg"] = s["weight_kg"]
            if s.get("reps") is not None:
                set_obj["reps"] = s["reps"]
            if s.get("rep_range") is not None:
                set_obj["rep_range"] = s["rep_range"]
            sets_out.append(set_obj)

        exercises_out.append({
            "exercise_template_id": tid,
            "superset_id": ex.get("superset_id"),
            "rest_seconds": ex.get("rest_seconds", 90),
            "notes": ex.get("notes", ""),
            "sets": sets_out,
        })

    return {
        "routine": {
            "title": spec["title"],
            "folder_id": spec.get("folder_id"),
            "notes": spec.get("notes", ""),
            "exercises": exercises_out,
        }
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Push de rotinas para o Hevy Pro")
    p.add_argument("--file", type=Path, help="Arquivo JSON com a rotina")
    p.add_argument("--search", type=str, help="Busca exercise_template_id no Hevy por nome")
    p.add_argument("--refresh-templates", action="store_true", help="Atualiza cache de templates do Hevy")
    p.add_argument("--dry-run", action="store_true", help="Mostra payload sem enviar para a API")
    args = p.parse_args()

    api_key = _load_key()
    templates = fetch_templates(api_key, refresh=args.refresh_templates)

    if args.search:
        q = args.search.lower()
        hits = [t for t in templates if q in t.get("title", "").lower()][:20]
        for t in hits:
            print(f"{t['id']} | {t['title']} ({t.get('primary_muscle_group', '?')})")
        return 0

    if not args.file:
        p.print_help()
        return 1

    spec = json.loads(args.file.read_text(encoding="utf-8"))
    payload = build_payload(spec, templates)

    if args.dry_run:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    resp = _request("POST", "/routines", api_key, payload)
    print(json.dumps(resp, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
