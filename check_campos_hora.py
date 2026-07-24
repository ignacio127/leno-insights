#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico: ¿el API de Gesdatta (restoVentasComanda) ya trae un campo de
hora/timestamp que ingestor.py hoy no está leyendo?

Uso: colocar este archivo en la MISMA carpeta que ingestor.py y config.env
    python check_campos_hora.py

No modifica nada. Solo hace UNA llamada (1 sucursal, 1 día) y muestra:
  1) Todas las keys que trae cada fila cruda (no solo las que usa ingestor.py)
  2) Cualquier key que "suene" a hora/fecha/timestamp
  3) Una fila completa de ejemplo, para inspección visual
"""
import json, os, sys, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
API_URL = "https://app.gesdatta.com/reportesApi/restoVentasComanda"

# --- Elegí una sucursal y un día CON VENTAS conocidas para el test ---
CLIENTE   = "Leno S.R.L."   # cambiar si querés probar otra razón social
SUCURSAL  = "6"              # Tafi Viejo, según BRANCHES de ingestor.py
DESDE     = "2026-07-20"
HASTA     = "2026-07-20"

def load_env():
    email = os.environ.get("GESDATTA_EMAIL", "").strip()
    pw    = os.environ.get("GESDATTA_PASSWORD", "").strip()
    if email and pw:
        return email, pw
    p = os.path.join(HERE, "config.env")
    if not os.path.exists(p):
        sys.exit("ERROR: falta config.env y no hay variables de entorno GESDATTA_EMAIL/GESDATTA_PASSWORD")
    env = {}
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    email = env.get("GESDATTA_EMAIL", "").strip()
    pw    = env.get("GESDATTA_PASSWORD", "").strip()
    if not email or not pw:
        sys.exit("ERROR: completá GESDATTA_EMAIL y GESDATTA_PASSWORD en config.env")
    return email, pw

def api_call(email, pw):
    body = json.dumps({
        "email": email, "password": pw, "cliente": CLIENTE,
        "f_desde": DESDE, "f_hasta": HASTA, "estado": "",
        "sucursal_resto_id": SUCURSAL,
    }).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }
    req = urllib.request.Request(API_URL, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read().decode("utf-8"))
    return data.get("datos", [])

def looks_like_time(key):
    key_l = key.lower()
    return any(s in key_l for s in [
        "hora", "time", "timestamp", "created", "alta", "apertura",
        "cierre", "ingreso", "fecha_hora", "datetime", "ts_"
    ])

def main():
    email, pw = load_env()
    print(f"Consultando {CLIENTE} / sucursal {SUCURSAL} / {DESDE} a {HASTA}...")
    rows = api_call(email, pw)
    if not rows:
        sys.exit("Sin filas devueltas para ese rango/sucursal. Probá otra fecha con ventas conocidas.")

    all_keys = set()
    for r in rows:
        all_keys.update(r.keys())

    print(f"\nTotal de filas: {len(rows)}")
    print(f"\n=== TODAS las keys que trae el JSON crudo ({len(all_keys)}) ===")
    for k in sorted(all_keys):
        flag = "  <-- posible campo de hora/timestamp" if looks_like_time(k) else ""
        print(f"  - {k}{flag}")

    candidatos = [k for k in all_keys if looks_like_time(k)]
    print(f"\n=== Candidatos a hora/timestamp: {candidatos or 'NINGUNO ENCONTRADO'} ===")

    print("\n=== Fila de ejemplo completa (primera fila) ===")
    print(json.dumps(rows[0], ensure_ascii=False, indent=2))

    if candidatos:
        print("\n>>> Revisá el valor real de esos campos en la fila de ejemplo de arriba.")
        print(">>> Si alguno trae hora real (ej: '20:14' o '2026-07-20T20:14:00'), ")
        print(">>> el dato YA está disponible y no hace falta pedirle nada a Gesdatta:")
        print(">>> solo hay que extenderlo en ingestor.py.")
    else:
        print("\n>>> No apareció ningún campo con nombre asociado a hora en este endpoint.")
        print(">>> Con esto confirmado, el paso siguiente es pedirle a Gesdatta que lo exponga")
        print(">>> (ver mensaje sugerido para soporte).")

if __name__ == "__main__":
    main()
