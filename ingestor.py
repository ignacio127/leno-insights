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
    p = os.path.join(HERE, "config.env")
    if not os.path.exists(p):
        sys.exit("ERROR: falta config.env")
    env = {}
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1); env[k.strip()] = v.strip()
    if not env.get("GESDATTA_EMAIL") or not env.get("GESDATTA_PASSWORD"):
        sys.exit("ERROR: completá GESDATTA_EMAIL y GESDATTA_PASSWORD en config.env")
    return env["GESDATTA_EMAIL"], env["GESDATTA_PASSWORD"]

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
    agg   = defaultdict(lambda: [0.0, 0.0])
    comandas = set(); gross = 0.0
    envu = envi = smu = smi = 0.0
    # PY tracking
    py_agg  = defaultdict(lambda: [0.0, 0.0, set()])  # nombre -> [u, imp, cmds]
    py_dias = defaultdict(lambda: [0.0, 0.0])          # fecha  -> [imp, u]

    for r in rows:
        a = (r.get("articulo_id") or "").strip()
        if not a or "PRUEBA" in a.upper(): continue
        v = num(r.get("total")); c = num(r.get("cantidad"))
        if v == 0: continue
        if v < 0:
            desc += v; descdet[a] += -v; continue
        gross += v
        cl = (r.get("tipo_delivery") or "").strip() or "Salón/Mostrador"
        canal[cl] += v
        turno[(r.get("turno_id") or "").strip() or "?"] += v
        ing = (r.get("ingreso") or "").strip()
        comp[ing.split()[0] if ing else "S/C"] += v
        cn = str(r.get("comprobante_numero") or "").strip()
        if cn: comandas.add(cn)
        agg[a][0] += c; agg[a][1] += v
        if ENVIO.search(a): envu += c; envi += v
        if SERVM.search(a): smu += c; smi += v
        # PY
        if cl == "PEDIDOS YA":
            fecha = (r.get("fecha") or "").strip()
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
        "descuentos":  round(desc),
        "envios":      {"u": int(envu), "imp": round(envi)},
        "servmesa":    {"u": int(smu),  "imp": round(smi)},
        "comandas": nc, "ticket": round(gross / nc) if nc else 0, "gross": round(gross),
    }
    py_data = {
        "agg":  {k: [v[0], v[1], list(v[2])] for k, v in py_agg.items()},
        "dias": {f: [round(x[0]), round(x[1])] for f, x in py_dias.items()},
    }
    return analytics, {"items": items, "gross": round(gross)}, \
           {k: round(x) for k, x in descdet.items()}, round(gross), py_data

# ===========================================================================
# AUDITORIA
# ===========================================================================
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
    master["especial2026"] = esp

# ===========================================================================
# REBUILD MUNDIALES
# ===========================================================================
def rebuild_mundiales(master, P, args):
    mund = master.get("mundiales", {})
    mund["rango"] = fmt_rango(args.desde, args.hasta)

    # Match por nombre uppercase
    rk_upper = defaultdict(lambda:{"u":0,"imp":0,"branches":{}})
    for br in master.get("rankings",{}).get(P,{}):
        for it in master["rankings"][P][br]["items"]:
            key = it["nombre"].upper()
            rk_upper[key]["u"]   += it["u"]
            rk_upper[key]["imp"] += it["imp"]
            rk_upper[key]["branches"][br]={"u":it["u"],"imp":it["imp"]}

    for prod in mund.get("productos",[]):
        key = prod["nombre"].upper()
        hit = rk_upper.get(key,{})
        prod["total"]    = {"u":hit.get("u",0),"imp":hit.get("imp",0)}
        prod["branches"] = hit.get("branches",{})

    mund["vasos"]    = sum(p["total"]["u"]   for p in mund.get("productos",[]))
    mund["totalImp"] = sum(p["total"]["imp"] for p in mund.get("productos",[]))
    master["mundiales"] = mund

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
    A_all={};R_all={};D_all={};tot={};py_all={}
    all_ok = True
    for cliente, suc, branch, grupo in BRANCHES:
        rows = api_call(cliente, suc, args.desde, args.hasta, email, pw)
        if not rows:
            print(f"  ‼ {branch:14} SIN DATOS — revisá cliente='{cliente}' o el rango.")
            all_ok=False; continue
        A,R,D,g,py = transform(rows, prodcat)
        A_all[branch]=A; R_all[branch]=R; D_all[branch]=D; tot[branch]=g; py_all[branch]=py
        all_ok &= audit(branch,A,R)

    if not A_all:
        sys.exit("\nERROR: ninguna sucursal devolvió datos. Abortado.")

    # --- merge datos core ---
    for key in ("analytics","rankings","descdet","branch_tot"):
        master.setdefault(key,{}).setdefault(P,{})
    for b in A_all:
        master["analytics"][P][b]  = A_all[b]
        master["rankings"][P][b]   = R_all[b]
        master["descdet"][P][b]    = D_all[b]
        master["branch_tot"][P][b] = tot[b]

    grp={"SRL":0,"Franquicias":0}
    for _,_,branch,grupo in BRANCHES:
        if branch in tot: grp[grupo]+=tot[branch]
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

    # --- guardar ---
    import shutil
    try: shutil.copy(os.path.join(HERE,"master.json"), os.path.join(HERE,"master.json.bak"))
    except: pass
    json.dump(master, open(os.path.join(HERE,"master.json"),"w",encoding="utf-8"),
              ensure_ascii=False)

    print(f"\n  master.json actualizado · red ${grp['Total']:,.0f} "
          f"(SRL ${grp['SRL']:,.0f} · Franq ${grp['Franquicias']:,.0f})")
    print(f"  Secciones actualizadas: analytics · rankings · descdet · "
          f"peya · especial2026 · mundiales")

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
