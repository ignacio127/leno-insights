#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LENO Insights — Ingestor API Gesdatta v2
=========================================
Reconstruye TODAS las secciones del dashboard en una corrida:
  analytics, rankings, descdet, peya, especial2026, mundiales, burgermes

Uso:
    python ingestor.py
    python ingestor.py --desde 2026-06-01 --hasta 2026-06-30 --periodo Junio
"""
import json, os, re, sys, argparse, subprocess, urllib.request, urllib.error
from collections import defaultdict, Counter
from datetime import date, datetime, timedelta

HERE   = os.path.dirname(os.path.abspath(__file__))
API_URL = "https://app.gesdatta.com/reportesApi/restoVentasComanda"
API_URL_CUENTAS = "https://app.gesdatta.com/reportesApi/restoVentasCuenta"

BRANCHES = [
    # (cliente exacto, sucursal_resto_id, nombre_sucursal, grupo)
    ("Leno S.R.L.",      "9", "Aconquija",     "SRL"),
    ("Leno S.R.L.",      "8", "Barrio Norte",  "SRL"),
    ("Leno S.R.L.",      "6", "Tafi Viejo",    "SRL"),
    ("Blend S.A.S.",     "1", "Independencia", "Franquicias"),
    ("FRANQUICIAR SAS",  "1", "Barrio Sur",    "Franquicias"),
    ("Mafra S.A.S.",     "1", "Peron",         "Franquicias"),
    ("Mafra S.A.S.",     "2", "FLIP",          "Franquicias"),
]

DEF_PERIODO, DEF_DESDE, DEF_HASTA = "Julio", "2026-07-01", "2026-07-31"

MES_ABBR = {"01":"ene","02":"feb","03":"mar","04":"abr","05":"may","06":"jun",
             "07":"jul","08":"ago","09":"sep","10":"oct","11":"nov","12":"dic"}

# ===========================================================================
# Credenciales
# ===========================================================================
def load_env():
    # Primero intenta variables de entorno (GitHub Actions, CI/CD)
    email = os.environ.get("GESDATTA_EMAIL", "").strip()
    pw    = os.environ.get("GESDATTA_PASSWORD", "").strip()
    if email and pw:
        return email, pw
    # Fallback: config.env local (uso en PC)
    p = os.path.join(HERE, "config.env")
    if not os.path.exists(p):
        sys.exit("ERROR: falta config.env y no hay variables de entorno GESDATTA_EMAIL/GESDATTA_PASSWORD")
    env = {}
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1); env[k.strip()] = v.strip()
    email = env.get("GESDATTA_EMAIL", "").strip()
    pw    = env.get("GESDATTA_PASSWORD", "").strip()
    if not email or not pw:
        sys.exit("ERROR: completá GESDATTA_EMAIL y GESDATTA_PASSWORD en config.env")
    return email, pw

# ===========================================================================
# API
# ===========================================================================
def api_call(url, cliente, suc, desde, hasta, email, pw, estado=""):
    body = json.dumps({
        "email": email, "password": pw, "cliente": cliente,
        "f_desde": desde, "f_hasta": hasta, "estado": estado,
        "sucursal_resto_id": suc,
    }).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept":        "application/json",
        "User-Agent":    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        bt = e.read().decode("utf-8", "ignore")[:300]
        hint = ""
        if e.code == 403 or "1010" in bt:
            hint = "  → Bloqueo Cloudflare. Corré desde la misma red donde funciona tu Power Query."
        print(f"  ‼ ERROR HTTP {e.code} en {cliente}/{suc}: {bt}\n{hint}")
        return None  # main() lo trata igual que 'SIN DATOS' y conserva el valor previo
    except Exception as e:
        print(f"  ‼ ERROR de red en {cliente}/{suc}: {e}")
        return None
    return data.get("datos", [])

# ===========================================================================
# Utilidades
# ===========================================================================
def num(x):
    if x is None: return 0.0
    if isinstance(x, (int, float)): return float(x)
    s = str(x).strip().replace("$","").replace(" ","")
    if "," in s and "." in s: s = s.replace(".","").replace(",",".")
    elif "," in s: s = s.replace(",",".")
    try: return float(s)
    except: return 0.0

def build_prodcat(master):
    v = defaultdict(Counter)
    for per in master["rankings"]:
        for br in master["rankings"][per]:
            for it in master["rankings"][per][br]["items"]:
                v[it["nombre"]][(it.get("cat"), it.get("madre"), it.get("promo"))] += 1
    return {k: c.most_common(1)[0][0] for k, c in v.items()}

def fmt_rango(desde, hasta):
    """'2026-06-01','2026-06-30' -> '01/06–30/06'"""
    d = desde.split("-"); h = hasta.split("-")
    return f"{d[2]}/{d[1]}–{h[2]}/{h[1]}"

ENVIO = re.compile(r"ENV[IÍ]O",  re.I)
SERVM = re.compile(r"SERVICIO.*MESA|CUBIERTO", re.I)

# ===========================================================================
# TRANSFORM
# ===========================================================================
def transform(rows, prodcat):
    canal = defaultdict(float); turno = defaultdict(float); comp = defaultdict(float)
    desc = 0.0; descdet = defaultdict(float)
    comp_desc = defaultdict(float)  # descuentos por tipo de comprobante: FAB/FAX/S/C/etc.
    agg   = defaultdict(lambda: [0.0, 0.0])
    comandas = set(); gross = 0.0
    comanda_tot = defaultdict(float)  # comanda_id (CMD-...) -> venta real sumada (auditoria 23/07/2026)
    envu = envi = smu = smi = 0.0
    # PY tracking
    py_agg  = defaultdict(lambda: [0.0, 0.0, set()])  # nombre -> [u, imp, cmds]
    py_dias = defaultdict(lambda: [0.0, 0.0])          # fecha  -> [imp, u]
    # Diario por fecha (para weekly/monthly) — solo bruto, mismo criterio que branch_tot
    daily = defaultdict(float)  # date object -> gross
    # Descuento diario real (para calcular neto exacto por día, no un ratio promedio del mes)
    daily_desc = defaultdict(float)  # date object -> descuento (negativo)
    daily_cupon_py = defaultdict(float)  # "DD/MM" -> cupón PedidosYa del día (negativo)
    # S/C drill-down: comandas sin comprobante con sus ítems
    sc_cmds = defaultdict(lambda: {"fecha": "", "turno": "", "canal": "", "importe": 0.0, "items": []})

    for r in rows:
        a = (r.get("articulo_id") or "").strip()
        if not a or "PRUEBA" in a.upper(): continue
        v = num(r.get("total")); c = num(r.get("cantidad"))
        if v == 0: continue
        fecha_raw = (r.get("fecha") or "").strip()
        if v < 0:
            ing_d = (r.get("ingreso") or "").strip()
            tipo_d = ing_d.split()[0] if ing_d else "S/C"
            comp_desc[tipo_d] += v  # negativo
            desc += v; descdet[a] += -v
            # bucket diario del descuento, con el mismo criterio de fecha que "daily"
            if fecha_raw:
                try:
                    dd = datetime.strptime(fecha_raw.split(" ")[0], "%d/%m/%Y").date()
                    daily_desc[dd] += v
                except Exception:
                    pass
                if a == "CUPON PY":
                    fecha_py = fecha_raw
                    if "/" in fecha_py: fecha_py = "/".join(fecha_py.split("/")[:2])  # "01/06"
                    daily_cupon_py[fecha_py] += v
            continue
        gross += v
        cl = (r.get("tipo_delivery") or "").strip() or "Salón/Mostrador"
        canal[cl] += v
        turno[(r.get("turno_id") or "").strip() or "?"] += v
        ing = (r.get("ingreso") or "").strip()
        tipo_comp = ing.split()[0] if ing else "S/C"
        comp[tipo_comp] += v
        cn = str(r.get("comprobante_numero") or "").strip()
        if cn:
            comandas.add(cn)
            comanda_tot[cn] += v
        # S/C drill-down: acumular ítems por comanda sin comprobante
        if not ing and cn:
            fecha_raw = (r.get("fecha") or "").strip()
            sc = sc_cmds[cn]
            sc["importe"] += v
            sc["items"].append({"nombre": a, "u": int(c), "imp": round(v)})
            if not sc["fecha"]:
                sc["fecha"] = fecha_raw
                sc["turno"] = (r.get("turno_id") or "").strip() or "?"
                sc["canal"] = cl
        agg[a][0] += c; agg[a][1] += v
        if ENVIO.search(a): envu += c; envi += v
        if SERVM.search(a): smu += c; smi += v
        # fecha -> bucket diario
        if fecha_raw:
            try:
                d = datetime.strptime(fecha_raw.split(" ")[0], "%d/%m/%Y").date()
                daily[d] += v
            except Exception:
                pass
        # PY
        if cl == "PEDIDOS YA":
            fecha = fecha_raw
            if "/" in fecha: fecha = "/".join(fecha.split("/")[:2])   # "01/06"
            py_agg[a][0] += c; py_agg[a][1] += v
            if cn: py_agg[a][2].add(cn)
            py_dias[fecha][0] += v; py_dias[fecha][1] += c

    items = []
    for a, (u, imp) in agg.items():
        cat, madre, promo = prodcat.get(a, (None, a, False))
        items.append({"nombre": a, "u": int(u), "imp": round(imp),
                      "cat": cat, "promo": promo, "madre": madre})
    items.sort(key=lambda x: -x["imp"])
    nc = len(comandas)
    analytics = {
        "canal":       {k: round(x) for k, x in canal.items()},
        "turno":       {k: round(x) for k, x in turno.items()},
        "comprobante": {k: round(x) for k, x in comp.items()},
        "comp_desc":   {k: round(x) for k, x in comp_desc.items()},
        "descuentos":  round(desc),
        "envios":      {"u": int(envu), "imp": round(envi)},
        "servmesa":    {"u": int(smu),  "imp": round(smi)},
        "comandas": nc, "ticket": round(gross / nc) if nc else 0, "gross": round(gross),
    }
    py_data = {
        "agg":  {k: [v[0], v[1], list(v[2])] for k, v in py_agg.items()},
        "dias": {f: [round(x[0]), round(x[1])] for f, x in py_dias.items()},
    }
    sc_list = sorted([
        {
            "cmd":     k,
            "fecha":   v["fecha"],
            "turno":   v["turno"],
            "canal":   v["canal"],
            "importe": round(v["importe"]),
            "items":   v["items"],
        }
        for k, v in sc_cmds.items() if k
    ], key=lambda x: x["fecha"])
    return analytics, {"items": items, "gross": round(gross)}, \
           {k: round(x) for k, x in descdet.items()}, round(gross), py_data, daily, daily_desc, \
           dict(daily_cupon_py), sc_list, dict(comanda_tot)

# ===========================================================================
# REBUILD WEEKLY / MONTHLY (histórico de cadena, fuera del selector de período)
# ===========================================================================
WK_KEY = {  # nombre interno -> key usado en el histórico (weekly/monthly)
    "Aconquija": "Aconquija", "Barrio Norte": "Barrio Norte", "Tafi Viejo": "Tafi Viejo",
    "Independencia": "Independencia", "Barrio Sur": "Barrio Sur", "Peron": "Peron", "FLIP": "Flip",
}
MESES_ES = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
            7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
SRL_BR = {"Aconquija", "Barrio Norte", "Tafi Viejo"}

def _semana_label(d):
    """Lunes de la semana ISO que contiene a d, formato 'DD.MM al DD.MM'."""
    lunes = d - timedelta(days=d.weekday())
    domingo = lunes + timedelta(days=6)
    return f"{lunes.day:02d}.{lunes.month:02d} al {domingo.day:02d}.{domingo.month:02d}", lunes

def rebuild_weekly_monthly(master, daily_by_branch, daily_desc_by_branch, args):
    """daily_by_branch: {branch: {date: gross}}. daily_desc_by_branch: {branch: {date: descuento (neg.)}}.
    Recalcula semanas y meses que caen dentro del rango consultado; preserva todo lo anterior.
    Si una sucursal no respondió en esta corrida (SIN DATOS), su valor
    previo en esa semana/mes se mantiene en vez de pisarse con 0."""
    weeks  = defaultdict(lambda: defaultdict(float))   # semana_label -> {branch_key: imp}
    weeks_desc = defaultdict(lambda: defaultdict(float))   # semana_label -> {branch_key: desc}
    months = defaultdict(lambda: defaultdict(float))   # mes_nombre   -> {branch_key: imp}
    months_desc = defaultdict(lambda: defaultdict(float))   # mes_nombre -> {branch_key: desc}
    month_dias = defaultdict(set)                       # mes_nombre -> {fechas con datos}

    for branch, dailymap in daily_by_branch.items():
        key = WK_KEY.get(branch, branch)
        for d, imp in dailymap.items():
            wl, _ = _semana_label(d)
            weeks[wl][key] += imp
            mn = MESES_ES[d.month]
            months[mn][key] += imp
            month_dias[mn].add(d)

    for branch, descmap in daily_desc_by_branch.items():
        key = WK_KEY.get(branch, branch)
        for d, v in descmap.items():
            wl, _ = _semana_label(d)
            weeks_desc[wl][key] += v
            mn = MESES_ES[d.month]
            months_desc[mn][key] += v

    SRL_KEYS = ("Aconquija", "Barrio Norte", "Tafi Viejo")
    FR_KEYS  = ("Independencia", "Barrio Sur", "Peron", "Flip")

    def _merge(existing, touched, touched_desc=None):
        """Parte del registro previo (si hay), pisa solo las sucursales
        tocadas en esta corrida, recalcula SRL/Franquicias/Total (bruto).
        Si además llega el descuento real de las sucursales tocadas, lo
        guarda como '{sucursal}_desc' y recalcula SRL_desc/Franquicias_desc/
        Total_desc — pero solo cuando TODAS las sucursales del grupo tienen
        ese dato (para no mezclar semanas/meses viejos, sin descuento real,
        con los nuevos)."""
        keys_ok = set(SRL_KEYS) | set(FR_KEYS)
        out = {k: v for k, v in (existing or {}).items()
               if k in keys_ok or (k.endswith("_desc") and k[:-5] in keys_ok)}
        for k, v in touched.items():
            out[k] = round(v)
        if touched_desc:
            for k, v in touched_desc.items():
                out[k + "_desc"] = round(v)
        srl = sum(out.get(k, 0) for k in SRL_KEYS)
        fr  = sum(out.get(k, 0) for k in FR_KEYS)
        out["SRL"] = round(srl); out["Franquicias"] = round(fr); out["Total"] = round(srl + fr)
        if all((k + "_desc") in out for k in SRL_KEYS):
            out["SRL_desc"] = sum(out.get(k + "_desc", 0) for k in SRL_KEYS)
        if all((k + "_desc") in out for k in FR_KEYS):
            out["Franquicias_desc"] = sum(out.get(k + "_desc", 0) for k in FR_KEYS)
        if all((k + "_desc") in out for k in list(SRL_KEYS) + list(FR_KEYS)):
            out["Total_desc"] = out.get("SRL_desc", 0) + out.get("Franquicias_desc", 0)
        return out

    # --- merge semanal: pisa solo sucursales tocadas, preserva el resto ---
    existentes = {w["semana"]: i for i, w in enumerate(master.get("weekly", []))}
    weekly_list = list(master.get("weekly", []))
    for wl, d in weeks.items():
        idx = existentes.get(wl)
        prev = weekly_list[idx] if idx is not None else {}
        entry = {"semana": wl, **_merge(prev, d, weeks_desc.get(wl, {}))}
        if idx is not None:
            weekly_list[idx] = entry
        else:
            weekly_list.append(entry)
    # orden cronológico real (no alfabético): por (mes, dia) del inicio de semana
    def _wkey(w):
        dd, mm = w["semana"].split(" al ")[0].split(".")
        return (int(mm), int(dd))
    weekly_list.sort(key=_wkey)
    master["weekly"] = weekly_list

    # --- merge mensual: pisa solo sucursales tocadas, preserva el resto ---
    import calendar
    monthly = dict(master.get("monthly", {}))
    anio = int(args.desde.split("-")[0])
    mes_num = {v: k for k, v in MESES_ES.items()}
    for mn, d in months.items():
        prev = monthly.get(mn, {})
        entry = _merge(prev, d, months_desc.get(mn, {}))
        dias_con_datos = len(month_dias[mn])
        ndias_mes = calendar.monthrange(anio, mes_num[mn])[1]
        entry["_dias"] = dias_con_datos
        entry["_parcial"] = dias_con_datos < ndias_mes
        monthly[mn] = entry
    master["monthly"] = monthly

    # --- daily_data por período: {fecha: {branch: imp, SRL:, Franquicias:, Total:}} ---
    # Acumula por fecha cruzando todas las sucursales del rango
    P = args.periodo
    SRL_BR   = [b for _,_,b,g in BRANCHES if g=="SRL"]
    FRANQ_BR = [b for _,_,b,g in BRANCHES if g=="Franquicias"]
    daily_by_fecha = defaultdict(lambda: defaultdict(float))
    for branch, dailymap in daily_by_branch.items():
        for d, imp in dailymap.items():
            fecha = f"{d.day:02d}/{d.month:02d}"
            daily_by_fecha[fecha][branch] += imp

    # Descuento real por fecha/sucursal (para neto exacto por día, ver auditoría 02/07/2026)
    daily_desc_by_fecha = defaultdict(lambda: defaultdict(float))
    for branch, descmap in daily_desc_by_branch.items():
        for d, v in descmap.items():
            fecha = f"{d.day:02d}/{d.month:02d}"
            daily_desc_by_fecha[fecha][branch] += v

    # Leer daily_data previo del período para mergear (preservar fechas ya guardadas)
    prev_daily = {row["fecha"]: dict(row)
                  for row in master.get("daily_data", {}).get(P, [])}
    for fecha, bmap in daily_by_fecha.items():
        entry = prev_daily.get(fecha, {"fecha": fecha})
        for b, v in bmap.items():
            entry[b] = round(v)
        # Descuentos del día para las sucursales tocadas esta corrida (negativo, o 0 si no hubo)
        dmap = daily_desc_by_fecha.get(fecha, {})
        for b in bmap:
            entry[b + "_desc"] = round(dmap.get(b, 0.0))
        # Recalcular SRL / Franquicias / Total (bruto)
        entry["SRL"]         = sum(entry.get(b, 0) for b in SRL_BR)
        entry["Franquicias"] = sum(entry.get(b, 0) for b in FRANQ_BR)
        entry["Total"]       = entry["SRL"] + entry["Franquicias"]
        # Recalcular SRL_desc / Franquicias_desc / Total_desc — solo si TODAS las
        # sucursales del grupo tienen el campo _desc (si falta alguna, se omite el
        # agregado para no mezclar neto exacto con bruto de un histórico viejo)
        if all((b + "_desc") in entry for b in SRL_BR):
            entry["SRL_desc"] = sum(entry.get(b + "_desc", 0) for b in SRL_BR)
        if all((b + "_desc") in entry for b in FRANQ_BR):
            entry["Franquicias_desc"] = sum(entry.get(b + "_desc", 0) for b in FRANQ_BR)
        if all((b + "_desc") in entry for b in SRL_BR + FRANQ_BR):
            entry["Total_desc"] = entry.get("SRL_desc", 0) + entry.get("Franquicias_desc", 0)
        prev_daily[fecha]    = entry

    # Ordenar cronológicamente (dd/mm → sort por mes luego día)
    def _dsort(f):
        d2, m2 = f.split("/"); return (int(m2), int(d2))
    master.setdefault("daily_data", {})[P] = sorted(prev_daily.values(), key=lambda x: _dsort(x["fecha"]))

# ===========================================================================
# MEDIOS DE PAGO (restoVentasCuenta) — categorías confirmadas con datos reales
# (Tafi Viejo + Independencia, jun-2026; FLIP confirmado igual al resto de
# Franquicias; Barrio Norte = "Rivadavia" en Gesdatta).
# ===========================================================================
CUENTA_MAP_SRL = {
    "CAJA": "Efectivo",
    "LENO+ EFECTIVO": "Efectivo",
    "LENO+ A COBRAR": "LENO+ (canal propio)",
    "MERCADOPAGO A COBRAR": "MercadoPago/QR",
    "PEDIDOS YA A COBRAR": "PedidosYa",
    "NAVE A COBRAR": "Nave",  # Aconquija (SRL) sí opera con Nave; se asumía Franquicia-only (sin_clasificar_detalle Junio: $879.200)
}
CUENTA_MAP_FRANQ = {
    "CAJA": "Efectivo",
    "CAJA MERCADOPAGO": "MercadoPago/QR",
    "CAJA PAYWAY": "Tarjeta (PayWay)",
    "CAJA NAVE": "Nave",
    "PEDIDOS YA A COBRAR": "PedidosYa",
}
# Sucursales con nombre distinto en Gesdatta vs. el nombre usado en el dashboard.
# Si al correr contra las 7 sucursales aparece otro alias, agregarlo acá.
ALIAS_SUCURSAL = {"Barrio Norte": "RIVADAVIA"}


def normalizar_cuenta(cuenta_id, branch, grupo):
    """cuenta_id crudo de Gesdatta -> categoría canónica.

    Case-insensitive y con strip del sufijo de sucursal / '($)', a propósito:
    ya tuvimos un bug de capitalización con 'Flip'/'FLIP' en build.py y no
    queremos repetirlo acá con 'CAJA' vs 'Caja' vs 'caja'. Todo lo que no
    matchea cae en 'Sin clasificar' -- no se pierde, queda visible.
    """
    s = (cuenta_id or "").upper().strip()
    s = s.replace("($)", "").strip()
    for alias in (branch, ALIAS_SUCURSAL.get(branch, branch)):
        if alias:
            s = s.replace(alias.upper(), "").strip()
    s = re.sub(r"\s+", " ", s)
    mapa = CUENTA_MAP_SRL if grupo == "SRL" else CUENTA_MAP_FRANQ
    return mapa.get(s, "Sin clasificar")


# Confirmado con datos reales de Peron e Independencia (jun-2026): cuando el mismo
# monto exacto se repite varias veces el mismo día y la misma cuenta, en
# comprobantes distintos, a veces NO son ventas reales -- es una liquidación de
# plataforma (Pedidos Ya / Nave) o un cierre de caja en lote que Gesdatta pega en
# cada comanda del lote en vez de repartir una vez por pedido. Llegó a explicar
# 40-67% del total de una sucursal en un mes.
#
# FALSO POSITIVO confirmado con datos reales de Aconquija (jul-2026): un combo de
# PedidosYa a $8.940 se repitió 21 veces el mismo día -- eso es simplemente un
# combo popular, no una liquidación en bloque (-$734.900 de venta real si se
# excluía por monto/repetición nomás).
#
# INTENTO 1 (DUP_CLUSTER_MIN + MONTO_SOSPECHOSO_MIN, ya reemplazado): exigir
# repetición Y magnitud. Falló con datos reales de Peron (jul-2026): el mismo día
# 04/07 tuvo un cluster real de $121.000 x3 (explica el 100% del gap de ese día)
# Y clusters de venta real de $14.100 x4 / $20.000 x4 -- magnitud y repetición NO
# alcanzan para separarlos (ambos < o cerca de $100K, ambos con 3-4 repeticiones).
#
# INTENTO 2 (solo espaciado de comprobante, ya reemplazado): funcionó perfecto
# en los 3 casos chicos de Peron jul-2026 (gap 0,0% exacto) pero REGRESIONÓ el
# caso grande ya resuelto de Peron jun-2026 (+40,21% en vez de +1,46%) e
# Independencia (+47,64% jun, +21,09% jul) -- un lote de 20-30+ comandas en un
# mes completo no siempre tiene comprobantes perfectamente consecutivos/parejos
# (hay pedidos reales intercalados en el medio), así que el espaciado solo no
# detecta los lotes grandes que el criterio de monto+repetición SÍ agarraba bien.
#
# CRITERIO ACTUAL: los dos criterios en OR, no uno reemplazando al otro.
# Se excluye un cluster si CUALQUIERA de los dos se cumple:
#   (a) monto >= MONTO_SOSPECHOSO_MIN y repetición >= DUP_CLUSTER_MIN
#       -> agarra lotes grandes obvios sin importar el comprobante (recupera el
#          comportamiento bueno de Peron/Independencia jun-2026).
#   (b) espaciado de comprobante sospechoso (ver es_cluster_sospechoso)
#       -> agarra lotes chicos que el piso de monto no ve (Peron jul-2026).
# Ningún caso real confirmado hasta ahora activa (a) y no (b) o viceversa de
# forma contradictoria, pero no está probado contra las 7 sucursales todavía.
def es_cluster_sospechoso(comprobantes):
    """comprobantes: lista de N° de comprobante (int) que comparten el mismo
    día+categoría+monto. True si el espaciado entre ellos es perfectamente
    regular Y compacto (paso <=3) -- eso es lo que separó, con datos reales,
    los 3 duplicados confirmados de Peron (jul-2026) de los clusters de venta
    real del mismo día. Con solo 2 comprobantes se exige paso==1 (consecutivos
    estrictos) porque dos puntos siempre "parecen" un espaciado regular."""
    nums = sorted(comprobantes)
    if len(nums) < 2:
        return False
    diffs = [nums[i + 1] - nums[i] for i in range(len(nums) - 1)]
    if len(set(diffs)) != 1:
        return False
    paso = diffs[0]
    if len(nums) >= 3:
        return 0 < paso <= 3
    return paso == 1


_COMPROBANTE_NUM_RE = re.compile(r"(\d+)$")


def _comprobante_num(comprobante_str):
    m = _COMPROBANTE_NUM_RE.search(str(comprobante_str or ""))
    return int(m.group(1)) if m else None


DUP_CLUSTER_MIN = 5
MONTO_SOSPECHOSO_MIN = 100_000

# Auditoria 23/07/2026 (Ramiro): categorias donde se confirmo con datos reales
# que Gesdatta puede pegarle el mismo monto (de un turno/lote) a varias comandas
# distintas en vez de repartirlo. Nave/PedidosYa/Tarjeta/MercadoPago: liquidacion
# de plataforma. Efectivo: NO es liquidacion de plataforma (no hay intermediario)
# pero se confirmo el MISMO patron via cierre de turno/caja -- ver caso FLIP
# 19/07/2026 (16 comandas, 3 grupos con monto identico repetido; API=$1.944.990
# vs real por comanda=$369.150, ratio 5.3x). Se corrige igual: cruzando contra
# comanda_tot (dato confiable de restoVentasComanda). LENO+/NCB-SID/Pendiente
# quedan afuera por ahora: sin evidencia de que tengan este bug.
CATEGORIAS_CON_LIQUIDACION_EN_LOTE = {"Nave", "PedidosYa", "Tarjeta (PayWay)", "MercadoPago/QR", "Efectivo"}

# Respaldo del heuristico viejo (monto+espaciado de comprobante), usado SOLO
# cuando no tenemos comanda_tot para cruzar (ver fetch_medios_pago). Sucursales
# confirmadas SIN patron de liquidacion en lote: ahi el caso de 2 comprobantes
# consecutivos con igual monto es ruido de combos populares, no evidencia.
BRANCHES_SIN_LOTE_CONFIRMADO = {"Aconquija", "Barrio Norte", "Tafi Viejo", "Barrio Sur"}


def fetch_medios_pago(cliente, suc, branch, grupo, desde, hasta, email, pw, comanda_tot=None):
    """Devuelve (dailymap, duplicados, sin_clasificar_raw) para una sucursal y
    rango de fechas.
    dailymap: {date: {categoria: monto}} | None. None = mismo criterio que
    comandas: 'sin dato esta corrida' (no se pisa lo que ya había).
    duplicados: None si no se detectó ningún cluster sospechoso, o
    {"monto_excluido": X, "clusters": [...]} con el detalle de lo que se corrigió.
    sin_clasificar_raw: None si no hubo nada sin mapear, o {cuenta_id_crudo:
    monto} con el TEXTO EXACTO que llegó de Gesdatta -- para poder agregarlo a
    CUENTA_MAP_SRL/CUENTA_MAP_FRANQ sin tener que pedir otra extracción manual.
    Filtra pago != True: no confirmado todavía con datos reales que existan
    filas con pago:false (cuenta corriente sin cobrar), se deja el filtro por
    las dudas para no contar como venta algo pendiente de cobro.

    NCB/SID: por decisión de Ramiro, en el desglose visible NO existe una
    categoría "Sin clasificar" -- todo lo que no se pueda mapear a un medio de
    pago real (cuenta_id vacío, Notas de Crédito, o texto que todavía no está
    en CUENTA_MAP_SRL/FRANQ) cae en "NCB/SID". El texto crudo de lo que SÍ
    tenía cuenta_id pero no matcheó ningún mapeo se sigue guardando en
    sin_clasificar_raw (y de ahí a sin_clasificar_detalle en master.json) para
    poder seguir auditando y cerrando gaps de diccionario nuevos (como pasó
    con "NAVE A COBRAR") sin que la plata quede invisible en el medio.

    comanda_tot: {comanda_id (CMD-...): venta_real} calculado por transform()
    sobre Ventas por Comanda de LA MISMA corrida. Auditoria 23/07/2026: el
    campo "comprobante" de esta API (restoVentasCuenta) es el ID de comanda
    (ej. "CMD-00002507"), NO un numero de comprobante fiscal -- confirmado
    contra la API en vivo. Con eso podemos cruzar cada comanda de Medios de
    Pago contra su venta real, en vez de adivinar duplicados por patron de
    monto+espaciado. Caso real que confirmo el mecanismo: Peron, 09/07/2026,
    PedidosYa -- 20 comandas DISTINTAS (CMD-00002562 a CMD-00002581) mostraban
    cada una $513.590 (el mismo numero, 20 veces). Sumando la venta real de
    esas 20 comandas (Ventas por Comanda) da EXACTAMENTE $513.590 -- o sea,
    PedidosYa le pega el total del lote completo a cada comanda del lote, en
    vez de repartir lo que corresponde a cada una. El heuristico viejo
    (monto+espaciado, mas abajo) queda solo de respaldo para comandas que no
    aparezcan en comanda_tot (p.ej. si Ventas por Comanda no trajo dato esta
    corrida)."""
    rows = api_call(API_URL_CUENTAS, cliente, suc, desde, hasta, email, pw)
    if rows is None:
        return None, None, None
    comanda_tot = comanda_tot or {}
    sin_clasificar_raw = defaultdict(float)  # cuenta_id crudo -> monto (solo lo NO mapeado)
    por_comanda = defaultdict(list)  # comanda_id -> [(date, categoria, monto, comprobante_num_o_None), ...]
    for r in rows:
        try:
            d = datetime.strptime(r["fecha"], "%d/%m/%Y").date()
        except Exception:
            continue
        monto = num(r.get("total"))
        comp_num = _comprobante_num(r.get("comprobante"))
        comanda_id = str(r.get("comprobante") or "").strip()
        if r.get("pago") is not True:
            # NO se descarta más. Con Independencia confirmamos con datos reales
            # que esto puede ser cuenta corriente genuina O simplemente el pedido
            # sigue abierto en el momento exacto de la corrida -- el dashboard se
            # actualiza 3x/día con datos en vivo de un período que todavía no
            # cerró. Antes esto generaba una brecha fantasma contra Facturación
            # (que sí reconoce la venta); ahora queda visible como "Pendiente"
            # en vez de desaparecer en silencio.
            por_comanda[comanda_id].append((d, "Pendiente", monto, comp_num))
            continue
        cuenta_id_crudo = r.get("cuenta_id", "")
        if not (cuenta_id_crudo or "").strip():
            cat = "NCB/SID"
        else:
            cat = normalizar_cuenta(cuenta_id_crudo, branch, grupo)
            if cat == "Sin clasificar":
                sin_clasificar_raw[cuenta_id_crudo] += monto
                cat = "NCB/SID"  # visible como NCB/SID; el texto crudo queda auditado en sin_clasificar_raw
        por_comanda[comanda_id].append((d, cat, monto, comp_num))

    out = defaultdict(lambda: defaultdict(float))
    clusters = []
    monto_excluido_total = 0.0
    TOLERANCIA_COMANDA = 2.0  # pesos, margen de redondeo entre las dos APIs
    entradas_fallback = defaultdict(list)  # (date, categoria) -> [(monto, comp_num), ...], SOLO sin comanda_tot

    for comanda_id, filas in por_comanda.items():
        real = comanda_tot.get(comanda_id) if comanda_id else None
        cats_presentes = set(f[1] for f in filas)
        solo_plataforma = bool(cats_presentes) and cats_presentes.issubset(CATEGORIAS_CON_LIQUIDACION_EN_LOTE)
        cuenta_sum = sum(f[2] for f in filas)

        if real is not None and solo_plataforma and (cuenta_sum - real) > TOLERANCIA_COMANDA:
            # Lote de plataforma pegado a esta comanda (ver docstring) -- se
            # corrige usando la venta real de Ventas por Comanda como fuente
            # de verdad, repartiendo proporcionalmente entre las filas que
            # tenia (normalmente 1 sola).
            excluido = cuenta_sum - real
            monto_excluido_total += excluido
            factor = (real / cuenta_sum) if cuenta_sum else 0.0
            clusters.append({
                "fecha": filas[0][0].isoformat(),
                "categoria": ",".join(sorted(cats_presentes)),
                "comanda": comanda_id,
                "monto_cuenta": round(cuenta_sum),
                "monto_real": round(real),
                "excluido": round(excluido),
                "via": "cruce_comanda_real",
            })
            for d, cat, monto, comp_num in filas:
                out[d][cat] += monto * factor
        else:
            for d, cat, monto, comp_num in filas:
                out[d][cat] += monto
                if comanda_id and real is None:
                    entradas_fallback[(d, cat)].append((monto, comp_num))

    # --- respaldo: heuristico viejo (monto+espaciado), SOLO para lo que no
    # tenia comanda_tot con que cruzar esta corrida ---
    for (d, cat), pares in entradas_fallback.items():
        if cat not in CATEGORIAS_CON_LIQUIDACION_EN_LOTE:
            continue
        por_monto = defaultdict(list)
        for monto, comp_num in pares:
            por_monto[monto].append(comp_num)
        for monto, comps in por_monto.items():
            if not monto:
                continue
            rep = len(comps)
            comps_validos = [c for c in comps if c is not None]
            criterio_a = monto >= MONTO_SOSPECHOSO_MIN and rep >= DUP_CLUSTER_MIN
            criterio_b = (len(comps_validos) == len(comps)
                          and es_cluster_sospechoso(comps_validos))
            if criterio_b and rep == 2 and branch in BRANCHES_SIN_LOTE_CONFIRMADO:
                criterio_b = False
            if not (criterio_a or criterio_b):
                continue  # ni lote grande obvio ni espaciado sospechoso -> venta real
            excluido = monto * (rep - 1)
            monto_excluido_total += excluido
            clusters.append({
                "fecha": d.isoformat(), "categoria": cat,
                "monto": round(monto), "repeticiones": rep,
                "excluido": round(excluido),
                "via": "respaldo_sin_comanda_tot",
            })
            out[d][cat] -= excluido  # ya se habia sumado completo arriba

    dailymap = {d: dict(cats) for d, cats in out.items()}
    duplicados = {"monto_excluido": round(monto_excluido_total), "clusters": clusters} if clusters else None
    sc_raw = {k: round(v) for k, v in sin_clasificar_raw.items()} if sin_clasificar_raw else None
    return dailymap, duplicados, sc_raw


def rebuild_medios_pago(master, periodo, daily_cuenta_by_branch, dup_by_branch=None, sc_raw_by_branch=None):
    """daily_cuenta_by_branch: {branch: {date: {categoria: monto}} | None}.
    dup_by_branch: {branch: {"monto_excluido":X,"clusters":[...]} | None} --
    lo que fetch_medios_pago descartó por sospecha de liquidación duplicada.
    sc_raw_by_branch: {branch: {cuenta_id_crudo: monto} | None} -- lo que cayó
    en "Sin clasificar", con el texto EXACTO tal como llegó de Gesdatta, para
    poder agregarlo al mapeo sin pedir otra extracción manual.

    Guarda total por período (branch_tot-like) y desglose semanal, usando las
    MISMAS semanas ISO que rebuild_weekly_monthly (_semana_label) para que
    'Medios de Pago' y 'Resumen' coincidan.

    NOTA: el merge semanal acá recalcula desde cero las semanas tocadas en esta
    corrida -- no tiene el manejo fino de "preservar semana vieja si esta
    corrida no trajo dato" que sí tiene rebuild_weekly_monthly. Alcanza porque
    cada corrida trae el rango completo pedido; si en el futuro se corre con
    rangos parciales día por día, revisar este merge con el mismo cuidado.
    """
    mp = master.setdefault("medios_pago", {})
    por_periodo = mp.setdefault("por_periodo", {})
    por_periodo[periodo] = por_periodo.get(periodo, {})
    semanal = mp.setdefault("semanal", {})  # {branch: {semana_label: {categoria: monto}}}
    dup_periodo = mp.setdefault("duplicados_excluidos", {}).setdefault(periodo, {})
    sc_periodo = mp.setdefault("sin_clasificar_detalle", {}).setdefault(periodo, {})

    for branch, dailymap in daily_cuenta_by_branch.items():
        if not dailymap:
            continue  # None (sin dato esta corrida) o {} (sin filas) -> no tocar lo que ya había
        tot_branch = defaultdict(float)
        sem_branch = semanal.setdefault(branch, {})
        semanas_tocadas = defaultdict(lambda: defaultdict(float))
        for d, cats in dailymap.items():
            wl, _ = _semana_label(d)
            for cat, monto in cats.items():
                semanas_tocadas[wl][cat] += monto
                tot_branch[cat] += monto
        for wl, cats in semanas_tocadas.items():
            sem_branch[wl] = {k: round(v) for k, v in cats.items()}
        por_periodo[periodo][branch] = {k: round(v) for k, v in tot_branch.items()}
        dup = (dup_by_branch or {}).get(branch)
        if dup:
            dup_periodo[branch] = dup
        elif branch in dup_periodo:
            del dup_periodo[branch]  # esta corrida no encontró clusters -> no dejar un aviso viejo colgado
        sc_raw = (sc_raw_by_branch or {}).get(branch)
        if sc_raw:
            sc_periodo[branch] = sc_raw
        elif branch in sc_periodo:
            del sc_periodo[branch]  # esta corrida no encontró nada sin clasificar -> no dejar un aviso viejo colgado


def chequear_reconciliacion_medios_pago(master, periodo, umbral_pct=15.0):
    """Compara la suma de medios_pago por sucursal contra el NETO de
    Facturación (branch_tot BRUTO + descuentos del período, que ya vienen
    negativos) -- NO contra branch_tot crudo.
    Medios de Pago es, por definición, lo que el cliente efectivamente pagó
    (neto). Compararlo contra Bruto genera un sesgo negativo estructural del
    tamaño de la tasa de descuento de cada sucursal, y hace ver como 'problema
    de cobro' algo que es solo descuento. Confirmado con datos reales: Barrio
    Norte Jul-2026 (9 días) -- Bruto $8.834.816, Descuentos -$924.069, Neto
    $7.910.747, Medios de Pago $7.443.187 -> gap vs Bruto -15.75% (falla),
    gap vs Neto -5.91% (dentro de umbral). 10,46 de los 15,75 puntos eran
    descuento, no plata sin clasificar/cobrar.
    Si el desvío contra Neto supera umbral_pct, queda marcado ok:false para
    que build.py lo muestre como alerta, en vez de confiar en el número sin
    chequear."""
    bt = master.get("branch_tot", {}).get(periodo, {})
    an = master.get("analytics", {}).get(periodo, {})
    mp = master.get("medios_pago", {}).get("por_periodo", {}).get(periodo, {})
    out = {}
    for branch, cats in mp.items():
        total_mp = sum(cats.values())
        bruto = bt.get(branch)
        if not bruto:
            continue
        descuentos = an.get(branch, {}).get("descuentos", 0)  # ya viene negativo
        total_comanda = bruto + descuentos  # Neto
        if not total_comanda:
            continue
        gap_pct = round((total_mp - total_comanda) / total_comanda * 100, 2)
        out[branch] = {
            "total_medios_pago": round(total_mp),
            "total_comanda": round(total_comanda),
            "gap_pct": gap_pct,
            "ok": abs(gap_pct) <= umbral_pct,
        }
    rec = master.setdefault("medios_pago", {}).setdefault("reconciliacion", {})
    rec[periodo] = out


def audit(branch, A, R):
    g = A["gross"]
    items_sum = round(sum(i["imp"] for i in R["items"]))
    checks_ok = (round(sum(A["canal"].values())) == g and
                 round(sum(A["turno"].values())) == g and
                 round(sum(A["comprobante"].values())) == g and
                 items_sum == g)
    gap = g - items_sum  # históricamente la brecha aparece siempre acá (items vs gross)
    gap_pct = round(gap / g * 100, 2) if g else 0.0
    flag = "OK " if checks_ok else "‼ "
    fails = "" if checks_ok else f" | FALLA identidad (gap items ${gap:,.0f} · {gap_pct}%)"
    print(f"  {flag}{branch:14} gross ${g:>12,.0f} | desc ${abs(A['descuentos']):>10,.0f} | "
          f"comandas {A['comandas']:>4} | ticket ${A['ticket']:>7,.0f}{fails}")
    dq = {"gross": g, "items_sum": items_sum, "gap": gap, "gap_pct": gap_pct, "ok": checks_ok}
    return checks_ok, dq

# ===========================================================================
# REBUILD PEYA
# ===========================================================================
def rebuild_peya(master, P, py_by_branch, tot_by_branch, daily_cupon_py_by_branch, args):
    peya     = master.get("peya", {})
    rango    = fmt_rango(args.desde, args.hasta)
    # Template de promos: buscar en período existente o legacy plano
    _peya_template = peya.get(P) or next((v for v in peya.values() if isinstance(v, dict) and "promos" in v), peya)
    net_tot  = sum(tot_by_branch.values())

    br_out   = {}; dias_net = defaultdict(lambda:[0.0,0.0])
    dias_br  = {}
    cupon_by = {}; cupon_tot = 0

    for br, py in py_by_branch.items():
        br_imp=0; br_u=0; br_cmds=set()
        br_dias = defaultdict(lambda:[0.0,0.0])
        cupon_dia = daily_cupon_py_by_branch.get(br, {})  # {"DD/MM": cupón del día (negativo)}
        for nombre,(u,imp,cmds) in py["agg"].items():
            br_imp+=imp; br_u+=u; br_cmds.update(cmds)
        for fecha,(imp,u) in py["dias"].items():
            imp_neto = imp + cupon_dia.get(fecha, 0.0)  # cupón ya es negativo
            br_dias[fecha][0]+=imp_neto; br_dias[fecha][1]+=u
            dias_net[fecha][0]+=imp_neto; dias_net[fecha][1]+=u
        cupon = master.get("descdet",{}).get(P,{}).get(br,{}).get("CUPON PY",0)
        cupon_by[br]=round(cupon); cupon_tot+=cupon
        br_ped=len(br_cmds)
        if br_imp>0:
            br_out[br]={
                "imp":   round(br_imp - cupon),
                "bruto": round(br_imp),
                "desc":  -round(cupon),
                "u":     int(br_u),
                "pedidos": br_ped,
                "ticket": round((br_imp-cupon)/br_ped) if br_ped else 0,
                "parcial": False,
                "rango": rango,
            }
        if br_dias:
            dias_br[br]=[{"fecha":f,"imp":round(x[0]),"u":int(x[1])}
                         for f,x in sorted(br_dias.items())]

    # Leer período previo (para mergear 'branches' y luego 'dias'/'diasBr')
    peya_prev = peya.get(P, {}) if isinstance(peya.get(P), dict) else {}

    # Conservar sucursales que no aportaron datos nuevos esta corrida (fallback de API)
    # pero sí tenían PEYA cargado en la corrida anterior — mismo criterio que ya se aplica
    # abajo para 'dias'/'diasBr'. Sin esto, una falla transitoria de API borra temporalmente
    # el detalle de PedidosYa de esa sucursal en vez de conservar el último valor conocido.
    for br, old in peya_prev.get("branches", {}).items():
        if br not in br_out:
            br_out[br] = old
    all_imp  = sum(x["bruto"] for x in br_out.values())
    # Suma de pedidos por sucursal (cada sucursal ya deduplica sus propias comandas
    # correctamente). ANTES se juntaban los números de comanda de las 7 sucursales en
    # un solo set global y se contaba ese set — pero cada sucursal tiene su propio POS,
    # que numera sus comandas desde cero, así que dos sucursales distintas comparten
    # números de comanda todo el tiempo. Ese dedupe cruzado hacía perder ~16% de los
    # pedidos reales en el total de "Todas las sucursales" (verificado con datos de
    # Junio 2026: 4.239 pedidos reales sumados por sucursal vs 3.555 que mostraba el
    # dedupe global — 684 pedidos perdidos).
    all_ped  = sum(x.get("pedidos", 0) for x in br_out.values())
    all_u    = sum(x["u"] for x in br_out.values())
    net_imp  = all_imp - cupon_tot

    # Actualizar totales de promos desde rankings
    rk_all = defaultdict(lambda:{"u":0,"imp":0,"branches":{}})
    for br in master.get("rankings",{}).get(P,{}):
        for it in master["rankings"][P][br]["items"]:
            rk_all[it["nombre"]]["u"]   += it["u"]
            rk_all[it["nombre"]]["imp"] += it["imp"]
            rk_all[it["nombre"]]["branches"][br]={"u":it["u"],"imp":it["imp"]}

    promos_new=[]; cat_acc=defaultdict(lambda:{"imp":0,"u":0})
    cat_br_acc=defaultdict(lambda:defaultdict(lambda:{"imp":0,"u":0}))
    for pr in _peya_template.get("promos",[]):
        hit = rk_all.get(pr["nombre"],{})
        pr2 = dict(pr)
        pr2["imp"]      = hit.get("imp",0)
        pr2["u"]        = hit.get("u",0)
        pr2["branches"] = hit.get("branches",{})
        promos_new.append(pr2)
        c = pr2.get("cat","Always On")
        cat_acc[c]["imp"] += pr2["imp"]; cat_acc[c]["u"] += pr2["u"]
        for br,bv in pr2["branches"].items():
            cat_br_acc[br][c]["imp"] += bv["imp"]; cat_br_acc[br][c]["u"] += bv["u"]

    # Merge de 'dias' (preservar fechas ya guardadas de otro rango)
    prev_dias = {d["fecha"]: d for d in peya_prev.get("dias", [])}
    for d in [{"fecha":f,"imp":round(x[0]),"u":int(x[1])} for f,x in sorted(dias_net.items())]:
        prev_dias[d["fecha"]] = d  # pisa con datos nuevos
    merged_dias = sorted(prev_dias.values(), key=lambda x: (int(x["fecha"].split("/")[1]), int(x["fecha"].split("/")[0])))

    prev_dias_br = peya_prev.get("diasBr", {})
    for br, dlist in dias_br.items():
        prev_br = {d["fecha"]: d for d in prev_dias_br.get(br, [])}
        for d in dlist:
            prev_br[d["fecha"]] = d
        dias_br[br] = sorted(prev_br.values(), key=lambda x: (int(x["fecha"].split("/")[1]), int(x["fecha"].split("/")[0])))

    peya_new = {
        "rango": rango,
        "total": {"imp":round(net_imp),"bruto":round(all_imp),"desc":-round(cupon_tot),
                  "u":all_u,"pedidos":all_ped,
                  "ticket":round(net_imp/all_ped) if all_ped else 0},
        "participacion": round(net_imp/net_tot*100,1) if net_tot else 0,
        "netoRedJunio":  round(net_tot),
        "branches":      br_out,
        "dias":          merged_dias,
        "diasBr":        dias_br,
        "promos":        promos_new,
        "cat":           {c:v for c,v in cat_acc.items()},
        "catBr":         {br:dict(d) for br,d in cat_br_acc.items()},
        "cupones":{
            "total": round(cupon_tot),
            "byBr":  {br:v for br,v in cupon_by.items() if v>0},
            "pctSobrePeya": round(cupon_tot/all_imp*100,1) if all_imp else 0,
        },
        "srlBr":  [b for _,_,b,g in BRANCHES if g=="SRL"],
        "frBr":   [b for _,_,b,g in BRANCHES if g=="Franquicias"],
    }
    # Guardar por período, limpiar legacy plano
    peya_clean = {k: v for k, v in peya.items() if isinstance(v, dict) and k != P}
    peya_clean[P] = peya_new
    master["peya"] = peya_clean

# ===========================================================================
# REBUILD ESPECIAL 2026
# ===========================================================================
def rebuild_especial2026(master, P, args):
    # Leer template de productos del período MÁS RECIENTE que tenga "productos"
    # (excluyendo el período actual P), o del nivel raíz (legacy) si no hay ninguno.
    # IMPORTANTE: se recorre master["periods"] en orden inverso -- no esp_dict.items() --
    # porque los dicts no garantizan orden cronológico y un producto agregado a mano
    # en un período nuevo se perdía en el próximo rebuild si el período más viejo
    # seguía siendo el primero en iterarse.
    esp_dict = master.get("especial2026", {})
    template = None
    for k in reversed(master.get("periods", [])):
        if k == P:
            continue
        v = esp_dict.get(k)
        if isinstance(v, dict) and "productos" in v:
            template = v
            break
    if template is None:
        # fallback: cualquier período con productos, o legacy plano
        for k, v in esp_dict.items():
            if isinstance(v, dict) and "productos" in v:
                template = v
                break
        if template is None and "productos" in esp_dict:
            template = esp_dict  # legacy plano
    if template is None:
        template = {"productos": []}

    esp_new = {
        "rango":   fmt_rango(args.desde, args.hasta),
        "parcial": args.hasta.split("-")[2] not in ("30","31","28","29"),
        "srlBr":   [b for _,_,b,g in BRANCHES if g=="SRL"],
        "frBr":    [b for _,_,b,g in BRANCHES if g=="Franquicias"],
        "productos": [dict(p) for p in template.get("productos", [])],
    }

    rk_all = defaultdict(lambda:{"u":0,"imp":0,"branches":{}})
    for br in master.get("rankings",{}).get(P,{}):
        for it in master["rankings"][P][br]["items"]:
            rk_all[it["nombre"]]["u"]   += it["u"]
            rk_all[it["nombre"]]["imp"] += it["imp"]
            rk_all[it["nombre"]]["branches"][br]={"u":it["u"],"imp":it["imp"]}

    for prod in esp_new["productos"]:
        hit = rk_all.get(prod["nombre"],{})
        prod["u"]        = hit.get("u",0)
        prod["imp"]      = hit.get("imp",0)
        prod["branches"] = hit.get("branches",{})

    esp_new["total"] = {
        "u":   sum(p["u"]   for p in esp_new["productos"]),
        "imp": sum(p["imp"] for p in esp_new["productos"]),
    }
    # Guardar solo las claves por período (limpiar legacy plano)
    master["especial2026"] = {k: v for k, v in esp_dict.items() if isinstance(v, dict) and "rango" in v and k != P}
    master["especial2026"][P] = esp_new

# ===========================================================================
# REBUILD MUNDIALES
# ===========================================================================
def rebuild_mundiales(master, P, args):
    mund_dict = master.get("mundiales", {})
    # Buscar template de productos del período MÁS RECIENTE (excluyendo P),
    # no el primero que aparezca en el dict -- mismo fix que rebuild_especial2026,
    # ver comentario ahí para el detalle del bug original.
    template = None
    for k in reversed(master.get("periods", [])):
        if k == P:
            continue
        v = mund_dict.get(k)
        if isinstance(v, dict) and "productos" in v:
            template = v
            break
    if template is None:
        for k, v in mund_dict.items():
            if isinstance(v, dict) and "productos" in v:
                template = v
                break
        if template is None and "productos" in mund_dict:
            template = mund_dict  # legacy plano
    if template is None:
        template = {"productos": []}

    def _norm(s):
        return s.replace("ELEMMENTAL", "ELEMENTAL")

    rk_upper = defaultdict(lambda: {"u": 0, "imp": 0, "branches": {}})
    for br in master.get("rankings", {}).get(P, {}):
        for it in master["rankings"][P][br]["items"]:
            key = _norm(it["nombre"].upper().strip())
            rk_upper[key]["u"]   += it["u"]
            rk_upper[key]["imp"] += it["imp"]
            rk_upper[key]["branches"][br] = {"u": it["u"], "imp": it["imp"]}

    def match_mundial(nombre):
        key = _norm(nombre.upper().strip())
        es_aros  = "AROS"  in key
        es_papas = "PAPAS" in key
        STOPWORDS = {"CON","DE","LA","EL","LOS","LAS","Y","A"}
        kw = [w for w in key.split() if w not in STOPWORDS and len(w) > 2]
        burger_words = [w for w in kw if w not in ("AROS","PAPAS","CEBOLLA","VASO","COLECCIONABLE")]
        agg = {"u": 0, "imp": 0, "branches": {}}
        for rk_key, rk_val in rk_upper.items():
            if "VASO" not in rk_key:
                continue
            if es_aros  and "AROS"  not in rk_key: continue
            if es_papas and "AROS"  in  rk_key:    continue
            if all(w in rk_key for w in burger_words):
                agg["u"]   += rk_val["u"]
                agg["imp"] += rk_val["imp"]
                for br, bv in rk_val["branches"].items():
                    if br in agg["branches"]:
                        agg["branches"][br]["u"]   += bv["u"]
                        agg["branches"][br]["imp"] += bv["imp"]
                    else:
                        agg["branches"][br] = dict(bv)
        return agg if agg["u"] > 0 else {}

    productos_new = [dict(p) for p in template.get("productos", [])]
    for prod in productos_new:
        hit = match_mundial(prod["nombre"])
        prod["total"]    = {"u": hit.get("u", 0), "imp": hit.get("imp", 0)}
        prod["branches"] = hit.get("branches", {})

    mund_new = {
        "rango":    fmt_rango(args.desde, args.hasta),
        "srlBr":    [b for _,_,b,g in BRANCHES if g=="SRL"],
        "frBr":     [b for _,_,b,g in BRANCHES if g=="Franquicias"],
        "productos": productos_new,
        "vasos":    sum(p["total"]["u"]   for p in productos_new),
        "totalImp": sum(p["total"]["imp"] for p in productos_new),
    }
    # Guardar por período, limpiar legacy plano
    master["mundiales"] = {k: v for k, v in mund_dict.items() if isinstance(v, dict) and "rango" in v and k != P}
    master["mundiales"][P] = mund_new
def _prev_snapshot(master, P, branch):
    """Devuelve el último valor validado de una sucursal para el período P, o None
    si no hay historial previo. Se usa tanto para SIN DATOS (falla de API) como
    para CUARENTENA (dato fresco que no pasa la auditoría de identidad)."""
    prev_tot = master.get("branch_tot", {}).get(P, {}).get(branch)
    prev_A   = master.get("analytics", {}).get(P, {}).get(branch)
    if prev_A is None or prev_tot is None:
        return None
    prev_R  = master.get("rankings", {}).get(P, {}).get(branch)
    prev_D  = master.get("descdet", {}).get(P, {}).get(branch)
    prev_sc = master.get("sc_comandas", {}).get(P, {}).get(branch)
    return {
        "A": dict(prev_A),
        "R": dict(prev_R) if prev_R else {"items": [], "gross": 0},
        "D": dict(prev_D) if prev_D else {},
        "tot": prev_tot,
        "sc": list(prev_sc) if prev_sc else [],
    }

# ===========================================================================
# MAIN
# ===========================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde",    default=DEF_DESDE)
    ap.add_argument("--hasta",    default=DEF_HASTA)
    ap.add_argument("--periodo",  default=DEF_PERIODO)
    ap.add_argument("--no-build", action="store_true")
    args = ap.parse_args()

    email, pw = load_env()
    master    = json.load(open(os.path.join(HERE,"master.json"), encoding="utf-8"))
    prodcat   = build_prodcat(master)
    P         = args.periodo

    # Tolerancia de la auditoría de identidad (gross vs. suma de ítems del ranking).
    # Por debajo de esto se acepta el dato fresco igual (ruido de redondeo entre
    # componentes que se redondean por separado). Por encima, la sucursal entra en
    # CUARENTENA esta corrida: no se confía en su dato fresco, se conserva el último
    # valor validado, y las demás sucursales siguen su curso normal (no todo-o-nada).
    IDENTITY_TOLERANCE_PCT = 0.15

    print(f"\n=== Ingesta {P}  ({args.desde} → {args.hasta})  ·  {len(BRANCHES)} sucursales ===")
    A_all={};R_all={};D_all={};tot={};py_all={};daily_all={};daily_desc_all={};daily_cupon_py_all={};sc_all={}
    daily_cuenta_all={}
    dup_cuenta_all={}
    sc_raw_cuenta_all={}
    all_ok = True
    fallback_branches = []    # sucursales que usaron valor previo por SIN DATOS esta corrida
    api_error_branches = []   # sucursales cuyo fallo fue error de red/API (no "sin ventas" legítimo)
    quarantined_now = {}      # branch -> dq, sucursales puestas en cuarentena ESTA corrida
    cleared_now = []          # branch, sucursales que estaban en cuarentena y ahora pasaron la auditoría
    data_quality = {}         # branch -> {gross, items_sum, gap, gap_pct, ok} — solo datos FRESCOS y aceptados
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    for cliente, suc, branch, grupo in BRANCHES:
        rows = api_call(API_URL, cliente, suc, args.desde, args.hasta, email, pw)
        if rows is None:
            api_error_branches.append(branch)

        # Auditoria 23/07/2026: corremos transform() antes de fetch_medios_pago
        # para poder pasarle el total real por comanda (comanda_tot) y que
        # cruce Medios de Pago contra la venta real (ver docstring de
        # fetch_medios_pago), en vez de adivinar duplicados por patron.
        transform_result = transform(rows, prodcat) if rows else None
        comanda_tot_this = transform_result[-1] if transform_result else None

        daily_cuenta_all[branch], dup_cuenta_all[branch], sc_raw_cuenta_all[branch] = fetch_medios_pago(
            cliente, suc, branch, grupo, args.desde, args.hasta, email, pw, comanda_tot=comanda_tot_this)

        if not rows:
            prev = _prev_snapshot(master, P, branch)
            if prev is not None:
                # Falla transitoria de API (Cloudflare/timeout/rate-limit): conservamos el
                # último valor real conocido en vez de pisarlo con cero. Antes esto NO pasaba
                # acá (sí pasaba en daily_data/weekly/monthly), y generaba números distintos
                # entre el KPI de Resumen/Ranking y el gráfico de Evolución diaria para el
                # mismo período.
                print(f"  ⚠ {branch:14} SIN DATOS esta corrida — se CONSERVA el valor previo "
                      f"(${prev['tot']:,.0f}) en vez de pisar con cero.")
                A_all[branch]=prev["A"]; R_all[branch]=prev["R"]; D_all[branch]=prev["D"]
                tot[branch]=prev["tot"]; sc_all[branch]=prev["sc"]
                daily_all[branch]={}; daily_desc_all[branch]={}; daily_cupon_py_all[branch]={}
                py_all[branch]={"agg":{},"dias":{}}  # ver limitación conocida en rebuild_peya (merge por branch)
                fallback_branches.append(branch)
            else:
                print(f"  ‼ {branch:14} SIN DATOS y sin historial previo — se registra en cero.")
                A_zero = {
                    "canal": {}, "turno": {}, "comprobante": {}, "comp_desc": {},
                    "descuentos": 0, "envios": {"u":0,"imp":0}, "servmesa": {"u":0,"imp":0},
                    "comandas": 0, "ticket": 0, "gross": 0,
                }
                R_zero = {"items": [], "gross": 0}
                A_all[branch]=A_zero; R_all[branch]=R_zero; D_all[branch]={}
                tot[branch]=0; py_all[branch]={"agg":{},"dias":{}}
                daily_all[branch]={}; sc_all[branch]=[]
                daily_desc_all[branch]={}
                daily_cupon_py_all[branch]={}
            continue

        A,R,D,g,py,daily,daily_desc,daily_cupon_py,sc,_comanda_tot_unused = transform_result
        ok_b, dq = audit(branch,A,R)
        all_ok &= ok_b

        if abs(dq["gap_pct"]) <= IDENTITY_TOLERANCE_PCT:
            # Dentro de tolerancia (o exacto): se acepta el dato fresco.
            A_all[branch]=A; R_all[branch]=R; D_all[branch]=D; tot[branch]=g; py_all[branch]=py
            daily_all[branch]=daily; daily_desc_all[branch]=daily_desc; sc_all[branch]=sc
            daily_cupon_py_all[branch]=daily_cupon_py
            data_quality[branch] = dq
            master.setdefault("branch_last_ok", {})[branch] = now_iso
            if branch in master.get("quarantine", {}).get(P, {}):
                cleared_now.append(branch)
        else:
            # CUARENTENA: el dato fresco no pasa la auditoría de identidad más allá de
            # lo tolerable. No se confía en él esta corrida — se conserva el último
            # valor validado (mismo criterio que SIN DATOS). A propósito NO se actualiza
            # branch_last_ok: si la cuarentena persiste, el aviso de "dato viejo" (que
            # mira branch_last_ok) se va a prender solo después de STALE_HOURS, como
            # forma de escalar una cuarentena larga sin necesitar un contador aparte.
            print(f"  🔍 {branch:14} EN REVISIÓN esta corrida — gap ${dq['gap']:,.0f} "
                  f"({dq['gap_pct']}%) supera la tolerancia ({IDENTITY_TOLERANCE_PCT}%). "
                  f"Se conserva el último valor validado.")
            prev = _prev_snapshot(master, P, branch)
            if prev is not None:
                A_all[branch]=prev["A"]; R_all[branch]=prev["R"]; D_all[branch]=prev["D"]
                tot[branch]=prev["tot"]; sc_all[branch]=prev["sc"]
            else:
                # Primera vez que se ve esta sucursal en el período y ya viene con
                # desvío: no hay nada validado a lo que volver — se guarda igual pero
                # marcada, para no perder la única data disponible.
                A_all[branch]=A; R_all[branch]=R; D_all[branch]=D; tot[branch]=g
            daily_all[branch]={}; daily_desc_all[branch]={}; daily_cupon_py_all[branch]={}
            py_all[branch]={"agg":{},"dias":{}}
            sc_all.setdefault(branch, [])
            quarantined_now[branch] = dq

    # --- actualizar el registro de cuarentena (solo sucursales tocadas esta corrida) ---
    quarantine_period = dict(master.get("quarantine", {}).get(P, {}))
    for b in cleared_now:
        quarantine_period.pop(b, None)
    for b, dq in quarantined_now.items():
        quarantine_period[b] = {"gap": dq["gap"], "gap_pct": dq["gap_pct"], "detectado": now_iso}
    master.setdefault("quarantine", {})[P] = quarantine_period

    if len(api_error_branches) == len(BRANCHES):
        sys.exit(f"\nERROR: las {len(BRANCHES)} sucursales fallaron por error de red/API en esta "
                 f"corrida (no es 'sin ventas', es que la API no respondió bien a ninguna). "
                 f"No se escribe master.json para no ocultar un problema real de credenciales o "
                 f"de disponibilidad de la API detrás de un 'éxito' con datos viejos.\n"
                 f"Sucursales afectadas: {', '.join(api_error_branches)}")

    if not any(v["gross"] > 0 for v in A_all.values()):
        print("\n  ‼ Ninguna sucursal devolvió datos con ventas. Se registran ceros.")

    # --- merge datos core ---
    for key in ("analytics","rankings","descdet","branch_tot","sc_comandas"):
        master.setdefault(key,{}).setdefault(P,{})
    for b in A_all:
        master["analytics"][P][b]  = A_all[b]
        master["rankings"][P][b]   = R_all[b]
        master["descdet"][P][b]    = D_all[b]
        master["branch_tot"][P][b] = tot[b]
        master["sc_comandas"][P][b] = sc_all.get(b, [])

    # groups: se calcula sobre el branch_tot YA MERGEADO (persistido), no solo
    # sobre lo tocado en esta corrida — así una sucursal con SIN DATOS no
    # desinfla el total de red aunque su valor anterior siga en branch_tot.
    bt_persist = master["branch_tot"][P]
    grp={"SRL":0,"Franquicias":0}
    for _,_,branch,grupo in BRANCHES:
        if branch in bt_persist: grp[grupo]+=bt_persist[branch]
    grp["Total"]=grp["SRL"]+grp["Franquicias"]
    master.setdefault("groups",{})[P]=grp

    # --- period_meta ---
    desde_d=args.desde.split("-")[2].lstrip("0")
    hasta_d=args.hasta.split("-")[2].lstrip("0")
    anio=args.desde.split("-")[0]; mes=args.desde.split("-")[1]
    label=(f"{P} {anio}" if desde_d=="1" and hasta_d in ("30","31","28","29")
           else f"{P} {anio} ({desde_d}–{hasta_d})")
    from datetime import date
    try: dias=(date.fromisoformat(args.hasta)-date.fromisoformat(args.desde)).days+1
    except: dias=None
    master.setdefault("period_meta",{})[P]={
        "label":label,"scope":f"{len(A_all)} sucursales",
        "branches":list(A_all.keys()),"dias":dias,
        "parcial":hasta_d not in ("30","31","28","29"),
        "sin_datos_ultima_corrida": fallback_branches,  # sucursales con fallo de API en esta corrida (valor previo conservado)
    }
    if P not in master.get("periods",[]):
        master.setdefault("periods",[]).append(P)

    # --- secciones de promos ---
    rebuild_peya(master, P, py_all, tot, daily_cupon_py_all, args)
    rebuild_especial2026(master, P, args)
    rebuild_mundiales(master, P, args)
    rebuild_weekly_monthly(master, daily_all, daily_desc_all, args)
    rebuild_medios_pago(master, P, daily_cuenta_all, dup_cuenta_all, sc_raw_cuenta_all)
    chequear_reconciliacion_medios_pago(master, P)

    # --- Sucursales con dato viejo (más de STALE_HOURS sin una corrida fresca ACEPTADA
    # —ni SIN DATOS ni CUARENTENA cuentan como fresca—), calculado sobre el estado YA
    # PERSISTIDO de branch_last_ok (no solo lo tocado hoy), para que el aviso sobreviva
    # aunque la sucursal problemática no aparezca en esta corrida.
    # El cron corre a las 8, 13 y 19 UTC: el bache MÁS LARGO entre corridas normales es
    # el nocturno, 19h -> 8h del día siguiente = 13h. El umbral tiene que ser mayor a
    # eso o el aviso se prende solo todas las noches sin que haya ningún problema real.
    STALE_HOURS = 15  # 13h de bache máximo normal + 2h de margen
    now = datetime.utcnow()
    data_quality_alert = {}
    for _, _, branch, _ in BRANCHES:
        last_ok_iso = master.get("branch_last_ok", {}).get(branch)
        if not last_ok_iso:
            continue
        try:
            last_ok = datetime.strptime(last_ok_iso, "%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            continue
        hrs = (now - last_ok).total_seconds() / 3600
        if hrs > STALE_HOURS:
            data_quality_alert[branch] = {"last_ok": last_ok_iso, "hours_stale": round(hrs, 1)}
    master["data_quality_alert"] = data_quality_alert
    master.setdefault("data_quality", {}).setdefault(P, {}).update(data_quality)


    # --- guardar ---
    import shutil
    try:
        shutil.copy(os.path.join(HERE,"master.json"), os.path.join(HERE,"master.json.bak"))
    except Exception as e:
        print(f"  ⚠ No se pudo crear master.json.bak (no es crítico, se sigue igual): {e}")
    json.dump(master, open(os.path.join(HERE,"master.json"),"w",encoding="utf-8"),
              ensure_ascii=False)

    print(f"\n  master.json actualizado · red ${grp['Total']:,.0f} "
          f"(SRL ${grp['SRL']:,.0f} · Franq ${grp['Franquicias']:,.0f})")
    print(f"  Secciones actualizadas: analytics · rankings · descdet · "
          f"peya · especial2026 · mundiales · weekly · monthly · medios_pago")
    if fallback_branches:
        print(f"  ⚠ ATENCIÓN: {len(fallback_branches)} sucursal(es) fallaron esta corrida y se "
              f"conservó su último valor conocido en vez de ponerlas en cero: "
              f"{', '.join(fallback_branches)}. Revisar si la falla persiste en la próxima corrida.")
    if api_error_branches:
        print(f"  ⚠ De esas, {len(api_error_branches)} fallaron por error de red/API real "
              f"(no por falta de ventas): {', '.join(api_error_branches)}.")
    if quarantined_now:
        detalle_q = ', '.join(f"{b} ({dq['gap_pct']}%)" for b, dq in quarantined_now.items())
        print(f"  🔍 ATENCIÓN: {len(quarantined_now)} sucursal(es) puestas EN REVISIÓN esta "
              f"corrida (dato fresco descartado, se conservó el último validado): {detalle_q}.")
    if cleared_now:
        print(f"  ✓ Salieron de revisión esta corrida: {', '.join(cleared_now)}.")
    if data_quality_alert:
        detalle_stale = ', '.join(f"{b} ({v['hours_stale']}h)" for b, v in data_quality_alert.items())
        print(f"  ⚠ ATENCIÓN: {len(data_quality_alert)} sucursal(es) sin corrida exitosa hace "
              f"más de {STALE_HOURS}h — se muestra aviso en el dashboard: {detalle_stale}.")

    if args.no_build:
        print("  (--no-build: index.html no regenerado)"); return

    print("  Generando index.html ...")
    r = subprocess.run([sys.executable, os.path.join(HERE,"build.py")], cwd=HERE)
    if r.returncode==0:
        print("  ✓ index.html listo. Subilo a Netlify.")
    else:
        sys.exit("  ERROR al correr build.py")
    if not all_ok:
        print("\n  ‼ Revisá las sucursales marcadas arriba antes de publicar.")

if __name__=="__main__":
    main()
