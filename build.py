import json
master=open('master.json',encoding='utf-8').read()
img=open('img.json',encoding='utf-8').read()
HTML = r'''<!DOCTYPE html>
<html lang="es"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LENO Insights · Control de Gestión</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style id="tw">__TWCSS__</style>
<style>
:root{
 --red:#E2001A;--red2:#FA0050;
 --bg:#f3f4f8;--card:#ffffff;--line:#e9ebf1;--line2:#f2f3f7;
 --txt:#0f1117;--txt2:#3b414e;--mut:#6a7183;--mut2:#9aa1b2;
 --primary:#4f46e5;--peya:#FA0050;--ok:#059669;--bad:#e11d48;--warn:#d97706;
 --r:14px;--r-sm:10px;--r-lg:18px;
 --sh1:0 1px 2px rgba(16,24,40,.05);
 --sh2:0 1px 3px rgba(16,24,40,.06),0 10px 26px -10px rgba(16,24,40,.12);
 --sh3:0 18px 40px -12px rgba(16,24,40,.20);}
*{font-family:'Inter',ui-sans-serif,system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
body{background:var(--bg);color:var(--txt);background-image:radial-gradient(1100px 560px at 100% -6%,rgba(79,70,229,.045),transparent),radial-gradient(820px 460px at -6% 0,rgba(226,0,26,.035),transparent);background-attachment:fixed}
h1,h2,h3{letter-spacing:-.015em}
.tnum{font-variant-numeric:tabular-nums}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh1)}
.card.lift{transition:box-shadow .2s,transform .2s}
.card.lift:hover{box-shadow:var(--sh3);transform:translateY(-2px)}
.kpi{position:relative;overflow:hidden;box-shadow:var(--sh2);transition:box-shadow .2s,transform .2s}
.kpi:hover{transform:translateY(-2px);box-shadow:var(--sh3)}
.kpi::before{content:'';position:absolute;left:0;top:0;height:3px;width:100%;background:var(--acc,#E2001A)}
.kpi .kl{font-size:10.5px;font-weight:700;color:var(--mut);text-transform:uppercase;letter-spacing:.06em}
.kpi .kv{font-size:30px;font-weight:800;letter-spacing:-.025em;line-height:1.05;color:var(--txt);font-variant-numeric:tabular-nums}
::-webkit-scrollbar{width:9px;height:9px}::-webkit-scrollbar-thumb{background:#cfd4de;border-radius:8px}::-webkit-scrollbar-thumb:hover{background:#b9bfcb}::-webkit-scrollbar-track{background:transparent}
.navi{transition:.15s;border-left:3px solid transparent;color:#565b66;cursor:pointer;border-radius:0 8px 8px 0;margin-right:8px}
.navi:hover{background:#eef0f5;color:var(--txt)}
.navi.active{background:#fdeaec;border-left:3px solid var(--red);color:var(--red);font-weight:600}
.navi .nic{font-size:13.5px;width:18px;text-align:center;flex-shrink:0;filter:grayscale(.15)}
.navgrp{font-size:.58rem;letter-spacing:.13em;text-transform:uppercase;color:#a2a8b4;font-weight:800;padding:16px 20px 6px}
.sec{display:none}.sec.active{display:block;animation:f .3s ease}
@keyframes f{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:none}}
table{border-collapse:collapse;width:100%}
.tg{cursor:pointer;transition:.12s}
.badge{font-size:.62rem;padding:3px 9px;border-radius:99px;font-weight:700;letter-spacing:.02em;display:inline-flex;align-items:center;gap:3px;white-space:nowrap}
.click{cursor:pointer;transition:.12s}.click:hover{background:#f7f8fa}
.sel{font-size:.8rem;padding:.45rem .8rem;border-radius:.6rem;background:#fff;border:1px solid var(--line);color:var(--txt);font-weight:500;box-shadow:var(--sh1);cursor:pointer;transition:.15s}
.sel:hover{border-color:#d3d7e0}.sel:focus{outline:none;border-color:var(--primary);box-shadow:0 0 0 3px rgba(79,70,229,.16)}
.secttl{font-size:1.3rem;font-weight:800;letter-spacing:-.025em}
.hbtn{cursor:pointer;padding:.45rem .85rem;border-radius:.6rem;font-size:.75rem;font-weight:600;transition:.15s;background:#fff;border:1px solid var(--line);color:var(--txt2);box-shadow:var(--sh1)}
.hbtn:hover{background:#f7f8fa;border-color:#d3d7e0}
#modal{position:fixed;inset:0;background:rgba(16,20,28,.5);display:none;align-items:center;justify-content:center;z-index:50;padding:24px;backdrop-filter:blur(2px)}#modal.on{display:flex}
.pbtn{cursor:pointer;padding:.42rem .95rem;border-radius:.5rem;font-size:.8rem;font-weight:600;transition:.15s;color:#71757f}
.pbtn:hover{color:var(--txt)}
@media print{aside{display:none!important}header{position:static!important}.hbtn,#periodTabs,#periodHint{display:none!important}body{background:#fff;background-image:none}.card{box-shadow:none;break-inside:avoid}}

/* ===== RESPONSIVE MOBILE ===== */
#menuBtn{display:none;background:none;border:none;cursor:pointer;padding:6px;border-radius:8px;font-size:20px;line-height:1;color:var(--txt)}
#menuBtn:hover{background:#eef0f5}
#sideOverlay{display:none;position:fixed;inset:0;background:rgba(10,12,18,.45);z-index:39;backdrop-filter:blur(2px)}
#sideOverlay.on{display:block}

@media(max-width:768px){
  /* sidebar como drawer */
  aside{position:fixed!important;left:0;top:0;height:100dvh;z-index:40;transform:translateX(-100%);transition:transform .26s cubic-bezier(.4,0,.2,1);box-shadow:var(--sh3)}
  aside.open{transform:translateX(0)}
  /* main ocupa todo el ancho */
  main{width:100%}
  /* header compacto */
  header{padding:10px 14px!important}
  header h1.secttl{font-size:1rem!important}
  header p#secScope{font-size:.65rem!important}
  #periodChip{display:none}
  #hoy{display:none}
  .hbtn{padding:.35rem .6rem!important;font-size:.7rem!important}
  #menuBtn{display:inline-flex;align-items:center;justify-content:center}
  /* período */
  #periodTabs{flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch}
  .px-7{padding-left:14px!important;padding-right:14px!important}
  .p-7{padding:12px!important}
  .px-5{padding-left:12px!important;padding-right:12px!important}
  /* grids: 2 col en mobile */
  .grid-cols-4,.grid-cols-3{grid-template-columns:repeat(2,minmax(0,1fr))!important}
  .grid-cols-2{grid-template-columns:repeat(2,minmax(0,1fr))!important}
  /* KPI valor más chico */
  .kpi .kv{font-size:22px!important}
  .kpi .kl{font-size:9.5px!important}
  .kpi{padding:14px!important}
  /* banner hero: más bajo */
  .promoHero{height:110px!important}
  /* tablas: scroll horizontal */
  .tableWrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
  table{min-width:480px}
  /* charts: altura reducida */
  canvas{max-height:220px!important}
  /* section padding */
  .sec.active{padding-bottom:32px}
  /* ocultar columnas opcionales en tablas */
  .hide-mobile{display:none!important}
  /* selects y filtros: full width */
  .sel{width:100%;max-width:100%}
  /* footer */
  footer{padding:16px 14px!important;font-size:.62rem!important}
}
@media(max-width:480px){
  .kpi .kv{font-size:18px!important}
  .kpi{padding:11px!important}
  canvas{max-height:180px!important}
  .promoHero{height:90px!important}
}
</style></head>
<body class="min-h-screen">
<div id="sideOverlay" onclick="closeSidebar()"></div>
<div class="flex">
<aside id="sidebar" class="w-60 shrink-0 min-h-screen border-r sticky top-0 h-screen overflow-y-auto bg-white" style="border-color:var(--line)">
  <div class="p-5 flex items-center gap-3 border-b" style="border-color:var(--line)">
     <div class="w-14 h-14 rounded-xl bg-white border flex items-center justify-center overflow-hidden shrink-0" style="border-color:var(--line);box-shadow:var(--sh1)"><img id="logoLeno" class="w-12 h-12 object-contain"/></div>
     <div class="min-w-0"><div class="font-extrabold tracking-tight leading-none text-lg">LENO Insights</div><div class="text-[11px] mt-1" style="color:var(--mut)">Control de Gestión</div></div></div>
  <nav class="py-3 text-sm" id="nav"></nav>
  <div class="px-4 pb-4 pt-3 mt-1 border-t" style="border-color:var(--line)">
     <div class="text-[10px] font-semibold mb-2.5" style="color:var(--mut);text-transform:uppercase;letter-spacing:.09em">Fuente de datos</div>
     <div class="rounded-xl flex items-center justify-center" style="background:#fff;border:1px solid var(--line);box-shadow:0 1px 3px rgba(16,24,40,.06);padding:16px 12px">
       <img id="gesSide" style="height:22px" class="object-contain"/>
     </div></div>
</aside>
<main class="flex-1 min-w-0">
 <header class="px-7 py-4 flex items-center justify-between border-b sticky top-0 z-20" style="border-color:var(--line);background:rgba(244,245,248,.9);backdrop-filter:blur(8px)">
   <div class="flex items-center gap-3">
     <button id="menuBtn" onclick="toggleSidebar()" aria-label="Menú">☰</button>
     <div><h1 class="secttl" id="secTitle">Resumen</h1><p class="text-[12px]" id="secScope" style="color:var(--mut)"></p></div>
   </div>
   <div class="flex items-center gap-2"><span id="periodChip" class="text-xs px-3 py-2 rounded-lg font-semibold" style="background:#fdeaec;color:#E2001A"></span><button onclick="window.print()" class="hbtn">🖨 PDF</button><button onclick="exportCSV()" class="hbtn">⤓ CSV</button><span id="hoy" class="text-xs px-3 py-2 rounded-lg bg-white border" style="border-color:var(--line);color:var(--mut)"></span></div></header>
 <div class="px-7 pt-5 flex items-center gap-3 flex-wrap w-full" style="max-width:1500px;margin-left:auto;margin-right:auto">
   <span class="text-[12px] font-semibold" style="color:var(--mut)">PERÍODO:</span>
   <div id="periodTabs" class="flex gap-1 p-1 rounded-xl bg-white border" style="border-color:var(--line);box-shadow:var(--sh1)"></div>
   <span id="periodHint" class="text-[12px]" style="color:var(--mut)"></span>
 </div>
 <div class="p-7 pt-4 w-full" style="max-width:1500px;margin-left:auto;margin-right:auto" id="content"></div>
 <footer class="px-7 py-6 text-center text-[11px] flex items-center justify-center gap-2 flex-wrap" style="color:var(--mut)"><span>LENO Insights · vía API</span><img id="gesFoot" class="h-3.5 inline"/></footer>
</main></div>
<div id="modal" onclick="if(event.target.id==='modal')closeModal()"><div class="card p-6 w-full max-w-2xl max-h-[85vh] overflow-y-auto" id="modalBox"></div></div>
<script>
// ── Responsive sidebar drawer ──────────────────────────────────────────────
function toggleSidebar(){
  const s=document.getElementById('sidebar'),o=document.getElementById('sideOverlay');
  const open=s.classList.toggle('open');
  o.classList.toggle('on',open);
  document.body.style.overflow=open?'hidden':'';
}
function closeSidebar(){
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sideOverlay').classList.remove('on');
  document.body.style.overflow='';
}
const DATA=__MASTER__;const IMG=__IMG__;
document.getElementById('logoLeno').src=IMG.leno;document.getElementById('gesSide').src=IMG.gesdatta;document.getElementById('gesFoot').src=IMG.gesdatta;
document.getElementById('hoy').textContent=new Date().toLocaleDateString('es-AR');
const F=n=>'$'+Math.round(n).toLocaleString('es-AR');
const Fm=n=>'$'+(n/1e6).toFixed(1)+'M';
const pct=(a,b)=>b?((a-b)/b*100):0;
const SRL=['Aconquija','Barrio Norte','Tafi Viejo'];
const BDKEY={'Aconquija':'Aconquija','Barrio Norte':'Barrio Norte','Tafi Viejo':'Tafi Viejo','Peron':'Peron','Independencia':'Independencia','Barrio Sur':'Barrio Sur','FLIP':'Flip'};
const PAL=['#E2001A','#2563eb','#f59e0b','#10b981','#8b5cf6','#ec4899','#0ea5e9','#f97316','#6366f1','#84cc16','#14b8a6'];
const MADRE_OVERRIDE={'X4 CHEESEBURGER CON PAPAS':'LENO BUCKETS CHEESEBURGER X4'};
const CROWN='<span title="Top 1">👑</span>';
let PERIOD='Mayo';let charts={};
function mkChart(id,cfg){if(charts[id])charts[id].destroy();const el=document.getElementById(id);if(el)charts[id]=new Chart(el,cfg);}
Chart.defaults.color='#71757f';Chart.defaults.font.family='Inter';Chart.defaults.borderColor='#e7e9ee';
const LINE='#e7e9ee';
function pbranches(){return DATA.period_meta[PERIOD].branches;}
function mergeDict(brs,field){const o={};brs.forEach(b=>{const a=DATA.analytics[PERIOD][b];if(a&&a[field])Object.entries(a[field]).forEach(([k,v])=>o[k]=(o[k]||0)+v);});return o;}
function sumNum(brs,field){let s=0;brs.forEach(b=>{const a=DATA.analytics[PERIOD][b];if(a)s+=a[field]||0;});return s;}
function sumSub(brs,field,sub){let s=0;brs.forEach(b=>{const a=DATA.analytics[PERIOD][b];if(a&&a[field])s+=a[field][sub]||0;});return s;}
function brOpts(cur){return '<option value="ALL">Todas</option>'+pbranches().map(b=>'<option value="'+b+'"'+(cur===b?' selected':'')+'>'+b+'</option>').join('');}
function selBrs(v){return (v==='ALL'||pbranches().indexOf(v)<0)?pbranches():[v];}

const SECTIONS=[['resumen','Resumen'],['semanal','Comparativa Semanal'],['mensual','Comparativa Mensual'],['ranking','Ranking de Productos'],['categorias','Categorías'],['fiscal','Facturación FAB/FAA/FAX'],['descuentos','Descuentos'],['turnos','Ventas por Turno'],['canales','Canales & Delivery'],['peya','Pedidos Ya - Campañas'],['envios','Envíos'],['mesa','Servicios de Mesa'],['especial2026','Especial 2026'],['burgerday','Burger Day'],['burgermes','Burger del Mes'],['mundiales','Nos Fuimos Mundiales']];
const NONPERIOD=['semanal','mensual'];
const GROUPS={resumen:'Panorama',ranking:'Comercial',canales:'Plataformas',especial2026:'Promociones'};
const SELFSCOPE={burgermes:{chip:DATA.burgermes.rango,scope:'Promo Burger del Mes · '+DATA.burgermes.rango+' · 7 sucursales'},mundiales:{chip:DATA.mundiales.rango,scope:'Promo Nos Fuimos Mundiales · '+DATA.mundiales.rango+' · 7 sucursales'},peya:{chip:DATA.peya.rango,scope:'PedidosYa Campañas · '+DATA.peya.rango+' · 7 sucursales'},especial2026:{chip:DATA.especial2026.rango,scope:'Promo Especial 2026 · '+DATA.especial2026.rango+' · en curso'}};
const nav=document.getElementById('nav');
const ICONS={resumen:'📊',semanal:'📈',mensual:'🗓️',ranking:'🏅',categorias:'🗂️',fiscal:'🧾',descuentos:'🏷️',turnos:'🕑',canales:'🛰️',peya:'🛵',envios:'📦',mesa:'🍽️',especial2026:'⭐',burgerday:'🎉',burgermes:'🍔',mundiales:'⚽'};
SECTIONS.forEach(([id,t])=>{if(GROUPS[id]){const g=document.createElement('div');g.className='navgrp';g.textContent=GROUPS[id];nav.appendChild(g);}const a=document.createElement('div');a.className='navi flex items-center gap-2 px-5 py-2.5';a.dataset.id=id;a.innerHTML='<span class="nic">'+(ICONS[id]||'•')+'</span><span>'+t+'</span>';a.onclick=()=>go(id);nav.appendChild(a);});
const content=document.getElementById('content');
SECTIONS.forEach(([id])=>{const d=document.createElement('section');d.className='sec';d.id='sec-'+id;content.appendChild(d);});
// period tabs
const ptabs=document.getElementById('periodTabs');
DATA.periods.forEach(p=>{const b=document.createElement('div');b.className='pbtn';b.dataset.p=p;b.textContent=DATA.period_meta[p].label;b.onclick=()=>setPeriod(p);ptabs.appendChild(b);});
function setPeriod(p){PERIOD=p;fTurno='ALL';fFisc='ALL';fDesc='ALL';fEnvios='ALL';fMesa='ALL';fCanal='ALL';rkScope='ALL';rkCat='ALL';
 document.querySelectorAll('#periodTabs .pbtn').forEach(b=>{const on=b.dataset.p===p;b.style.background=on?'#E2001A':'transparent';b.style.color=on?'#fff':'#71757f';});
 document.getElementById('periodHint').textContent=DATA.period_meta[p].parcial?'⚠ Datos parciales (en curso, se actualizan)':'Mes completo';
 const cur=[...document.querySelectorAll('.navi')].find(n=>n.classList.contains('active'));go(cur?cur.dataset.id:'resumen');}
let curSec='resumen';
function go(id){curSec=id;
 document.querySelectorAll('.navi').forEach(n=>n.classList.toggle('active',n.dataset.id===id));
 document.querySelectorAll('.sec').forEach(s=>s.classList.remove('active'));
 document.getElementById('sec-'+id).classList.add('active');
 document.getElementById('secTitle').textContent=SECTIONS.find(x=>x[0]===id)[1];
 document.getElementById('secScope').textContent=NONPERIOD.indexOf(id)>=0?'Histórico de cadena · Ene–May 2026 · todas las sucursales':(SELFSCOPE[id]?SELFSCOPE[id].scope:(DATA.period_meta[PERIOD].label+' · '+DATA.period_meta[PERIOD].scope));
 const chip=document.getElementById('periodChip');chip.textContent=NONPERIOD.indexOf(id)>=0?'Ene–May':(SELFSCOPE[id]?SELFSCOPE[id].chip:DATA.period_meta[PERIOD].label);
 if(RENDER[id])RENDER[id]();window.scrollTo(0,0);if(window.innerWidth<=768)closeSidebar();}
function kpi(label,val,sub,delta,color){let d='';if(delta!==undefined){const up=delta>=0;d='<span class="badge" style="background:'+(up?'#dcfce7':'#fee2e2')+';color:'+(up?'#16a34a':'#e11d48')+'">'+(up?'▲':'▼')+' '+Math.abs(delta).toFixed(1)+'%</span>';}
 return '<div class="card kpi p-5" style="--acc:'+(color||'#E2001A')+'"><div class="kl mb-2">'+label+'</div><div class="kv">'+val+'</div><div class="mt-2 flex items-center gap-2 text-[12px]" style="color:var(--mut)">'+d+'<span>'+(sub||'')+'</span></div></div>';}
function note(t){return '<div class="text-[12px] mt-3 px-4 py-2.5 rounded-lg flex gap-2" style="background:#fff7ed;border:1px solid #fed7aa;color:#9a3412">ℹ️ <span>'+t+'</span></div>';}
const histBanner='<div class="text-[12px] mb-4 px-4 py-2.5 rounded-lg flex gap-2" style="background:#eff6ff;border:1px solid #bfdbfe;color:#1e40af">📅 <span>Vista <b>histórica de cadena</b> (todas las sucursales, Ene–May). No cambia con el selector de período.</span></div>';
function insight(c,t,d){return '<div class="rounded-lg p-3" style="background:#fafbfc;border:1px solid var(--line);border-left:3px solid '+c+'"><div class="font-semibold mb-0.5">'+t+'</div><div style="color:var(--mut)">'+d+'</div></div>';}
function promoHero(img,name,sub,pos){return '<div class="promoHero mb-4" style="position:relative;height:144px;border-radius:1.1rem;overflow:hidden;border:1px solid var(--line)"><img src="'+img+'" style="width:100%;height:100%;object-fit:cover;object-position:'+(pos||'center 58%')+';display:block"/><div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(10,14,30,.82) 0%,rgba(10,14,30,.46) 55%,rgba(10,14,30,.12) 100%)"></div><div style="position:absolute;left:22px;bottom:18px;right:18px"><div style="color:#fff;font-size:22px;font-weight:800;letter-spacing:-.01em;text-shadow:0 2px 8px rgba(0,0,0,.45);line-height:1.1">'+name+'</div><div style="color:rgba(255,255,255,.92);font-size:13px;font-weight:600;margin-top:3px;text-shadow:0 1px 4px rgba(0,0,0,.5)">'+sub+'</div></div></div>';}
const RENDER={};

RENDER.resumen=()=>{
 const bt=DATA.branch_tot[PERIOD],g=DATA.groups[PERIOD],pm=DATA.period_meta[PERIOD];
 const ranked=pbranches().map(b=>({b,v:bt[b]})).sort((a,b)=>b.v-a.v);const maxb=ranked[0].v;
 const tks=pbranches().map(b=>DATA.analytics[PERIOD][b].ticket);const tkAvg=Math.round(tks.reduce((a,b)=>a+b,0)/tks.length);
 const topShare=ranked[0].v/g.Total*100;
 const turAll=mergeDict(pbranches(),'turno');const turTot=Object.values(turAll).reduce((a,b)=>a+b,0)||1;const noche=(turAll.Noche||0)/turTot*100;
 const canAll=mergeDict(pbranches(),'canal');const canTot=Object.values(canAll).reduce((a,b)=>a+b,0)||1;const peya=(canAll['PEDIDOS YA']||0)/canTot*100;
 const rr=pm.parcial?'<div class="text-[12px] mt-1" style="color:var(--mut)">Proyección a 30 días: <b>'+Fm(g.Total/pm.dias*30)+'</b></div>':'';
 const periodDesc=pbranches().reduce((s,b)=>s+Math.abs(DATA.analytics[PERIOD][b].descuentos),0);
 const neto=g.Total-periodDesc;const descPct=periodDesc/g.Total*100;
 let kpis=kpi('Facturación bruta',Fm(g.Total),pm.parcial?pm.dias+' días · '+pbranches().length+' suc.':'mes · '+pbranches().length+' suc.',undefined,'#E2001A')+
   kpi('Descuentos','−'+Fm(periodDesc),descPct.toFixed(1)+'% sobre bruto',undefined,'#e11d48')+
   kpi('Facturación NETA',Fm(neto),'bruto − descuentos',undefined,'#16a34a')+
   kpi('Ticket promedio',F(tkAvg),'por comanda',undefined,'#2563eb');
 const strip='<div class="card p-4 mt-4 flex flex-wrap items-center gap-x-8 gap-y-2 text-sm">'+
   '<div><span style="color:var(--mut)">Propias (SRL): </span><b>'+Fm(g.SRL)+'</b></div>'+
   (g.Franquicias>0?'<div><span style="color:var(--mut)">Franquicias: </span><b>'+Fm(g.Franquicias)+'</b></div>':'')+
   '<div class="flex items-center gap-2"><span style="color:var(--mut)">Resultado:</span> <b>'+Fm(g.Total)+'</b> <span style="color:#e11d48">− '+Fm(periodDesc)+'</span> <span style="color:var(--mut)">=</span> <b style="color:#16a34a">'+Fm(neto)+' neto</b></div></div>';
 const pidx=DATA.periods.indexOf(PERIOD);let cmp='';
 if(pidx>0){const prev=DATA.periods[pidx-1];
   const agg=per=>{const A=DATA.analytics[per];let gr=0,d=0,c=0;SRL.forEach(b=>{if(A[b]){gr+=A[b].gross;d+=Math.abs(A[b].descuentos);c+=A[b].comandas;}});const dd=DATA.period_meta[per].dias;return{brutoDia:gr/dd,netoDia:(gr-d)/dd,ticket:gr/Math.max(c,1),descPct:d/gr*100};};
   const cu=agg(PERIOD),pr=agg(prev);
   const row=(lbl,cv,pv,fmt,inv)=>{const dl=(cv/pv-1)*100,up=dl>=0,good=inv?!up:up;return '<tr style="border-top:1px solid var(--line)"><td class="py-2 pr-3">'+lbl+'</td><td class="py-2 px-3 text-right font-semibold">'+fmt(cv)+'</td><td class="py-2 px-3 text-right" style="color:var(--mut)">'+fmt(pv)+'</td><td class="py-2 px-3 text-right"><span class="badge" style="background:'+(good?'#dcfce7':'#fee2e2')+';color:'+(good?'#16a34a':'#e11d48')+'">'+(up?'▲':'▼')+' '+Math.abs(dl).toFixed(1)+'%</span></td></tr>';};
   cmp='<div class="card p-5 mt-4"><div class="font-semibold mb-1">📊 Comparación vs mes anterior · '+prev+'</div><div class="text-[12px] mb-3" style="color:var(--mut)">Base comparable: solo SRL (3 sucursales presentes en ambos períodos), normalizada por día.</div><div style="overflow-x:auto"><table class="text-sm w-full"><thead><tr class="text-[12px] text-left" style="color:var(--mut)"><th class="py-2 pr-3">Métrica (SRL)</th><th class="py-2 px-3 text-right">'+PERIOD+'</th><th class="py-2 px-3 text-right">'+prev+'</th><th class="py-2 px-3 text-right">Δ</th></tr></thead><tbody>'+
     row('Facturación bruta / día',cu.brutoDia,pr.brutoDia,Fm)+row('Facturación neta / día',cu.netoDia,pr.netoDia,Fm)+row('Ticket promedio',cu.ticket,pr.ticket,F)+row('Descuentos % s/ bruto',cu.descPct,pr.descPct,v=>v.toFixed(1)+'%',true)+
     '</tbody></table></div>'+note('La comparación aísla SRL y normaliza por día porque '+PERIOD+' es parcial/multi-sucursal y '+prev+' no. El total bruto de arriba sí incluye todas las sucursales del período.')+'</div>';}
 const el=document.getElementById('sec-resumen');
 el.innerHTML='<div class="grid grid-cols-1 md:grid-cols-4 gap-4">'+kpis+'</div>'+rr+strip+cmp+
  '<div class="card p-5 mt-4"><div class="font-semibold mb-3">🔔 Alertas & Insights</div><div class="grid md:grid-cols-2 gap-3 text-[13px]">'+
   insight('#E2001A','Concentración','<b>'+ranked[0].b+'</b> genera el <b>'+topShare.toFixed(0)+'%</b> del total del período. Punto único de falla: vigilar de cerca.')+
   insight('#8b5cf6','Dependencia horaria','La <b>Noche</b> concentra el <b>'+noche.toFixed(0)+'%</b> de la venta. Mediodía y After, subexplotados.')+
   insight('#FA0050','Delivery','PedidosYa = <b>'+peya.toFixed(0)+'%</b> del canal. Comisión de plataforma a contrastar contra LENO+.')+
   insight('#f59e0b','Margen','El panel mide facturación, no rentabilidad. Sin costos/comisiones no hay lectura de margen (mejora pendiente).')+
  '</div></div>'+
  '<div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-4"><div class="card p-5 lg:col-span-2"><div class="font-semibold mb-1">Evolución semanal · Total cadena (histórico)</div><div class="text-[12px] mb-3" style="color:var(--mut)">Ene–May 2026 · independiente del período seleccionado</div><canvas id="cRes" height="110"></canvas></div>'+
   '<div class="card p-5"><div class="font-semibold mb-3">Mix por sucursal</div><canvas id="cMix" height="190"></canvas></div></div>'+
  '<div class="card p-5 mt-4"><div class="font-semibold mb-1">Ranking de sucursales · '+pm.label+'</div><div class="text-[12px] mb-4" style="color:var(--mut)">Tocá una sucursal para ver su detalle</div>'+
   ranked.map((r,i)=>'<div class="click flex items-center gap-3 mb-2 p-1.5 rounded-lg" onclick="branchModal(\''+r.b+'\')"><span class="w-7 text-center font-bold">'+(i===0?CROWN:'<span style=\"color:var(--mut)\">'+(i+1)+'</span>')+'</span><span class="w-36 text-sm shrink-0">'+r.b+' '+(SRL.indexOf(r.b)>=0?'<span class=\"badge\" style=\"background:#dbeafe;color:#2563eb\">SRL</span>':'<span class=\"badge\" style=\"background:#fef3c7;color:#b45309\">FR</span>')+'</span><div class="flex-1 h-7 rounded-lg overflow-hidden" style="background:#f0f1f4"><div class="h-full flex items-center justify-end pr-2 text-[11px] font-bold text-white" style="width:'+(r.v/maxb*100)+'%;background:'+PAL[i%PAL.length]+'">'+Fm(r.v)+'</div></div></div>').join('')+'</div>';
 const wk=DATA.weekly;
 mkChart('cRes',{type:'line',data:{labels:wk.map(w=>w.semana.split(' al ')[0]),datasets:[{data:wk.map(w=>w.Total),borderColor:'#E2001A',backgroundColor:c=>{const x=c.chart.ctx.createLinearGradient(0,0,0,200);x.addColorStop(0,'rgba(226,0,26,.18)');x.addColorStop(1,'rgba(226,0,26,0)');return x;},fill:true,tension:.4,pointRadius:0,borderWidth:2.5}]},options:{interaction:{mode:'index',intersect:false},plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>'Total: '+F(c.raw)}}},scales:{y:{ticks:{callback:v=>'$'+(v/1e6).toFixed(0)+'M'},grid:{color:LINE}},x:{grid:{display:false}}}}});
 mkChart('cMix',{type:'doughnut',data:{labels:ranked.map(r=>r.b),datasets:[{data:ranked.map(r=>r.v),backgroundColor:ranked.map((r,i)=>PAL[i%PAL.length]),borderWidth:0}]},options:{cutout:'60%',plugins:{legend:{position:'bottom',labels:{padding:8,boxWidth:10,font:{size:10}}},tooltip:{callbacks:{label:c=>c.label+': '+Fm(c.raw)}}}}});
};

function branchModal(b){
 const rk=DATA.rankings[PERIOD][b];const items=(rk&&rk.items||[]).slice(0,8);const mx=items.length?items[0].imp:1;
 const a=DATA.analytics[PERIOD][b];
 let extra='<div class="grid grid-cols-3 gap-3 mt-4"><div class="rounded-lg p-3" style="background:#fafbfc;border:1px solid var(--line)"><div class="text-[11px]" style="color:var(--mut)">Ticket prom.</div><div class="text-xl font-bold">'+F(a.ticket)+'</div></div><div class="rounded-lg p-3" style="background:#fafbfc;border:1px solid var(--line)"><div class="text-[11px]" style="color:var(--mut)">Comandas</div><div class="text-xl font-bold">'+a.comandas.toLocaleString('es-AR')+'</div></div><div class="rounded-lg p-3" style="background:#fafbfc;border:1px solid var(--line)"><div class="text-[11px]" style="color:var(--mut)">Descuentos</div><div class="text-xl font-bold" style="color:#e11d48">'+Fm(Math.abs(a.descuentos))+'</div></div></div>';
 document.getElementById('modalBox').innerHTML='<div class="flex items-center justify-between mb-1"><div class="text-xl font-bold">'+b+'</div><button onclick="closeModal()" class="text-2xl leading-none" style="color:var(--mut)">×</button></div><div class="text-[13px] mb-4" style="color:var(--mut)">Facturación '+DATA.period_meta[PERIOD].label+': <b style="color:var(--txt)">'+F(DATA.branch_tot[PERIOD][b])+'</b></div><div class="font-semibold mb-2 text-sm">Top 8 productos</div>'+items.map((it,i)=>'<div class="flex items-center gap-3 mb-2"><span class="w-6 text-center">'+(i===0?CROWN:'<span style=\"color:var(--mut)\">'+(i+1)+'</span>')+'</span><span class="flex-1 text-sm">'+it.nombre+'</span><div class="w-28 h-4 rounded" style="background:#f0f1f4"><div class="h-full rounded" style="width:'+(it.imp/mx*100)+'%;background:'+PAL[i%PAL.length]+'"></div></div><span class="w-24 text-right text-sm font-semibold">'+F(it.imp)+'</span></div>').join('')+extra;
 document.getElementById('modal').classList.add('on');}
function closeModal(){document.getElementById('modal').classList.remove('on');}

RENDER.semanal=()=>{
 const wk=DATA.weekly;const el=document.getElementById('sec-semanal');
 const _b=histBanner;
 const cur=document.getElementById('selBr')?document.getElementById('selBr').value:'Total';
 const allbr=['Aconquija','Barrio Norte','Tafi Viejo','Peron','Independencia','Barrio Sur','FLIP'];
 el.innerHTML=_b+'<div class="card p-5"><div class="flex items-center justify-between flex-wrap gap-2 mb-1"><div class="font-semibold">Ventas semanales por sucursal</div><select id="selBr" onchange="RENDER.semanal()" class="sel"><option value="Total">Total cadena</option><option value="SRL">Solo SRL</option><option value="Franquicias">Solo Franquicias</option>'+allbr.map(b=>'<option value="'+BDKEY[b]+'">'+b+'</option>').join('')+'</select></div><div class="text-[12px] mb-3" style="color:var(--mut)">Histórico Ene–May (VTAS_SEMANALES, cadena completa). Pasá el cursor para ver el total de cada semana.</div><canvas id="cWk" height="90"></canvas></div>'+
  '<div class="card p-5 mt-4 overflow-x-auto"><div class="font-semibold mb-3">Detalle semanal</div><table class="text-sm"><thead><tr class="text-left text-[12px]" style="color:var(--mut)"><th class="py-2 pr-3">Semana</th>'+allbr.map(b=>'<th class="py-2 px-3 text-right">'+b.split(' ')[0]+'</th>').join('')+'<th class="py-2 pl-3 text-right" style="color:var(--red)">Total</th></tr></thead><tbody>'+wk.map(w=>'<tr style="border-top:1px solid var(--line)"><td class="py-2 pr-3 whitespace-nowrap">'+w.semana+'</td>'+allbr.map(b=>'<td class="py-2 px-3 text-right" style="color:var(--mut)">'+Fm(w[BDKEY[b]])+'</td>').join('')+'<td class="py-2 pl-3 text-right font-semibold" style="color:var(--red)">'+Fm(w.Total)+'</td></tr>').join('')+'</tbody></table></div>';
 document.getElementById('selBr').value=cur;
 mkChart('cWk',{type:'line',data:{labels:wk.map(w=>w.semana.split(' al ')[0]),datasets:[{label:cur,data:wk.map(w=>w[cur]),borderColor:'#2563eb',backgroundColor:c=>{const x=c.chart.ctx.createLinearGradient(0,0,0,220);x.addColorStop(0,'rgba(37,99,235,.20)');x.addColorStop(1,'rgba(37,99,235,0)');return x;},fill:true,tension:.4,pointRadius:0,pointHoverRadius:5,borderWidth:2.5}]},options:{interaction:{mode:'index',intersect:false},plugins:{legend:{display:false},tooltip:{callbacks:{title:it=>'Semana '+it[0].label,label:c=>'Total '+cur+': '+F(c.raw)}}},scales:{y:{ticks:{callback:v=>'$'+(v/1e6).toFixed(0)+'M'},grid:{color:LINE}},x:{grid:{display:false}}}}});
};

const MSRL=['Aconquija','Barrio Norte','Tafi Viejo'];const MFR=['Peron','Independencia','Barrio Sur','Flip'];
let mView='grupos';
RENDER.mensual=()=>{
 const mo=DATA.monthly,ms=['Enero','Febrero','Marzo','Abril','Mayo'];const el=document.getElementById('sec-mensual');
 const rows=ms.map((m,i)=>({m,v:mo[m].Total,p:i>0?pct(mo[m].Total,mo[ms[i-1]].Total):null}));
 const jun=DATA.groups.Junio,jd=DATA.period_meta.Junio.dias,rr=jun.Total/jd*30;
 let dist='';
 if(mView==='grupos')dist='<div class="grid md:grid-cols-2 gap-6"><div><div class="text-sm font-semibold mb-2" style="color:#2563eb">● LENO SRL por sucursal</div><canvas id="cSRL" height="160"></canvas></div><div><div class="text-sm font-semibold mb-2" style="color:#f59e0b">● Franquicias por sucursal</div><canvas id="cFR" height="160"></canvas></div></div>';
 else if(mView==='SRL')dist='<canvas id="cSRL" height="120"></canvas>';
 else if(mView==='FRANQ')dist='<canvas id="cFR" height="120"></canvas>';
 else dist='<canvas id="cBR" height="120"></canvas>';
 const opts=[['grupos','SRL + Franquicias (lado a lado)'],['SRL','Solo LENO SRL'],['FRANQ','Solo Franquicias']].concat(MSRL.concat(MFR).map(b=>[b,b]));
 el.innerHTML=histBanner+'<div class="grid grid-cols-1 lg:grid-cols-3 gap-4"><div class="card p-5 lg:col-span-2"><div class="font-semibold mb-3">Facturación mensual · cadena (histórico BD)</div><canvas id="cMo" height="120"></canvas></div>'+
  '<div class="card p-5"><div class="font-semibold mb-2">Junio en curso</div><div class="text-[12px] mb-3" style="color:var(--mut)">7 sucursales · 1–5 jun (comanda)</div><div class="text-3xl font-bold">'+Fm(jun.Total)+'</div><div class="text-[12px] mt-1" style="color:var(--mut)">en 5 días</div><div class="mt-3 rounded-lg p-3" style="background:#fafbfc;border:1px solid var(--line)"><div class="text-[11px]" style="color:var(--mut)">Proyección run-rate 30 días</div><div class="text-xl font-bold" style="color:#E2001A">'+Fm(rr)+'</div></div>'+
  '<div class="grid grid-cols-1 gap-2 mt-3 text-[12px]"><div class="flex justify-between"><span style="color:var(--mut)">SRL</span><b>'+Fm(jun.SRL)+'</b></div><div class="flex justify-between"><span style="color:var(--mut)">Franquicias</span><b>'+Fm(jun.Franquicias)+'</b></div></div></div></div>'+
  '<div class="card p-5 mt-4"><div class="flex items-center justify-between flex-wrap gap-2 mb-3"><div class="font-semibold">Distribución por grupo y sucursal</div><select class="sel" onchange="mView=this.value;RENDER.mensual()">'+opts.map(o=>'<option value="'+o[0]+'"'+(mView===o[0]?' selected':'')+'>'+o[1]+'</option>').join('')+'</select></div><div class="text-[12px] mb-4" style="color:var(--mut)">Barras apiladas por sucursal · tocá una sucursal en la leyenda para aislarla. Histórico Ene–May.</div>'+dist+'</div>'+
  '<div class="card p-5 mt-4"><div class="font-semibold mb-3">Variación intermensual (cadena)</div>'+rows.map(r=>'<div class="flex items-center justify-between py-2.5" style="border-bottom:1px solid var(--line)"><span>'+r.m+'</span><span class="font-semibold">'+Fm(r.v)+'</span>'+(r.p===null?'<span class="text-[11px]" style="color:var(--mut)">—</span>':'<span class="badge" style="background:'+(r.p>=0?'#dcfce7':'#fee2e2')+';color:'+(r.p>=0?'#16a34a':'#e11d48')+'">'+(r.p>=0?'▲':'▼')+' '+Math.abs(r.p).toFixed(1)+'%</span>')+'</div>').join('')+'</div>'+
  note('<b>Anti-inflación:</b> cifras nominales (precio + volumen mezclados). El bloque mensual (Ene–May) viene de VTAS_SEMANALES (cadena). “Junio en curso” viene de comanda Gesdatta (otra fuente) y es parcial: no es comparable cabeza a cabeza con los meses cerrados, por eso va aparte.');
 mkChart('cMo',{type:'bar',data:{labels:ms,datasets:[{data:ms.map(m=>mo[m].Total),backgroundColor:ms.map((m,i)=>PAL[i%PAL.length]),borderRadius:8}]},options:{plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>Fm(c.raw)}}},scales:{y:{ticks:{callback:v=>'$'+(v/1e6).toFixed(0)+'M'},grid:{color:LINE}},x:{grid:{display:false}}}}});
 const mds=(brs,off)=>brs.map((b,i)=>({label:b,data:ms.map(m=>mo[m][b]||0),backgroundColor:PAL[((off||0)+i)%PAL.length],borderRadius:4,stack:'s'}));
 const stacked=(brs,off)=>({type:'bar',data:{labels:ms,datasets:mds(brs,off)},options:{plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:8,font:{size:10}}},tooltip:{callbacks:{label:c=>c.dataset.label+': '+Fm(c.raw)}}},scales:{x:{stacked:true,grid:{display:false}},y:{stacked:true,ticks:{callback:v=>'$'+(v/1e6).toFixed(0)+'M'},grid:{color:LINE}}}}});
 if(mView==='grupos'){mkChart('cSRL',stacked(MSRL,1));mkChart('cFR',stacked(MFR,2));}
 else if(mView==='SRL')mkChart('cSRL',stacked(MSRL,1));
 else if(mView==='FRANQ')mkChart('cFR',stacked(MFR,2));
 else mkChart('cBR',{type:'bar',data:{labels:ms,datasets:[{label:mView,data:ms.map(m=>mo[m][mView]||0),backgroundColor:'#E2001A',borderRadius:6}]},options:{plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>Fm(c.raw)+' · '+(c.raw/(mo[ms[c.dataIndex]].Total||1)*100).toFixed(1)+'% de la cadena'}}},scales:{y:{ticks:{callback:v=>'$'+(v/1e6).toFixed(0)+'M'},grid:{color:LINE}},x:{grid:{display:false}}}}});
};

let rkView='A',rkScope='ALL',rkCat='ALL',rkSort='imp',rkCompare=false;
function srlUnitsMap(period,view){const m={};SRL.forEach(b=>{const items=(DATA.rankings[period][b]&&DATA.rankings[period][b].items)||[];items.forEach(it=>{const key=view==='A'?it.nombre:(MADRE_OVERRIDE[it.madre]||MADRE_OVERRIDE[it.nombre]||it.madre);m[key]=(m[key]||0)+it.u;});});return m;}
function rankData(){
 let brs=rkScope==='ALL'?pbranches():rkScope==='SRL'?pbranches().filter(b=>SRL.indexOf(b)>=0):rkScope==='FRANQ'?pbranches().filter(b=>SRL.indexOf(b)<0):[rkScope];
 const agg={};
 brs.forEach(b=>{const items=(DATA.rankings[PERIOD][b]&&DATA.rankings[PERIOD][b].items)||[];
   items.forEach(it=>{let key=it.nombre;if(rkView==='B'){key=MADRE_OVERRIDE[it.madre]||MADRE_OVERRIDE[it.nombre]||it.madre;}
     if(!agg[key])agg[key]={nombre:key,u:0,imp:0,cat:it.cat,promo:it.promo};
     agg[key].u+=it.u;agg[key].imp+=it.imp;if(rkView==='A'&&it.promo)agg[key].promo=true;});});
 let arr=Object.values(agg);if(rkCat!=='ALL')arr=arr.filter(x=>x.cat===rkCat);
 arr.sort((a,b)=>rkSort==='imp'?b.imp-a.imp:b.u-a.u);return arr;}
function rankRecos(){
 const all=(function(){const s=rkScope,c=rkCat;rkScope='ALL';rkCat='ALL';const v=rkView;rkView='A';const a=rankData();rkView=v;rkScope=s;rkCat=c;return a;})();
 const tot=all.reduce((s,x)=>s+x.imp,0)||1;
 const promoShare=all.filter(x=>x.promo).reduce((s,x)=>s+x.imp,0)/tot*100;
 const top=all[0];const top3=all.slice(0,3).reduce((s,x)=>s+x.imp,0)/tot*100;
 const tail=all.filter(x=>x.imp/tot<0.005).length;
 const catTot={};all.forEach(x=>catTot[x.cat]=(catTot[x.cat]||0)+x.imp);const catTop=Object.entries(catTot).sort((a,b)=>b[1]-a[1])[0];
 const pm=DATA.period_meta[PERIOD];
 let r=[];
 r.push(insight('#E2001A','Producto estrella','<b>'+top.nombre+'</b> lidera con '+F(top.imp)+' ('+(top.imp/tot*100).toFixed(1)+'% del total). El top 3 concentra el '+top3.toFixed(0)+'%.'));
 r.push(insight('#FA0050','Dependencia de promos','El '+promoShare.toFixed(0)+'% de la venta viene de artículos en promo/campaña. '+(promoShare>30?'Alta: cuidado con erosión de margen al sostenerlas.':'Saludable, las promos no canibalizan el menú base.')));
 r.push(insight('#f59e0b','Cola larga','Hay <b>'+tail+'</b> productos con menos de 0,5% de participación. Candidatos a revisar carta/simplificar cocina.'));
 r.push(insight('#10b981','Categoría líder','<b>'+catTop[0]+'</b> manda con '+(catTop[1]/tot*100).toFixed(0)+'% de la facturación.'+(pm.parcial?' (muestra de 5 días)':'')));
 return '<div class="grid md:grid-cols-2 gap-3 text-[13px]">'+r.join('')+'</div>';
}
RENDER.ranking=()=>{
 const cats=[...new Set(Object.values(DATA.rankings[PERIOD]).flatMap(r=>r.items.map(i=>i.cat)))].filter(c=>c!=='Envíos'&&c!=='Servicio de Mesa').sort();
 const el=document.getElementById('sec-ranking');
 const tgcss=on=>on?'background:#E2001A;color:#fff':'';
 el.innerHTML='<div class="card p-5 mb-4"><div class="font-semibold mb-3">💡 Recomendaciones & novedades</div>'+rankRecos()+'</div>'+
  '<div class="card p-5"><div class="flex flex-wrap items-center gap-3 mb-4"><div class="flex rounded-lg overflow-hidden text-xs border" style="border-color:var(--line)"><div class="tg px-3 py-1.5" style="'+tgcss(rkView==='A')+'" onclick="rkView=\'A\';RENDER.ranking()">Artículos</div><div class="tg px-3 py-1.5" style="'+tgcss(rkView==='B')+'" onclick="rkView=\'B\';RENDER.ranking()">Consolidado (madre)</div></div>'+
   '<select onchange="rkScope=this.value;RENDER.ranking()" class="sel"><option value="ALL">Todas</option><option value="SRL"'+(rkScope==='SRL'?' selected':'')+'>Propias (SRL)</option><option value="FRANQ"'+(rkScope==='FRANQ'?' selected':'')+'>Franquicias</option>'+pbranches().map(b=>'<option value="'+b+'"'+(rkScope===b?' selected':'')+'>'+b+'</option>').join('')+'</select>'+
   '<select onchange="rkCat=this.value;RENDER.ranking()" class="sel"><option value="ALL">Todas las categorías</option>'+cats.map(c=>'<option value="'+c+'"'+(rkCat===c?' selected':'')+'>'+c+'</option>').join('')+'</select>'+
   '<div class="tg px-3 py-1.5 rounded-lg text-xs border" style="border-color:var(--line);'+(rkCompare?'background:#16a34a;color:#fff':'')+'" onclick="rkCompare=!rkCompare;RENDER.ranking()">↔ vs mes ant.</div>'+
   '<div class="flex rounded-lg overflow-hidden text-xs border ml-auto" style="border-color:var(--line)"><div class="tg px-3 py-1.5" style="'+tgcss(rkSort==='imp')+'" onclick="rkSort=\'imp\';RENDER.ranking()">$ Facturación</div><div class="tg px-3 py-1.5" style="'+tgcss(rkSort==='u')+'" onclick="rkSort=\'u\';RENDER.ranking()">Unidades</div></div></div><div id="rkBody"></div>'+
   note('SRL: nivel comanda. Franquicias (solo Junio): comanda. Se excluyen modificadores, packaging, comps $0, “PRUEBA” y personal. <b>Consolidado</b> suma promos y junta “X4 Cheeseburger” en “Leno Buckets Cheeseburger X4”.')+'</div>';
 paintRk();};
function paintRk(){const arr=rankData();const tot=arr.reduce((s,x)=>s+x.imp,0)||1;const mx=Math.max.apply(null,arr.map(x=>rkSort==='imp'?x.imp:x.u).concat([1]));
 const _pi=DATA.periods.indexOf(PERIOD);const other=_pi>0?DATA.periods[_pi-1]:null;
 const canCmp=rkCompare&&!!other;
 const curMap=canCmp?srlUnitsMap(PERIOD,rkView):{};const othMap=canCmp?srlUnitsMap(other,rkView):{};
 const curD=DATA.period_meta[PERIOD].dias,othD=other?DATA.period_meta[other].dias:1;
 function cmpCell(name){if(!canCmp)return '';
   const cu=curMap[name]||0,ou=othMap[name]||0;
   if(ou===0&&cu>0)return '<td class="py-2.5 px-3 text-right"><span class="badge" style="background:#dbeafe;color:#2563eb">nuevo</span></td>';
   if(cu===0)return '<td class="py-2.5 px-3 text-right" style="color:var(--mut)">—</td>';
   const v=pct(cu/curD,ou/othD),up=v>=0;
   return '<td class="py-2.5 px-3 text-right" title="'+name+': '+PERIOD+' '+cu+'u en '+curD+'d vs '+other+' '+ou+'u en '+othD+'d"><span class="badge" style="background:'+(up?'#dcfce7':'#fee2e2')+';color:'+(up?'#16a34a':'#e11d48')+'">'+(up?'▲':'▼')+' '+Math.abs(v).toFixed(0)+'%</span></td>';}
 const cmpHead=canCmp?'<th class="py-2 px-3 text-right">vs '+DATA.period_meta[other].label+'<br><span style="font-weight:400;font-size:10px">SRL · por día</span></th>':'';
 const cmpNote=!rkCompare?'':(other?'<div class="text-[12px] mb-3 px-3 py-2 rounded-lg" style="background:#ecfdf5;border:1px solid #a7f3d0;color:#065f46">↔ Variación de <b>unidades por día</b> contra <b>'+DATA.period_meta[other].label+'</b>, calculada solo sobre <b>SRL</b> (sucursales presentes en ambos meses) y normalizada por días ('+PERIOD+': '+curD+'d vs '+other+': '+othD+'d).</div>':'<div class="text-[12px] mb-3 px-3 py-2 rounded-lg" style="background:#fef9c3;border:1px solid #fde047;color:#854d0e">↔ '+DATA.period_meta[PERIOD].label+' es el primer mes cargado: no hay mes anterior para comparar.</div>');
 document.getElementById('rkBody').innerHTML=cmpNote+'<table class="text-sm"><thead><tr class="text-[12px] text-left" style="color:var(--mut)"><th class="py-2 pr-2 w-8">#</th><th class="py-2 pr-3">Producto</th><th class="py-2 px-3">Categoría</th><th class="py-2 px-3 text-right">Unidades</th><th class="py-2 px-3 text-right">Facturación</th><th class="py-2 px-3 text-right">%</th>'+cmpHead+'</tr></thead><tbody>'+arr.slice(0,60).map((x,i)=>'<tr style="border-top:1px solid var(--line)"><td class="py-2.5 pr-2 font-bold">'+(i===0?CROWN:'<span style=\"color:var(--mut)\">'+(i+1)+'</span>')+'</td><td class="py-2.5 pr-3"><div class="flex items-center gap-2"><span>'+x.nombre+'</span>'+(x.promo&&rkView==='A'?'<span class="badge" style="background:#ffe4ec;color:#FA0050">PROMO</span>':'')+'</div><div class="h-1.5 mt-1.5 rounded-full" style="background:#f0f1f4"><div class="h-full rounded-full" style="width:'+((rkSort==='imp'?x.imp:x.u)/mx*100)+'%;background:'+PAL[i%PAL.length]+'"></div></div></td><td class="py-2.5 px-3 text-[12px]" style="color:var(--mut)">'+x.cat+'</td><td class="py-2.5 px-3 text-right">'+x.u.toLocaleString('es-AR')+'</td><td class="py-2.5 px-3 text-right font-semibold">'+F(x.imp)+'</td><td class="py-2.5 px-3 text-right" style="color:var(--mut)">'+(x.imp/tot*100).toFixed(1)+'%</td>'+cmpCell(x.nombre)+'</tr>').join('')+'</tbody></table>'+(arr.length>60?'<div class="text-[12px] mt-3" style="color:var(--mut)">Top 60 de '+arr.length+'.</div>':'');}

let catSort='imp';
RENDER.categorias=()=>{const c=DATA.cat[PERIOD];const arr=Object.entries(c).filter(([k])=>k!=='Envíos'&&k!=='Servicio de Mesa').map(([k,v])=>({k,imp:v.imp,u:v.u}));
 arr.sort((a,b)=>catSort==='imp'?b.imp-a.imp:b.u-a.u);
 const totI=arr.reduce((s,x)=>s+x.imp,0),totU=arr.reduce((s,x)=>s+x.u,0);const mx=catSort==='imp'?arr[0].imp:arr[0].u;
 const el=document.getElementById('sec-categorias');const tgcss=on=>on?'background:#E2001A;color:#fff':'';
 el.innerHTML='<div class="card p-5"><div class="flex items-center justify-between flex-wrap gap-2 mb-1"><div class="font-semibold">Participación por categoría · '+DATA.period_meta[PERIOD].label+'</div><div class="flex rounded-lg overflow-hidden text-xs border" style="border-color:var(--line)"><div class="tg px-3 py-1.5" style="'+tgcss(catSort==='imp')+'" onclick="catSort=\'imp\';RENDER.categorias()">$ Facturación</div><div class="tg px-3 py-1.5" style="'+tgcss(catSort==='u')+'" onclick="catSort=\'u\';RENDER.categorias()">Unidades</div></div></div><div class="text-[12px] mb-4" style="color:var(--mut)">Tocá una categoría para verla en el ranking · se muestran $ y unidades</div>'+
  arr.map((x,i)=>'<div class="click mb-3 p-1.5 rounded-lg" onclick="rkCat=\''+x.k+'\';rkScope=\'ALL\';go(\'ranking\')"><div class="flex justify-between text-sm mb-1"><span class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-full" style="background:'+PAL[i%PAL.length]+'"></span>'+x.k+'</span><span class="font-semibold">'+Fm(x.imp)+' <span style="color:var(--mut)">· '+(x.imp/totI*100).toFixed(1)+'%</span> <span class="badge" style="background:#eef2ff;color:#4338ca">'+x.u.toLocaleString('es-AR')+' u · '+(x.u/totU*100).toFixed(1)+'%</span></span></div><div class="h-3 rounded-full" style="background:#f0f1f4"><div class="h-full rounded-full" style="width:'+((catSort==='imp'?x.imp:x.u)/mx*100)+'%;background:'+PAL[i%PAL.length]+'"></div></div></div>').join('')+'</div>';
};

let fCanal='ALL';
RENDER.canales=()=>{const brs=selBrs(fCanal);const raw=mergeDict(brs,'canal');const c={};
 Object.entries(raw).forEach(([k,v])=>{let nk=k;if(k==='TUCAN'||k==='DELIVERY')nk='LENO+';else if(k==='PEDIDOS YA')nk='PedidosYa';else if(k==='TAKEAWAY')nk='Take Away';else if(k==='Salón/Mostrador')nk='Salón / Mostrador';c[nk]=(c[nk]||0)+v;});
 const arr=Object.entries(c).map(([k,v])=>({k,v,peya:k==='PedidosYa'})).sort((a,b)=>b.v-a.v);const tot=arr.reduce((s,x)=>s+x.v,0)||1;const mx=arr.length?arr[0].v:1;const lenoMas=c['LENO+']||0;
 const el=document.getElementById('sec-canales');
 el.innerHTML=filterBar('fCanal','canales',fCanal)+'<div class="grid grid-cols-1 lg:grid-cols-3 gap-4"><div class="card p-5 lg:col-span-2"><div class="font-semibold mb-4">Ventas por canal</div>'+arr.map((x,i)=>'<div class="mb-4"><div class="flex justify-between text-sm mb-1"><span class="flex items-center gap-2">'+(x.peya?'<img src="'+IMG.peya+'" class="w-4 h-4 rounded"/>':'')+x.k+'</span><span class="font-semibold">'+Fm(x.v)+' <span style="color:var(--mut)">· '+(x.v/tot*100).toFixed(1)+'%</span></span></div><div class="h-3 rounded-full" style="background:#f0f1f4"><div class="h-full rounded-full" style="width:'+(x.v/mx*100)+'%;background:'+(x.peya?'#FA0050':PAL[i%PAL.length])+'"></div></div></div>').join('')+'</div>'+
  '<div class="flex flex-col gap-4"><div class="card p-5"><div class="font-semibold mb-1" style="color:#FA0050">PedidosYa</div><div class="text-3xl font-bold" style="color:#FA0050">'+((c['PedidosYa']||0)/tot*100).toFixed(1)+'%</div><div class="text-sm mt-1" style="color:var(--mut)">'+Fm(c['PedidosYa']||0)+'</div></div><div class="card p-5"><div class="font-semibold mb-1" style="color:#E2001A">LENO+ (delivery propio)</div><div class="text-3xl font-bold" style="color:#E2001A">'+(lenoMas/tot*100).toFixed(1)+'%</div><div class="text-sm mt-1" style="color:var(--mut)">'+Fm(lenoMas)+' · sin comisión</div></div></div></div>'+
  note('“LENO+” agrupa delivery propio + Tucán. '+DATA.period_meta[PERIOD].label+': '+DATA.period_meta[PERIOD].scope+'.');
};
function filterBar(varName,sec,cur){return '<div class="flex items-center gap-2 mb-4"><span class="text-[12px] font-semibold" style="color:var(--mut)">Sucursal:</span><select class="sel" onchange="'+varName+'=this.value;RENDER.'+sec+'()">'+brOpts(cur)+'</select></div>';}

let fTurno='ALL';
RENDER.turnos=()=>{const brs=selBrs(fTurno);const t=mergeDict(brs,'turno');const map={'Mediodia':'Mediodía','AFTER':'After Office','Noche':'Noche'};
 const arr=Object.entries(t).map(([k,v])=>({k:map[k]||k,v})).sort((a,b)=>b.v-a.v);const tot=arr.reduce((s,x)=>s+x.v,0)||1;const el=document.getElementById('sec-turnos');
 el.innerHTML=filterBar('fTurno','turnos',fTurno)+'<div class="grid grid-cols-1 lg:grid-cols-2 gap-4"><div class="card p-5"><div class="font-semibold mb-3">Ventas por turno</div><canvas id="cTurno" height="160"></canvas></div><div class="card p-5"><div class="font-semibold mb-3">Detalle</div>'+arr.map((x,i)=>'<div class="flex justify-between items-center py-3" style="border-bottom:1px solid var(--line)"><span class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-full" style="background:'+PAL[i%PAL.length]+'"></span>'+x.k+'</span><div class="text-right"><div class="font-semibold">'+Fm(x.v)+'</div><div class="text-[12px]" style="color:var(--mut)">'+(x.v/tot*100).toFixed(1)+'%</div></div></div>').join('')+'</div></div>';
 mkChart('cTurno',{type:'bar',data:{labels:arr.map(x=>x.k),datasets:[{data:arr.map(x=>x.v),backgroundColor:arr.map((x,i)=>PAL[i%PAL.length]),borderRadius:8}]},options:{indexAxis:'y',plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>Fm(c.raw)}}},scales:{x:{ticks:{callback:v=>'$'+(v/1e6).toFixed(1)+'M'},grid:{color:LINE}},y:{grid:{display:false}}}}});
};
let fFisc='ALL';
RENDER.fiscal=()=>{const brs=selBrs(fFisc);const c=mergeDict(brs,'comprobante');const lbl={'FAB':'FAB · Factura B','FAA':'FAA · Factura A','FAX':'FAX · Ticket/no fiscal','S/C':'Sin comprobante'};
 const arr=Object.entries(c).map(([k,v])=>({k:lbl[k]||k,v})).sort((a,b)=>b.v-a.v);const tot=arr.reduce((s,x)=>s+x.v,0)||1;const el=document.getElementById('sec-fiscal');
 el.innerHTML=filterBar('fFisc','fiscal',fFisc)+'<div class="grid grid-cols-1 lg:grid-cols-2 gap-4"><div class="card p-5"><div class="font-semibold mb-3">Por tipo de comprobante</div><canvas id="cFisc" height="170"></canvas></div><div class="card p-5"><div class="font-semibold mb-3">Detalle</div>'+arr.map((x,i)=>'<div class="flex justify-between items-center py-3" style="border-bottom:1px solid var(--line)"><span class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-full" style="background:'+PAL[i%PAL.length]+'"></span>'+x.k+'</span><div class="text-right"><div class="font-semibold">'+Fm(x.v)+'</div><div class="text-[12px]" style="color:var(--mut)">'+(x.v/tot*100).toFixed(1)+'%</div></div></div>').join('')+'</div></div>';
 mkChart('cFisc',{type:'bar',data:{labels:arr.map(x=>x.k),datasets:[{data:arr.map(x=>x.v),backgroundColor:arr.map((x,i)=>PAL[i%PAL.length]),borderRadius:8}]},options:{indexAxis:'y',plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>Fm(c.raw)}}},scales:{x:{ticks:{callback:v=>'$'+(v/1e6).toFixed(1)+'M'},grid:{color:LINE}},y:{grid:{display:false}}}}});
};
const DFAM=['Comercial/Cupones','Convenios comerciales','Convenio institucional','Promociones/Fidelización','Socios','Autorización Socios','Franquicias','Voucher','Gift Card','Interno/Comps','Ajuste sin concepto'];
const DFCOL={'Comercial/Cupones':'#E2001A','Convenios comerciales':'#f59e0b','Convenio institucional':'#d97706','Promociones/Fidelización':'#8b5cf6','Socios':'#2563eb','Autorización Socios':'#0ea5e9','Franquicias':'#14b8a6','Voucher':'#ec4899','Gift Card':'#64748b','Interno/Comps':'#ef4444','Ajuste sin concepto':'#94a3b8'};
const DMACRO={'Comercial/Cupones':'cli','Convenios comerciales':'cli','Convenio institucional':'cli','Promociones/Fidelización':'cli','Socios':'cli','Voucher':'cli','Autorización Socios':'int','Franquicias':'int','Interno/Comps':'int','Gift Card':'otr','Ajuste sin concepto':'otr'};
function descAgg(period,brs){const m={};brs.forEach(b=>{const d=(DATA.descdet[period]||{})[b]||{};for(const c in d){m[c]=(m[c]||0)+d[c];}});return m;}
let fDesc='ALL';
RENDER.descuentos=()=>{const brs=selBrs(fDesc);const el=document.getElementById('sec-descuentos');
 const concepts=descAgg(PERIOD,brs);const gross=brs.reduce((s,b)=>s+DATA.rankings[PERIOD][b].gross,0)||1;
 let tot=0;const famT={};const macro={cli:0,int:0,otr:0};const arr=[];
 for(const c in concepts){const v=concepts[c];tot+=v;const fm=DATA.descfam[c]||'Ajuste sin concepto';famT[fm]=(famT[fm]||0)+v;macro[DMACRO[fm]||'otr']+=v;arr.push({c,fm,v});}
 arr.sort((a,b)=>b.v-a.v);tot=tot||1;
 const famArr=DFAM.filter(f=>famT[f]).map(f=>({f,v:famT[f]}));const fmx=Math.max.apply(null,famArr.map(x=>x.v).concat([1]));
 const topc=arr[0];const intPct=macro.int/tot*100;
 el.innerHTML=filterBar('fDesc','descuentos',fDesc)+
  '<div class="grid grid-cols-1 md:grid-cols-4 gap-4">'+
   kpi('Descuentos totales',Fm(tot),DATA.period_meta[PERIOD].label,undefined,'#e11d48')+
   kpi('% sobre venta bruta',(tot/gross*100).toFixed(1)+'%','del bloque seleccionado',undefined,'#f59e0b')+
   kpi('A clientes / comercial',Fm(macro.cli),(macro.cli/tot*100).toFixed(0)+'% de descuentos',undefined,'#2563eb')+
   kpi('Internos / comps',Fm(macro.int),(macro.int/tot*100).toFixed(0)+'% de descuentos',undefined,'#ef4444')+'</div>'+
  '<div class="card p-5 mt-4"><div class="font-semibold mb-4">Por familia de descuento · '+DATA.period_meta[PERIOD].label+'</div>'+famArr.map(x=>'<div class="mb-3"><div class="flex justify-between text-sm mb-1"><span class="flex items-center gap-2"><span style="width:9px;height:9px;border-radius:2px;display:inline-block;background:'+(DFCOL[x.f]||'#94a3b8')+'"></span>'+x.f+'</span><span class="font-semibold">'+F(x.v)+' <span style="color:var(--mut)">· '+(x.v/tot*100).toFixed(1)+'%</span></span></div><div class="h-2.5 rounded-full" style="background:#f0f1f4"><div class="h-full rounded-full" style="width:'+(x.v/fmx*100)+'%;background:'+(DFCOL[x.f]||'#94a3b8')+'"></div></div></div>').join('')+'</div>'+
  '<div class="card p-5 mt-4"><div class="font-semibold mb-3">Ranking por concepto</div><div style="overflow-x:auto"><table class="text-sm"><thead><tr class="text-[12px] text-left" style="color:var(--mut)"><th class="py-2 pr-2 w-8">#</th><th class="py-2 pr-3">Concepto</th><th class="py-2 px-3">Familia</th><th class="py-2 px-3 text-right">Monto</th><th class="py-2 px-3 text-right">%</th></tr></thead><tbody>'+arr.slice(0,30).map((x,i)=>'<tr style="border-top:1px solid var(--line)"><td class="py-2 pr-2" style="color:var(--mut)">'+(i+1)+'</td><td class="py-2 pr-3">'+x.c+'</td><td class="py-2 px-3 text-[12px]"><span class="badge" style="background:#f3f4f6;color:'+(DFCOL[x.fm]||'#64748b')+'">'+x.fm+'</span></td><td class="py-2 px-3 text-right font-semibold" style="color:#e11d48">'+F(x.v)+'</td><td class="py-2 px-3 text-right" style="color:var(--mut)">'+(x.v/tot*100).toFixed(1)+'%</td></tr>').join('')+'</tbody></table></div>'+(arr.length>30?'<div class="text-[12px] mt-2" style="color:var(--mut)">Top 30 de '+arr.length+' conceptos.</div>':'')+'</div>'+
  '<div class="card p-5 mt-4"><div class="font-semibold mb-3">💡 Lectura</div><div class="grid md:grid-cols-2 gap-3 text-[13px]">'+
   insight('#e11d48','Incidencia',(tot/gross*100).toFixed(1)+'% de la venta bruta se va en descuentos y ajustes.')+
   (topc?insight('#f59e0b','Concepto principal','<b>'+topc.c+'</b> ('+topc.fm+') concentra '+(topc.v/tot*100).toFixed(0)+'% del total: '+F(topc.v)+'.'):'')+
   insight('#ef4444','Comps internos',intPct.toFixed(0)+'% no es descuento a cliente, es consumo interno/comps ('+Fm(macro.int)+'). Es control, no marketing.')+
   insight('#10b981','Acción',(tot/gross*100)>5?'Nivel alto: fijá un tope por comanda y auditá el concepto principal.':'Nivel controlado: vigilá que no escale mes a mes.')+'</div></div>'+
  '<div class="card p-5 mt-4"><div class="font-semibold mb-3">Evolución por mes · comercial vs interno</div><canvas id="cDescEvo" height="110"></canvas>'+note('Comparación entre meses (todas las sucursales del período de cada mes). Junio es parcial. “A clientes”: cupones, convenios, promos, socios, voucher. “Internos”: autorización socios, comps, franquicias.')+'</div>'+
  note('Derivado de líneas negativas a nivel comanda. En franquicias parte del descuento se carga sobre el producto sin concepto → cae en “Ajuste sin concepto”.');
 function macroOf(period){const mm={cli:0,int:0,otr:0};DATA.period_meta[period].branches.forEach(b=>{const d=(DATA.descdet[period]||{})[b]||{};for(const c in d){mm[DMACRO[DATA.descfam[c]||'Ajuste sin concepto']||'otr']+=d[c];}});return mm;}
 const ev=DATA.periods.map(macroOf);
 mkChart('cDescEvo',{type:'bar',data:{labels:DATA.periods.map(p=>DATA.period_meta[p].label),datasets:[{label:'A clientes / comercial',data:ev.map(x=>x.cli),backgroundColor:'#2563eb',borderRadius:4,stack:'s'},{label:'Internos / comps',data:ev.map(x=>x.int),backgroundColor:'#ef4444',borderRadius:4,stack:'s'},{label:'Canje / ajuste',data:ev.map(x=>x.otr),backgroundColor:'#94a3b8',borderRadius:4,stack:'s'}]},options:{plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:8,font:{size:10}}},tooltip:{callbacks:{label:c=>c.dataset.label+': '+Fm(c.raw)}}},scales:{x:{stacked:true,grid:{display:false}},y:{stacked:true,ticks:{callback:v=>'$'+(v/1e6).toFixed(1)+'M'},grid:{color:LINE}}}}});
};
let fEnvios='ALL',fMesa='ALL';
RENDER.envios=()=>{const brs=selBrs(fEnvios);const u=sumSub(brs,'envios','u'),i=sumSub(brs,'envios','imp');const el=document.getElementById('sec-envios');
 el.innerHTML=filterBar('fEnvios','envios',fEnvios)+'<div class="card p-5"><div class="font-semibold mb-1">🛵 Envíos</div><div class="text-[12px] mb-4" style="color:var(--mut)">Cargos de envío (en/fuera de zona), fuera del ranking de productos</div><div class="text-3xl font-bold">'+F(i)+'</div><div class="text-sm mt-1" style="color:var(--mut)">'+u.toLocaleString('es-AR')+' envíos</div></div>'+note('Se aíslan para no contaminar el ranking de comida ni el ticket de productos.');
};
RENDER.mesa=()=>{const brs=selBrs(fMesa);const u=sumSub(brs,'servmesa','u'),i=sumSub(brs,'servmesa','imp');const el=document.getElementById('sec-mesa');
 el.innerHTML=filterBar('fMesa','mesa',fMesa)+'<div class="card p-5"><div class="font-semibold mb-1">🍽️ Servicios de Mesa</div><div class="text-[12px] mb-4" style="color:var(--mut)">Cargos de servicio de mesa, rankeados por separado</div><div class="text-3xl font-bold">'+(i?F(i):'—')+'</div><div class="text-sm mt-1" style="color:var(--mut)">'+(u?u.toLocaleString('es-AR')+' cargos':'Sin registros')+'</div></div>'+note('Se aíslan para no contaminar el ranking de comida ni el ticket de productos.');
};

let pyBr='ALL';
RENDER.peya=()=>{const PY=DATA.peya;const el=document.getElementById('sec-peya');const allBr=PY.srlBr.concat(PY.frBr);
 const sc=pyBr==='ALL'?PY.total:PY.branches[pyBr];const scopeLbl=pyBr==='ALL'?'Todas las sucursales':pyBr;
 const part=pyBr==='ALL'?PY.participacion.toFixed(1)+'%':(sc.imp/PY.total.imp*100).toFixed(1)+'%';
 const partSub=pyBr==='ALL'?'PeYa sobre ventas de la red':'de las ventas PeYa de la red';
 let html='<div class="grid grid-cols-1 md:grid-cols-4 gap-4">'+
  kpi('Ventas PedidosYa',F(sc.imp),scopeLbl,undefined,'#2563eb')+
  kpi('Pedidos',sc.pedidos.toLocaleString('es-AR'),'comandas',undefined,'#0ea5e9')+
  kpi('Ticket promedio',F(sc.ticket),'por pedido',undefined,'#8b5cf6')+
  kpi('Participación',part,partSub,undefined,'#10b981')+'</div>';
 html+='<div class="flex items-center gap-2 flex-wrap mt-4 mb-2"><span class="text-[12px] font-semibold" style="color:var(--mut)">SUCURSAL:</span><select class="sel" onchange="pyBr=this.value;RENDER.peya()"><option value="ALL"'+(pyBr==='ALL'?' selected':'')+'>Todas las sucursales</option>'+allBr.map(b=>'<option value="'+b+'"'+(pyBr===b?' selected':'')+'>'+b+(PY.branches[b].parcial?' (parcial)':'')+'</option>').join('')+'</select>'+(pyBr!=='ALL'?'<span class="badge" style="background:#f3f4f6;color:'+(PY.srlBr.indexOf(pyBr)>=0?'#2563eb':'#f59e0b')+'">'+(PY.srlBr.indexOf(pyBr)>=0?'SRL':'Franquicia')+'</span>'+(PY.branches[pyBr].parcial?'<span class="badge" style="background:#fff7ed;color:#9a3412">parcial · '+PY.branches[pyBr].rango+'</span>':''):'')+'</div>';
 const dd=pyBr==='ALL'?PY.dias:(PY.diasBr[pyBr]||[]);
 html+='<div class="card p-5 mt-2"><div class="font-semibold mb-3">Evolución diaria · '+scopeLbl+'</div><canvas id="cPY" height="90"></canvas></div>';
 const cc=pyBr==='ALL'?PY.cat:PY.catBr[pyBr];const ao=cc['Always On']||{imp:0,u:0},io=cc['In & Out']||{imp:0,u:0};const tt=(ao.imp+io.imp)||1;
 html+='<div class="card p-5 mt-4"><div class="flex items-center justify-between mb-4"><div class="font-semibold">Always On vs In &amp; Out</div><span class="text-[11px]" style="color:var(--mut)">recurrente vs eventos</span></div><div class="grid grid-cols-2 gap-4"><div class="rounded-xl p-4" style="background:#ecfdf5;border:1px solid #a7f3d0"><div class="flex items-center gap-2 mb-2"><span style="width:9px;height:9px;border-radius:50%;background:#10b981;display:inline-block"></span><span class="text-[13px] font-bold" style="color:#047857">Always On</span><span class="text-[11px]" style="color:#059669">recurrente</span></div><div class="font-extrabold tracking-tight" style="font-size:27px;color:#065f46;line-height:1.05">'+F(ao.imp)+'</div><div class="text-[12px] mt-1.5" style="color:#059669">'+Math.round(ao.imp/tt*100)+'% del total · '+ao.u+' unidades</div></div><div class="rounded-xl p-4" style="background:'+(io.imp?'#fffbeb':'#f8fafc')+';border:1px solid '+(io.imp?'#fde68a':'var(--line)')+'"><div class="flex items-center gap-2 mb-2"><span style="width:9px;height:9px;border-radius:50%;background:'+(io.imp?'#f59e0b':'#cbd5e1')+';display:inline-block"></span><span class="text-[13px] font-bold" style="color:'+(io.imp?'#b45309':'#94a3b8')+'">In &amp; Out</span><span class="text-[11px]" style="color:'+(io.imp?'#d97706':'#94a3b8')+'">eventos</span></div><div class="font-extrabold tracking-tight" style="font-size:27px;color:'+(io.imp?'#92400e':'#cbd5e1')+';line-height:1.05">'+F(io.imp)+'</div><div class="text-[12px] mt-1.5" style="color:'+(io.imp?'#d97706':'#94a3b8')+'">'+(io.imp?Math.round(io.imp/tt*100)+'% del total · '+io.u+' unidades':'sin campañas In&amp;Out en el período')+'</div></div></div><div class="flex h-2.5 rounded-full overflow-hidden mt-4" style="background:#f0f1f4"><div style="width:'+Math.round(ao.imp/tt*100)+'%;background:#10b981"></div><div style="width:'+Math.round(io.imp/tt*100)+'%;background:#f59e0b"></div></div></div>';
 if(pyBr==='ALL'){const rows=allBr.map(b=>Object.assign({b:b,srl:PY.srlBr.indexOf(b)>=0},PY.branches[b])).sort((a,b)=>b.imp-a.imp);const mx=rows[0].imp||1;
  html+='<div class="card p-5 mt-4"><div class="font-semibold mb-3">Ranking por sucursal '+CROWN+'</div>'+rows.map((x,i)=>'<div class="mb-3"><div class="flex justify-between text-sm mb-1"><span>'+x.b+(i===0?' '+CROWN:'')+' <span class="badge" style="background:#f3f4f6;color:'+(x.srl?'#2563eb':'#f59e0b')+'">'+(x.srl?'SRL':'Franq')+'</span>'+(x.parcial?' <span class="badge" style="background:#fff7ed;color:#9a3412">parcial</span>':'')+'</span><span class="font-semibold">'+F(x.imp)+' <span style="color:var(--mut)">· '+x.pedidos+' ped</span></span></div><div class="h-2.5 rounded-full" style="background:#f0f1f4"><div class="h-full rounded-full" style="width:'+(x.imp/mx*100)+'%;background:'+PAL[i%PAL.length]+'"></div></div></div>').join('')+'</div>';}
 const pr=PY.promos.map(p=>Object.assign({n:p.nombre,cat:p.cat},(pyBr==='ALL'?{u:p.u,imp:p.imp}:(p.branches[pyBr]||{u:0,imp:0})))).filter(x=>x.imp>0).sort((a,b)=>b.imp-a.imp);const pmx=pr.length?pr[0].imp:1;
 html+='<div class="card p-5 mt-4"><div class="font-semibold mb-3">Ranking por promoción · '+scopeLbl+' '+CROWN+'</div>'+pr.map((x,i)=>'<div class="mb-3"><div class="flex justify-between items-center text-sm mb-1 gap-2"><span class="min-w-0">'+x.n+(i===0?' '+CROWN:'')+' <span class="badge" style="background:'+(x.cat==='In & Out'?'#fff7ed':'#ecfdf5')+';color:'+(x.cat==='In & Out'?'#b45309':'#059669')+'">'+x.cat+'</span></span><span class="font-semibold shrink-0">'+F(x.imp)+' <span style="color:var(--mut)">· '+x.u+'u</span></span></div><div class="h-2.5 rounded-full" style="background:#f0f1f4"><div class="h-full rounded-full" style="width:'+(x.imp/pmx*100)+'%;background:'+PAL[i%PAL.length]+'"></div></div></div>').join('')+'</div>';
 const cup=PY.cupones;const cupVal=pyBr==='ALL'?cup.total:(cup.byBr[pyBr]||0);
 html+='<div class="card p-5 mt-4" style="border-top:3px solid #E2001A"><div class="font-semibold mb-1">🎟️ Cupones PY</div><div class="text-[12px] mb-4" style="color:var(--mut)">Descuentos otorgados bajo el concepto “CUPON PY”</div><div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4"><div class="rounded-lg p-3" style="background:#fafbfc;border:1px solid var(--line)"><div class="text-[11px]" style="color:var(--mut)">Total cupones</div><div class="text-2xl font-bold">'+F(cupVal)+'</div></div><div class="rounded-lg p-3" style="background:#fafbfc;border:1px solid var(--line)"><div class="text-[11px]" style="color:var(--mut)">% sobre ventas PeYa</div><div class="text-2xl font-bold">'+(sc.imp?(cupVal/sc.imp*100).toFixed(1):'0')+'%</div></div><div class="rounded-lg p-3" style="background:#fafbfc;border:1px solid var(--line)"><div class="text-[11px]" style="color:var(--mut)">% sobre ventas red</div><div class="text-2xl font-bold">'+(cupVal/PY.netoRedJunio*100).toFixed(2)+'%</div></div></div>';
 if(pyBr==='ALL'){const cb=Object.entries(cup.byBr).sort((a,b)=>b[1]-a[1]);const cmx=cb.length?cb[0][1]:1;html+='<div class="font-semibold text-sm mb-2">Por sucursal</div>'+cb.map(e=>'<div class="mb-2"><div class="flex justify-between text-sm mb-1"><span>'+e[0]+'</span><span class="font-semibold">'+F(e[1])+'</span></div><div class="h-2 rounded-full" style="background:#f0f1f4"><div class="h-full rounded-full" style="width:'+(e[1]/cmx*100)+'%;background:#E2001A"></div></div></div>').join('')+note('Independencia no registra CUPON PY en el período. Los cupones salen del módulo de Descuentos (concepto único); no se suman a la venta.');}
 html+='</div>';
 html+=note('PedidosYa · '+DATA.peya.rango+' · Barrio Sur y FLIP con datos parciales (mes en curso). Es un subconjunto del total de la red — no se suma aparte. Independiente del selector de período.');
 el.innerHTML=html;
 mkChart('cPY',{type:'bar',data:{labels:dd.map(d=>d.fecha),datasets:[{label:'Ventas',data:dd.map(d=>d.imp),backgroundColor:'#0ea5e9',borderRadius:5}]},options:{plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>F(c.raw)+' · '+dd[c.dataIndex].u+'u'}}},scales:{y:{ticks:{callback:v=>'$'+(v/1e6).toFixed(1)+'M'},grid:{color:LINE}},x:{grid:{display:false}}}}});
};

let e26Br='ALL';
RENDER.especial2026=()=>{const E=DATA.especial2026;const el=document.getElementById('sec-especial2026');const allBr=E.srlBr.concat(E.frBr);
 const val=p=>e26Br==='ALL'?{imp:p.imp,u:p.u}:(p.branches[e26Br]||{imp:0,u:0});
 const tImp=E.productos.reduce((s,p)=>s+val(p).imp,0),tU=E.productos.reduce((s,p)=>s+val(p).u,0);
 const scopeLbl=e26Br==='ALL'?'Todas las sucursales':e26Br;
 const ranked=E.productos.map(p=>Object.assign({n:p.nombre},val(p))).sort((a,b)=>b.imp-a.imp);const activos=ranked.filter(x=>x.imp>0).length;
 let html='<div class="card p-5 mb-4" style="border-left:4px solid #E2001A"><div class="flex items-center gap-3 flex-wrap mb-1.5"><div class="text-xl font-extrabold tracking-tight">Especial 2026</div><span class="badge" style="background:#fef3c7;color:#92400e;font-weight:600">⏳ En curso · datos parciales</span></div><div class="text-[12.5px] leading-relaxed" style="color:var(--mut)">Período '+E.rango+'. Excluye los productos <b style="color:var(--txt)">LENO BUCKET</b>, que tienen su propia sección.</div></div>';
 html+='<div class="flex items-center gap-2 flex-wrap mb-4"><span class="text-[12px] font-semibold" style="color:var(--mut)">SUCURSAL:</span><select class="sel" onchange="e26Br=this.value;RENDER.especial2026()"><option value="ALL"'+(e26Br==='ALL'?' selected':'')+'>Todas las sucursales</option>'+allBr.map(b=>'<option value="'+b+'"'+(e26Br===b?' selected':'')+'>'+b+'</option>').join('')+'</select></div>';
 html+='<div class="grid grid-cols-1 md:grid-cols-3 gap-4">'+kpi('Ventas',F(tImp),scopeLbl,undefined,'#E2001A')+kpi('Unidades',tU.toLocaleString('es-AR'),'combos vendidos',undefined,'#f59e0b')+kpi('Productos con venta',activos+' / '+E.productos.length,'artículos activos',undefined,'#2563eb')+'</div>';
 const mx=(ranked.length&&ranked[0].imp)?ranked[0].imp:1;
 html+='<div class="card p-5 mt-4"><div class="font-semibold mb-3">Ranking por producto · '+scopeLbl+' '+CROWN+'</div>'+ranked.map((x,i)=>'<div class="mb-3"><div class="flex justify-between items-center text-sm mb-1 gap-2"><span class="min-w-0">'+x.n+((x.imp>0&&i===0)?' '+CROWN:'')+'</span><span class="font-semibold shrink-0">'+(x.imp?F(x.imp)+' <span style="color:var(--mut)">· '+x.u+'u</span>':'<span style="color:var(--mut)">sin ventas</span>')+'</span></div><div class="h-2.5 rounded-full" style="background:#f0f1f4"><div class="h-full rounded-full" style="width:'+(x.imp/mx*100)+'%;background:'+PAL[i%PAL.length]+'"></div></div></div>').join('')+'</div>';
 html+=note('Datos parciales ('+E.rango+'). Los volúmenes son bajos porque la promoción recién inicia y el mes está incompleto — se completarán al cargar el período full o al conectar la API.');
 el.innerHTML=html;
};

RENDER.burgerday=()=>{const buckets={};let bkTot=0,bkU=0;
 pbranches().forEach(b=>{const items=(DATA.rankings[PERIOD][b]&&DATA.rankings[PERIOD][b].items)||[];items.forEach(it=>{if(it.cat==='Leno Buckets'){buckets[b]=(buckets[b]||0)+it.imp;bkTot+=it.imp;bkU+=it.u;}});});
 const arr=Object.entries(buckets).sort((a,b)=>b[1]-a[1]);const mx=arr.length?arr[0][1]:1;const ham=(DATA.cat[PERIOD]['Hamburguesas']||{imp:0}).imp;const el=document.getElementById('sec-burgerday');
 el.innerHTML=promoHero(IMG.burgerday,'Burger Day',Fm(bkTot)+' · '+bkU.toLocaleString('es-AR')+' combos','center 83%')+
  '<div class="grid grid-cols-1 md:grid-cols-3 gap-4">'+kpi('Facturación Buckets',Fm(bkTot),DATA.period_meta[PERIOD].label,undefined,'#E2001A')+kpi('Unidades Buckets',bkU.toLocaleString('es-AR'),'combos',undefined,'#f59e0b')+kpi('% sobre Hamburguesas',(ham+bkTot>0?(bkTot/(ham+bkTot)*100).toFixed(1):'0')+'%','peso del formato',undefined,'#8b5cf6')+'</div>'+
  '<div class="card p-5 mt-4"><div class="font-semibold mb-4">Buckets por sucursal '+CROWN+'</div>'+(arr.length?arr.map(([b,v],i)=>'<div class="mb-3"><div class="flex justify-between text-sm mb-1"><span>'+b+(i===0?' '+CROWN:'')+'</span><span class="font-semibold">'+Fm(v)+'</span></div><div class="h-3 rounded-full" style="background:#f0f1f4"><div class="h-full rounded-full" style="width:'+(v/mx*100)+'%;background:'+PAL[i%PAL.length]+'"></div></div></div>').join(''):'<div class="text-sm" style="color:var(--mut)">Sin ventas de Buckets en este período.</div>')+note('En la vista Consolidado del Ranking, “X4 Cheeseburger con papas” se suma a “Leno Buckets Cheeseburger X4”.')+'</div>';
};
let bmView='all',bmBr='ALL';
RENDER.burgermes=()=>{const BM=DATA.burgermes,P=BM.promos;const el=document.getElementById('sec-burgermes');const allBr=BM.srlBr.concat(BM.frBr);
 const val=p=>bmBr==='ALL'?{imp:p.total.imp,u:p.total.u}:{imp:(p.branches[bmBr]||{imp:0}).imp,u:(p.branches[bmBr]||{u:0}).u};
 const totImp=P.reduce((s,p)=>s+val(p).imp,0),totU=P.reduce((s,p)=>s+val(p).u,0);
 const best=P.slice().sort((a,b)=>val(b).imp-val(a).imp)[0];const scopeLbl=bmBr==='ALL'?'Todas las sucursales':bmBr;const BMC=['#f59e0b','#8b5cf6','#E2001A'];
 let html=promoHero(IMG.burgermes,'Burger del Mes',Fm(P.reduce((s,p)=>s+p.total.imp,0))+' · '+P.reduce((s,p)=>s+p.total.u,0).toLocaleString('es-AR')+' u · 3 ediciones','center 40%');
 html+='<div class="flex items-center gap-2 flex-wrap mb-4"><span class="text-[12px] font-semibold" style="color:var(--mut)">SUCURSAL:</span><select class="sel" onchange="bmBr=this.value;RENDER.burgermes()"><option value="ALL"'+(bmBr==='ALL'?' selected':'')+'>Todas las sucursales</option>'+allBr.map(b=>'<option value="'+b+'"'+(bmBr===b?' selected':'')+'>'+b+'</option>').join('')+'</select>'+(bmBr!=='ALL'?'<span class="badge" style="background:#f3f4f6;color:'+(BM.srlBr.indexOf(bmBr)>=0?'#2563eb':'#f59e0b')+'">'+(BM.srlBr.indexOf(bmBr)>=0?'SRL':'Franquicia')+'</span>':'')+'</div>';
 html+='<div class="grid grid-cols-1 md:grid-cols-4 gap-4">'+P.map((p,i)=>{const v=val(p);return '<div class="card kpi p-5" style="--acc:'+BMC[i]+'"><div class="text-[11px] mb-2" style="color:var(--mut)">'+p.rango+'</div><div class="font-semibold leading-snug mb-2" style="min-height:2.4em">'+p.nombre+(p===best?' <span title="Mejor del período">🏆</span>':'')+'</div><div class="text-3xl font-bold tracking-tight">'+Fm(v.imp)+'</div><div class="text-[12px] mt-1.5" style="color:var(--mut)">'+v.u.toLocaleString('es-AR')+' unidades</div></div>';}).join('')+
  '<div class="card p-5" style="background:linear-gradient(135deg,#E2001A,#FA0050)"><div class="text-[11px] mb-2 text-white/80">'+BM.rango+'</div><div class="font-semibold leading-snug mb-2 text-white" style="min-height:2.4em">Acumulado · '+scopeLbl+'</div><div class="text-3xl font-bold tracking-tight text-white">'+Fm(totImp)+'</div><div class="text-[12px] mt-1.5 text-white/80">'+totU.toLocaleString('es-AR')+' unidades</div></div></div>';
 const opts=[['all','Las 3 comparadas']].concat(P.map((p,i)=>[String(i),p.nombre]));
 html+='<div class="card p-5 mt-4"><div class="flex items-center justify-between flex-wrap gap-2 mb-4"><div class="font-semibold">Detalle por hamburguesa</div><select class="sel" onchange="bmView=this.value;RENDER.burgermes()">'+opts.map(o=>'<option value="'+o[0]+'"'+(bmView===o[0]?' selected':'')+'>'+o[1]+'</option>').join('')+'</select></div>';
 if(bmView==='all'){
   html+='<canvas id="cBM" height="110"></canvas><div style="overflow-x:auto" class="mt-4"><table class="text-sm"><thead><tr class="text-[12px] text-left" style="color:var(--mut)"><th class="py-2.5 pr-3">Hamburguesa</th><th class="py-2.5 px-3">Período</th><th class="py-2.5 px-3 text-right">Unidades</th>'+(bmBr==='ALL'?'<th class="py-2.5 px-3 text-right">SRL</th><th class="py-2.5 px-3 text-right">Franquicias</th>':'')+'<th class="py-2.5 px-3 text-right">'+(bmBr==='ALL'?'Total':'Subtotal')+'</th></tr></thead><tbody>'+P.map(p=>{const v=val(p);return '<tr style="border-top:1px solid var(--line)"><td class="py-2.5 pr-3 font-semibold">'+p.nombre+(p===best?' 🏆':'')+'</td><td class="py-2.5 px-3 text-[12px]" style="color:var(--mut)">'+p.rango+'</td><td class="py-2.5 px-3 text-right">'+v.u.toLocaleString('es-AR')+'</td>'+(bmBr==='ALL'?'<td class="py-2.5 px-3 text-right">'+Fm(p.srl.imp)+'</td><td class="py-2.5 px-3 text-right">'+Fm(p.fr.imp)+'</td>':'')+'<td class="py-2.5 px-3 text-right font-bold">'+Fm(v.imp)+'</td></tr>';}).join('')+'</tbody></table></div>';
 } else {
   const p=P[+bmView];const allBr=BM.srlBr.concat(BM.frBr);
   const rows=allBr.map(b=>({b,u:(p.branches[b]||{u:0}).u,imp:(p.branches[b]||{imp:0}).imp,srl:BM.srlBr.indexOf(b)>=0})).sort((a,b)=>b.imp-a.imp);
   const mx=Math.max.apply(null,rows.map(x=>x.imp).concat([1]));
   html+='<div class="grid grid-cols-3 gap-3 mb-4"><div class="rounded-lg p-3" style="background:#fafbfc;border:1px solid var(--line)"><div class="text-[11px]" style="color:var(--mut)">Período</div><div class="font-semibold text-sm">'+p.rango+'</div></div><div class="rounded-lg p-3" style="background:#fafbfc;border:1px solid var(--line)"><div class="text-[11px]" style="color:var(--mut)">Total</div><div class="font-bold text-lg">'+Fm(p.total.imp)+'</div></div><div class="rounded-lg p-3" style="background:#fafbfc;border:1px solid var(--line)"><div class="text-[11px]" style="color:var(--mut)">Unidades</div><div class="font-bold text-lg">'+p.total.u.toLocaleString('es-AR')+'</div></div></div>';
   html+='<div class="font-semibold mb-3">Ranking por sucursal '+CROWN+'</div>'+rows.map((x,i)=>{const hl=x.b===bmBr;return '<div class="mb-3" style="'+(hl?'background:#fff7ed;padding:8px;border:1px solid #fed7aa;border-radius:8px':'')+'"><div class="flex justify-between text-sm mb-1"><span>'+x.b+(i===0?' '+CROWN:'')+' <span class="badge" style="background:#f3f4f6;color:'+(x.srl?'#2563eb':'#f59e0b')+'">'+(x.srl?'SRL':'Franq')+'</span>'+(hl?' <span class="badge" style="background:#E2001A;color:#fff">SELECCIONADA</span>':'')+'</span><span class="font-semibold">'+Fm(x.imp)+' <span style="color:var(--mut)">· '+x.u+'u</span></span></div><div class="h-2.5 rounded-full" style="background:#f0f1f4"><div class="h-full rounded-full" style="width:'+(x.imp/mx*100)+'%;background:'+(hl?'#E2001A':PAL[i%PAL.length])+'"></div></div></div>';}).join('')+
    '<div class="grid grid-cols-2 gap-3 mt-4 text-sm"><div class="rounded-lg p-3" style="background:#eff6ff"><span style="color:var(--mut)">SRL: </span><b>'+Fm(p.srl.imp)+'</b> ('+(p.srl.imp/p.total.imp*100).toFixed(0)+'%)</div><div class="rounded-lg p-3" style="background:#fffbeb"><span style="color:var(--mut)">Franquicias: </span><b>'+Fm(p.fr.imp)+'</b> ('+(p.fr.imp/p.total.imp*100).toFixed(0)+'%)</div></div>';
 }
 html+='</div>';
 const netTot=P.reduce((s,p)=>s+p.total.imp,0);const growth=(P[2].total.imp/P[0].total.imp-1)*100;const frShare=P.reduce((s,p)=>s+p.fr.imp,0)/netTot*100;const bn=P.slice().sort((a,b)=>b.total.imp-a.total.imp)[0];
 html+='<div class="card p-5 mt-4"><div class="font-semibold mb-3">💡 Lectura ejecutiva</div><div class="grid md:grid-cols-2 gap-3 text-[13px]">'+
  insight('#E2001A','Mejor del trimestre','<b>'+bn.nombre+'</b> ('+bn.rango+') lideró a nivel red con '+Fm(bn.total.imp)+' y '+bn.total.u.toLocaleString('es-AR')+' unidades.')+
  insight('#10b981','Tendencia','La promo creció <b>'+growth.toFixed(0)+'%</b> de la 1ª edición ('+P[0].mes+') a la 3ª ('+P[2].mes+'): el formato gana tracción mes a mes.')+
  insight('#f59e0b','Peso franquicias','Las franquicias aportaron <b>'+frShare.toFixed(0)+'%</b> del total de la promo — Independencia es el motor.')+
  insight('#2563eb','Acción',bmBr==='ALL'?'Replicar los atributos del ganador en próximas ediciones y reforzar stock/insumos en las 2 sucursales top.':'En <b>'+bmBr+'</b>, la mejor edición fue <b>'+best.nombre+'</b> ('+Fm(val(best).imp)+'). Ajustar la oferta local en base a eso.')+
  '</div></div>'+note('Dataset propio de la promo “Burger del Mes” ('+BM.rango+', 7 sucursales, pre-agregado). Es independiente del selector de período del panel.');
 el.innerHTML=html;
 if(bmView==='all')mkChart('cBM',{type:'bar',data:{labels:P.map(p=>p.nombre),datasets:[{label:'Facturación',data:P.map(p=>val(p).imp),backgroundColor:['#f59e0b','#8b5cf6','#E2001A'],borderRadius:8}]},options:{plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>Fm(c.raw)+' · '+val(P[c.dataIndex]).u+'u'}}},scales:{y:{ticks:{callback:v=>'$'+(v/1e6).toFixed(1)+'M'},grid:{color:LINE}},x:{grid:{display:false}}}}});
};
let mdBr='ALL',mdView='prod';
RENDER.mundiales=()=>{const MD=DATA.mundiales,P=MD.productos;const el=document.getElementById('sec-mundiales');const allBr=MD.srlBr.concat(MD.frBr);
 const val=p=>mdBr==='ALL'?{imp:p.total.imp,u:p.total.u}:{imp:(p.branches[mdBr]||{imp:0}).imp,u:(p.branches[mdBr]||{u:0}).u};
 const totImp=P.reduce((s,p)=>s+val(p).imp,0),totU=P.reduce((s,p)=>s+val(p).u,0);
 const ranked=P.map(p=>({p,v:val(p)})).sort((a,b)=>b.v.imp-a.v.imp);const best=ranked[0];
 const papas=P.filter(p=>p.side==='Papas').reduce((s,p)=>s+val(p).u,0),aros=totU-papas;
 const scopeLbl=mdBr==='ALL'?'Todas las sucursales':mdBr;const sideLbl=s=>'con '+s;const sideCol=s=>s==='Papas'?'#f59e0b':'#0ea5e9';const sideBg=s=>s==='Papas'?'#fff7ed':'#eff6ff';
 let html=promoHero(IMG.mundiales,'Nos Fuimos Mundiales',MD.vasos+' vasos entregados · '+Fm(MD.totalImp),'center 61%');
 html+='<div class="flex items-center gap-2 flex-wrap mb-4"><span class="text-[12px] font-semibold" style="color:var(--mut)">SUCURSAL:</span><select class="sel" onchange="mdBr=this.value;RENDER.mundiales()"><option value="ALL"'+(mdBr==='ALL'?' selected':'')+'>Todas las sucursales</option>'+allBr.map(b=>'<option value="'+b+'"'+(mdBr===b?' selected':'')+'>'+b+'</option>').join('')+'</select>'+(mdBr!=='ALL'?'<span class="badge" style="background:#f3f4f6;color:'+(MD.srlBr.indexOf(mdBr)>=0?'#2563eb':'#f59e0b')+'">'+(MD.srlBr.indexOf(mdBr)>=0?'SRL':'Franquicia')+'</span>':'')+'</div>';
 html+='<div class="grid grid-cols-1 md:grid-cols-4 gap-4">'+
  kpi('Facturación promo',Fm(totImp),scopeLbl,undefined,'#2563eb')+
  kpi('Vasos entregados',totU.toLocaleString('es-AR'),'1 vaso por unidad vendida',undefined,'#0ea5e9')+
  kpi('Producto top',best.p.burger,sideLbl(best.p.side)+' · '+Fm(best.v.imp),undefined,'#E2001A')+
  kpi('Mix Papas / Aros',(totU>0?Math.round(papas/totU*100):0)+'% / '+(totU>0?Math.round(aros/totU*100):0)+'%','papas vs aros de cebolla',undefined,'#f59e0b')+
 '</div>';
 html+='<div class="card p-5 mt-4"><div class="flex items-center justify-between flex-wrap gap-2 mb-4"><div class="font-semibold">Ranking de ventas</div><select class="sel" onchange="mdView=this.value;RENDER.mundiales()"><option value="prod"'+(mdView==='prod'?' selected':'')+'>Por producto</option><option value="suc"'+(mdView==='suc'?' selected':'')+'>Por sucursal</option></select></div>';
 if(mdView==='prod'){
   const mx=ranked[0].v.imp||1;
   html+='<div class="text-[12px] mb-3" style="color:var(--mut)">'+scopeLbl+' · '+totU.toLocaleString('es-AR')+' unidades = '+totU.toLocaleString('es-AR')+' vasos entregados</div>';
   html+=ranked.map((x,i)=>'<div class="mb-3"><div class="flex justify-between items-center text-sm mb-1 gap-2"><span class="min-w-0">'+'<b>'+x.p.burger+'</b>'+(i===0?' '+CROWN:'')+' <span class="badge" style="background:'+sideBg(x.p.side)+';color:'+sideCol(x.p.side)+'">'+sideLbl(x.p.side)+'</span></span><span class="font-semibold shrink-0">'+Fm(x.v.imp)+' <span style="color:var(--mut)">· '+x.v.u+'u</span></span></div><div class="h-2.5 rounded-full" style="background:#f0f1f4"><div class="h-full rounded-full" style="width:'+(x.v.imp/mx*100)+'%;background:'+PAL[i%PAL.length]+'"></div></div></div>').join('');
   html+='<div class="grid grid-cols-2 gap-3 mt-4 text-sm"><div class="rounded-lg p-3" style="background:#fff7ed;border:1px solid #fed7aa"><div class="text-[11px]" style="color:var(--mut)">🍟 Con Papas</div><div class="font-bold text-lg" style="color:#b45309">'+papas.toLocaleString('es-AR')+' <span class="text-sm font-normal">u ('+(totU>0?Math.round(papas/totU*100):0)+'%)</span></div></div><div class="rounded-lg p-3" style="background:#eff6ff;border:1px solid #bfdbfe"><div class="text-[11px]" style="color:var(--mut)">🧅 Con Aros de Cebolla</div><div class="font-bold text-lg" style="color:#0369a1">'+aros.toLocaleString('es-AR')+' <span class="text-sm font-normal">u ('+(totU>0?Math.round(aros/totU*100):0)+'%)</span></div></div></div>';
 } else {
   const brT=allBr.map(b=>{let imp=0,u=0;P.forEach(p=>{const x=p.branches[b];if(x){imp+=x.imp;u+=x.u;}});return{b,imp,u,srl:MD.srlBr.indexOf(b)>=0};}).sort((a,b)=>b.imp-a.imp);
   const mx=Math.max.apply(null,brT.map(x=>x.imp).concat([1]));
   html+='<div class="text-[12px] mb-3" style="color:var(--mut)">Total de la promo por sucursal · 1 vaso = 1 unidad vendida</div>';
   html+=brT.map((x,i)=>{const hl=x.b===mdBr;return '<div class="mb-3" style="'+(hl?'background:#fff7ed;padding:8px;border:1px solid #fed7aa;border-radius:8px':'')+'"><div class="flex justify-between text-sm mb-1"><span>'+x.b+(i===0?' '+CROWN:'')+' <span class="badge" style="background:#f3f4f6;color:'+(x.srl?'#2563eb':'#f59e0b')+'">'+(x.srl?'SRL':'Franq')+'</span>'+(hl?' <span class="badge" style="background:#E2001A;color:#fff">SELECCIONADA</span>':'')+'</span><span class="font-semibold">'+Fm(x.imp)+' <span style="color:var(--mut)">· '+x.u+' vasos</span></span></div><div class="h-2.5 rounded-full" style="background:#f0f1f4"><div class="h-full rounded-full" style="width:'+(x.imp/mx*100)+'%;background:'+(hl?'#E2001A':PAL[i%PAL.length])+'"></div></div></div>';}).join('');
 }
 html+='</div>';
 const netRanked=P.slice().sort((a,b)=>b.total.imp-a.total.imp);const star=netRanked[0];
 const srlImp=P.reduce((s,p)=>s+MD.srlBr.reduce((a,b)=>a+(p.branches[b]||{imp:0}).imp,0),0);const frImp=MD.totalImp-srlImp;
 const netPapas=P.filter(p=>p.side==='Papas').reduce((s,p)=>s+p.total.u,0);const netU=P.reduce((s,p)=>s+p.total.u,0);
 html+='<div class="card p-5 mt-4"><div class="font-semibold mb-3">💡 Lectura ejecutiva</div><div class="grid md:grid-cols-2 gap-3 text-[13px]">'+
  insight('#0ea5e9','Vasos entregados','Se entregaron <b>'+MD.vasos+' vasos coleccionables</b> en la semana — uno por cada unidad vendida de los 8 productos participantes.')+
  insight('#E2001A','Producto estrella','<b>'+star.burger+' '+sideLbl(star.side)+'</b> lideró a nivel red con '+Fm(star.total.imp)+' y '+star.total.u+' unidades.')+
  insight('#f59e0b','Acompañamiento','El <b>'+Math.round(netPapas/netU*100)+'%</b> eligió papas y solo el <b>'+Math.round((netU-netPapas)/netU*100)+'%</b> canjeó por aros de cebolla: la opción de aros tiene baja adopción pese a ser sin cargo.')+
  insight('#2563eb','Reparto SRL / Franquicias','Franquicias aportaron <b>'+Math.round(frImp/MD.totalImp*100)+'%</b> de la promo ('+Fm(frImp)+') vs '+Math.round(srlImp/MD.totalImp*100)+'% SRL ('+Fm(srlImp)+'). Independencia traccionó el grueso.')+
 '</div></div>'+note('Promo “Nos Fuimos Mundiales” ('+MD.rango+', 7 sucursales, datos a nivel comanda). Solo Salón / Take Away — excluye LENO+ y PedidosYa. Independiente del selector de período del panel.');
 el.innerHTML=html;
};

function exportCSV(){let rows=[['Sucursal','Facturacion '+PERIOD]];pbranches().forEach(b=>rows.push([b,DATA.branch_tot[PERIOD][b]]));rows.push(['TOTAL',DATA.groups[PERIOD].Total]);const csv=rows.map(r=>r.join(';')).join('\n');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));a.download='LENO_'+PERIOD+'.csv';a.click();}
(function(){var mn=['','Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'][new Date().getMonth()+1];var def=DATA.periods.indexOf(mn)>=0?mn:DATA.periods[DATA.periods.length-1];setPeriod(def);})();go('resumen');
</script></body></html>'''
twcss=open('twbuild/tw.css',encoding='utf-8').read()
HTML=HTML.replace('__TWCSS__',twcss).replace('__MASTER__',master).replace('__IMG__',img)
open('/mnt/user-data/outputs/index.html','w',encoding='utf-8').write(HTML)
print("written",round(len(HTML)/1024),"KB")
