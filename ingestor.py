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

DEF_PERIODO, DEF_DESDE, DEF_HASTA = "Junio", "2026-06-01", "2026-06-30"

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
def api_call(cliente, suc, desde, hasta, email, pw, estado=""):
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
    req = urllib.request.Request(API_URL, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        bt = e.read().decode("utf-8", "ignore")[:300]
        hint = ""
        if e.code == 403 or "1010" in bt:
            hint = "\n  → Bloqueo Cloudflare. Corré desde la misma red donde funciona tu Power Query."
        sys.exit(f"ERROR HTTP {e.code} en {cliente}/{suc}: {bt}{hint}")
    except Exception as e:
        sys.exit(f"ERROR de red en {cliente}/{suc}: {e}")
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
    envu = envi = smu = smi = 0.0
    # PY tracking
    py_agg  = defaultdict(lambda: [0.0, 0.0, set()])  # nombre -> [u, imp, cmds]
    py_dias = defaultdict(lambda: [0.0, 0.0])          # fecha  -> [imp, u]
    # Diario por fecha (para weekly/monthly) — solo bruto, mismo criterio que branch_tot
    daily = defaultdict(float)  # date object -> gross
    # S/C drill-down: comandas sin comprobante con sus ítems
    sc_cmds = defaultdict(lambda: {"fecha": "", "turno": "", "canal": "", "importe": 0.0, "items": []})

    for r in rows:
        a = (r.get("articulo_id") or "").strip()
        if not a or "PRUEBA" in a.upper(): continue
        v = num(r.get("total")); c = num(r.get("cantidad"))
        if v == 0: continue
        if v < 0:
            ing_d = (r.get("ingreso") or "").strip()
            tipo_d = ing_d.split()[0] if ing_d else "S/C"
            comp_desc[tipo_d] += v  # negativo
            desc += v; descdet[a] += -v; continue
        gross += v
        cl = (r.get("tipo_delivery") or "").strip() or "Salón/Mostrador"
        canal[cl] += v
        turno[(r.get("turno_id") or "").strip() or "?"] += v
        ing = (r.get("ingreso") or "").strip()
        tipo_comp = ing.split()[0] if ing else "S/C"
        comp[tipo_comp] += v
        cn = str(r.get("comprobante_numero") or "").strip()
        if cn: comandas.add(cn)
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
        fecha_raw = (r.get("fecha") or "").strip()
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
        "canal":       {k: round(x, 2) for k, x in canal.items()},
        "turno":       {k: round(x, 2) for k, x in turno.items()},
        "comprobante": {k: round(x, 2) for k, x in comp.items()},
        "comp_desc":   {k: round(x, 2) for k, x in comp_desc.items()},
        "descuentos":  round(desc, 2),
        "envios":      {"u": int(envu), "imp": round(envi, 2)},
        "servmesa":    {"u": int(smu),  "imp": round(smi, 2)},
        "comandas": nc, "ticket": round(gross / nc, 2) if nc else 0, "gross": round(gross, 2),
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
           {k: round(x) for k, x in descdet.items()}, round(gross), py_data, daily, sc_list

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

def rebuild_weekly_monthly(master, daily_by_branch, args):
    """daily_by_branch: {branch: {date: gross}}. Recalcula semanas y meses
    que caen dentro del rango consultado; preserva todo lo anterior.
    Si una sucursal no respondió en esta corrida (SIN DATOS), su valor
    previo en esa semana/mes se mantiene en vez de pisarse con 0."""
    weeks  = defaultdict(lambda: defaultdict(float))   # semana_label -> {branch_key: imp}
    months = defaultdict(lambda: defaultdict(float))   # mes_nombre   -> {branch_key: imp}
    month_dias = defaultdict(set)                       # mes_nombre -> {fechas con datos}

    for branch, dailymap in daily_by_branch.items():
        key = WK_KEY.get(branch, branch)
        for d, imp in dailymap.items():
            wl, _ = _semana_label(d)
            weeks[wl][key] += imp
            mn = MESES_ES[d.month]
            months[mn][key] += imp
            month_dias[mn].add(d)

    SRL_KEYS = ("Aconquija", "Barrio Norte", "Tafi Viejo")
    FR_KEYS  = ("Independencia", "Barrio Sur", "Peron", "Flip")

    def _merge(existing, touched):
        """Parte del registro previo (si hay), pisa solo las sucursales
        tocadas en esta corrida, recalcula SRL/Franquicias/Total."""
        out = {k: v for k, v in (existing or {}).items()
               if k in SRL_KEYS or k in FR_KEYS}
        for k, v in touched.items():
            out[k] = round(v)
        srl = sum(out.get(k, 0) for k in SRL_KEYS)
        fr  = sum(out.get(k, 0) for k in FR_KEYS)
        out["SRL"] = round(srl); out["Franquicias"] = round(fr); out["Total"] = round(srl + fr)
        return out

    # --- merge semanal: pisa solo sucursales tocadas, preserva el resto ---
    existentes = {w["semana"]: i for i, w in enumerate(master.get("weekly", []))}
    weekly_list = list(master.get("weekly", []))
    for wl, d in weeks.items():
        idx = existentes.get(wl)
        prev = weekly_list[idx] if idx is not None else {}
        entry = {"semana": wl, **_merge(prev, d)}
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
        entry = _merge(prev, d)
        dias_con_datos = len(month_dias[mn])
        ndias_mes = calendar.monthrange(anio, mes_num[mn])[1]
        entry["_dias"] = dias_con_datos
        entry["_parcial"] = dias_con_datos < ndias_mes
        monthly[mn] = entry
    master["monthly"] = monthly
def audit(branch, A, R):
    g = A["gross"]
    ok = (round(sum(A["canal"].values())) == g and
          round(sum(A["turno"].values())) == g and
          round(sum(A["comprobante"].values())) == g and
          round(sum(i["imp"] for i in R["items"])) == g)
    flag = "OK " if ok else "‼ "
    fails = "" if ok else " | FALLA identidad"
    print(f"  {flag}{branch:14} gross ${g:>12,.0f} | desc ${abs(A['descuentos']):>10,.0f} | "
          f"comandas {A['comandas']:>4} | ticket ${A['ticket']:>7,.0f}{fails}")
    return ok

# ===========================================================================
# REBUILD PEYA
# ===========================================================================
def rebuild_peya(master, P, py_by_branch, tot_by_branch, args):
    peya     = master.get("peya", {})
    rango    = fmt_rango(args.desde, args.hasta)
    net_tot  = sum(tot_by_branch.values())

    br_out   = {}; dias_net = defaultdict(lambda:[0.0,0.0])
    dias_br  = {}
    cupon_by = {}; cupon_tot = 0

    for br, py in py_by_branch.items():
        br_imp=0; br_u=0; br_cmds=set()
        br_dias = defaultdict(lambda:[0.0,0.0])
        for nombre,(u,imp,cmds) in py["agg"].items():
            br_imp+=imp; br_u+=u; br_cmds.update(cmds)
        for fecha,(imp,u) in py["dias"].items():
            br_dias[fecha][0]+=imp; br_dias[fecha][1]+=u
            dias_net[fecha][0]+=imp; dias_net[fecha][1]+=u
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

    all_imp  = sum(x["bruto"] for x in br_out.values())
    all_ped  = len({c for py in py_by_branch.values()
                      for cmds in [v[2] for v in py["agg"].values()] for c in cmds})
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
    for pr in peya.get("promos",[]):
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

    peya.update({
        "rango": rango,
        "total": {"imp":round(net_imp),"bruto":round(all_imp),"desc":-round(cupon_tot),
                  "u":all_u,"pedidos":all_ped,
                  "ticket":round(net_imp/all_ped) if all_ped else 0},
        "participacion": round(net_imp/net_tot*100,1) if net_tot else 0,
        "netoRedJunio":  round(net_tot),
        "branches":      br_out,
        "dias":   [{"fecha":f,"imp":round(x[0]),"u":int(x[1])}
                   for f,x in sorted(dias_net.items())],
        "diasBr": dias_br,
        "promos": promos_new,
        "cat":    {c:v for c,v in cat_acc.items()},
        "catBr":  {br:dict(d) for br,d in cat_br_acc.items()},
        "cupones":{
            "total": round(cupon_tot),
            "byBr":  {br:v for br,v in cupon_by.items() if v>0},
            "pctSobrePeya": round(cupon_tot/all_imp*100,1) if all_imp else 0,
        },
        "srlBr":  [b for _,_,b,g in BRANCHES if g=="SRL"],
        "frBr":   [b for _,_,b,g in BRANCHES if g=="Franquicias"],
    })
    master["peya"] = peya

# ===========================================================================
# REBUILD ESPECIAL 2026
# ===========================================================================
def rebuild_especial2026(master, P, args):
    esp = master.get("especial2026", {})
    esp["rango"]   = fmt_rango(args.desde, args.hasta)
    esp["parcial"] = args.hasta.split("-")[2] not in ("30","31","28","29")

    rk_all = defaultdict(lambda:{"u":0,"imp":0,"branches":{}})
    for br in master.get("rankings",{}).get(P,{}):
        for it in master["rankings"][P][br]["items"]:
            rk_all[it["nombre"]]["u"]   += it["u"]
            rk_all[it["nombre"]]["imp"] += it["imp"]
            rk_all[it["nombre"]]["branches"][br]={"u":it["u"],"imp":it["imp"]}

    for prod in esp.get("productos",[]):
        hit = rk_all.get(prod["nombre"],{})
        prod["u"]        = hit.get("u",0)
        prod["imp"]      = hit.get("imp",0)
        prod["branches"] = hit.get("branches",{})

    esp["total"] = {
        "u":   sum(p["u"]   for p in esp.get("productos",[])),
        "imp": sum(p["imp"] for p in esp.get("productos",[])),
    }
    master.setdefault("especial2026", {})[P] = esp

# ===========================================================================
# REBUILD MUNDIALES
# ===========================================================================
def rebuild_mundiales(master, P, args):
    mund = master.get("mundiales", {})
    mund["rango"] = fmt_rango(args.desde, args.hasta)

    # Índice de rankings por nombre uppercase
    # Gesdatta escribe "ELEMENTAL" (SRL) y "ELEMMENTAL" (franquicias) según la sucursal —
    # se normaliza a una sola grafía para no perder unidades de ningún lado.
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
        """Busca solo items con VASO COLECCIONABLE (promo mundiales), por burger + side."""
        key = _norm(nombre.upper().strip())
        es_aros  = "AROS"  in key
        es_papas = "PAPAS" in key
        STOPWORDS = {"CON","DE","LA","EL","LOS","LAS","Y","A"}
        kw = [w for w in key.split() if w not in STOPWORDS and len(w) > 2]
        burger_words = [w for w in kw if w not in ("AROS","PAPAS","CEBOLLA","VASO","COLECCIONABLE")]
        agg = {"u": 0, "imp": 0, "branches": {}}
        for rk_key, rk_val in rk_upper.items():
            if "VASO" not in rk_key:          # solo items de la promo mundiales
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

    for prod in mund.get("productos", []):
        hit = match_mundial(prod["nombre"])
        prod["total"]    = {"u": hit.get("u", 0), "imp": hit.get("imp", 0)}
        prod["branches"] = hit.get("branches", {})

    mund["vasos"]    = sum(p["total"]["u"]   for p in mund.get("productos", []))
    mund["totalImp"] = sum(p["total"]["imp"] for p in mund.get("productos", []))
    master.setdefault("mundiales", {})[P] = mund

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

    print(f"\n=== Ingesta {P}  ({args.desde} → {args.hasta})  ·  {len(BRANCHES)} sucursales ===")
    A_all={};R_all={};D_all={};tot={};py_all={};daily_all={};sc_all={}
    all_ok = True
    for cliente, suc, branch, grupo in BRANCHES:
        rows = api_call(cliente, suc, args.desde, args.hasta, email, pw)
        if not rows:
            print(f"  ‼ {branch:14} SIN DATOS — revisá cliente='{cliente}' o el rango.")
            all_ok=False; continue
        A,R,D,g,py,daily,sc = transform(rows, prodcat)
        A_all[branch]=A; R_all[branch]=R; D_all[branch]=D; tot[branch]=g; py_all[branch]=py; daily_all[branch]=daily; sc_all[branch]=sc
        all_ok &= audit(branch,A,R)

    if not A_all:
        sys.exit("\nERROR: ninguna sucursal devolvió datos. Abortado.")

    # --- merge datos core ---
    for key in ("analytics","rankings","descdet","branch_tot","sc_comandas"):
        master.setdefault(key,{}).setdefault(P,{})
    for b in A_all:
        master["analytics"][P][b]  = A_all[b]
        master["rankings"][P][b]   = R_all[b]
        master["descdet"][P][b]    = D_all[b]
        master["branch_tot"][P][b] = round(tot[b], 2)
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
    }
    if P not in master.get("periods",[]):
        master.setdefault("periods",[]).append(P)

    # --- secciones de promos ---
    rebuild_peya(master, P, py_all, tot, args)
    rebuild_especial2026(master, P, args)
    rebuild_mundiales(master, P, args)
    rebuild_weekly_monthly(master, daily_all, args)

    # --- guardar ---
    import shutil
    try: shutil.copy(os.path.join(HERE,"master.json"), os.path.join(HERE,"master.json.bak"))
    except: pass
    json.dump(master, open(os.path.join(HERE,"master.json"),"w",encoding="utf-8"),
              ensure_ascii=False)

    print(f"\n  master.json actualizado · red ${grp['Total']:,.0f} "
          f"(SRL ${grp['SRL']:,.0f} · Franq ${grp['Franquicias']:,.0f})")
    print(f"  Secciones actualizadas: analytics · rankings · descdet · "
          f"peya · especial2026 · mundiales · weekly · monthly")

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
