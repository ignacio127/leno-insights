#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normaliza las claves de 'turno' dentro de master.json para que todas las
sucursales usen el mismo estándar: Mañana / Mediodia / Noche / After
(sin acentos, "After" con A mayúscula solamente).

Corrige el legado de nombres con sucursal pegada (ej. "Noche Tafi Viejo")
y el viejo "AFTER" en mayúsculas, generado antes del renombre en Gesdatta.

MODO POR DEFECTO: dry-run — solo imprime qué cambiaría, no escribe nada.
Para aplicar de verdad: python normalizar_turnos.py --aplicar

Uso:
    python normalizar_turnos.py            # dry-run, solo audita
    python normalizar_turnos.py --aplicar   # escribe master.json normalizado
"""
import json, os, sys, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER_PATH = os.path.join(HERE, "master.json")

# Si "Tarde" (legado, solo Independencia) tiene que ir a otro lado, cambiar acá:
DESTINO_TARDE = "Mediodia"


def normalize_turno(raw):
    """Colapsa cualquier variante cruda de turno_id al estándar de 4 categorías.
    Usa matching por prefijo para blindar contra futuros nombres con sucursal
    pegada, sin depender de una lista fija de strings ya vistos."""
    r = (raw or "").strip()
    if not r:
        return "?"  # sin turno_id — se reporta aparte, no se inventa nada
    ru = r.upper()
    if ru.startswith("AFTER"):
        return "After"
    if ru.startswith("NOCHE"):
        return "Noche"
    if ru.startswith("MEDIODIA"):
        return "Mediodia"
    if ru.startswith("TARDE"):
        return DESTINO_TARDE
    if ru.startswith("MA") and "ANA" in ru.replace("Ñ", "N"):
        # cubre "Mañana" y variantes sin ñ
        return "Mañana"
    return r  # desconocido — no lo toco, pero lo reporto como alerta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true",
                     help="Si no se pasa, corre en modo dry-run (solo audita).")
    args = ap.parse_args()

    if not os.path.exists(MASTER_PATH):
        sys.exit(f"ERROR: no encuentro {MASTER_PATH}")

    master = json.load(open(MASTER_PATH, encoding="utf-8"))
    an = master.get("analytics", {})

    cambios = []       # (periodo, sucursal, clave_vieja, clave_nueva, monto)
    desconocidas = []  # claves que no matchearon ningún patrón conocido
    sin_cambio = 0

    for periodo, brs in an.items():
        for br, a in brs.items():
            turno = a.get("turno", {})
            nuevo_turno = {}
            for k, v in turno.items():
                nk = normalize_turno(k)
                if nk == k:
                    sin_cambio += 1
                elif nk == k.strip() and nk not in ("?",):
                    pass
                if nk not in ("?",) and nk == k:
                    pass
                nuevo_turno[nk] = nuevo_turno.get(nk, 0) + v
                if nk != k:
                    cambios.append((periodo, br, k, nk, v))
                if nk == k and k not in ("Mañana", "Mediodia", "Noche", "After", "?"):
                    desconocidas.append((periodo, br, k, v))
            turno.clear()
            turno.update(nuevo_turno)

    print(f"=== DRY-RUN: {'DESACTIVADO (se va a escribir master.json)' if args.aplicar else 'activo (no se escribe nada)'} ===\n")

    print(f"Cambios de clave detectados: {len(cambios)}")
    for periodo, br, k_old, k_new, v in cambios:
        print(f"  [{periodo}] {br}: {k_old!r:28s} -> {k_new!r:12s} (monto: {v:,.0f})")

    if desconocidas:
        print(f"\n⚠ Claves NO reconocidas por ningún patrón ({len(desconocidas)}) — revisar a mano:")
        for periodo, br, k, v in desconocidas:
            print(f"  [{periodo}] {br}: {k!r} (monto: {v:,.0f})")
    else:
        print("\nSin claves desconocidas — todo matcheó a alguna de las 4 categorías.")

    print(f"\nClaves que ya estaban bien y no cambiaron: {sin_cambio}")

    if not args.aplicar:
        print("\n>>> Esto fue un DRY-RUN. Nada se escribió.")
        print(">>> Si el plan de arriba te cierra, volvé a correr con --aplicar")
        return

    with open(MASTER_PATH, "w", encoding="utf-8") as f:
        json.dump(master, f, ensure_ascii=False, indent=1)
    print(f"\n✔ master.json actualizado en {MASTER_PATH}")


if __name__ == "__main__":
    main()
