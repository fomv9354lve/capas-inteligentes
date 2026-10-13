import re, html
from xml.etree import ElementTree as ET
def text_of(path):
    try: t=" ".join(ET.parse(path).getroot().itertext())
    except Exception: t=open(path,encoding="utf-8",errors="replace").read()
    t=html.unescape(re.sub(r"<[^>]+>"," ",t))
    for a,b in ((" "," "),(" "," "),(" "," "),(" "," "),("−","-"),("–","-"),("≤","<="),("≥",">="),("×","x")):
        t=t.replace(a,b)
    return re.sub(r"[ \t]+"," ",t)
PCT=re.compile(r"\b(\d+)\s*(?:/|of|out of)\s*(\d+)\b\s*\(\s*(\d+(?:\.\d+)?)\s*%\s*\)|\b(\d+(?:\.\d+)?)\s*%\s*\(\s*(\d+)\s*(?:/|of)\s*(\d+)\s*\)")
GRIM=re.compile(r"(?:\bmean\b|\bM\b)\s*(?:\(SD\))?\s*[=:]\s*(\d+\.\d+)[^.;\n]{0,80}?\b[nN]\s*=\s*(\d+)|\b[nN]\s*=\s*(\d+)[^.;\n]{0,80}?(?:\bmean\b|\bM\b)\s*[=:]\s*(\d+\.\d+)")
PVAL=re.compile(r"\b(t|F|χ2|chi2|chi-square|z)\s*\(\s*(\d+(?:\.\d+)?)\s*(?:,\s*(\d+(?:\.\d+)?))?\s*\)\s*=\s*(-?\d+(?:\.\d+)?)[^.;\n]{0,50}?\b[pP]\s*([<=>]=?)\s*(0?\.\d+|1\.0+)")
def items(t):
    out=[]
    for m in PCT.finditer(t):
        k,N,p = (m.group(1),m.group(2),m.group(3)) if m.group(1) else (m.group(5),m.group(6),m.group(4))
        out.append({"kind":"pct","k":int(k),"N":int(N),"pct":float(p),"decimals":len(p.split(".")[1]) if "." in p else 0})
    for m in GRIM.finditer(t):
        mean,n = (m.group(1),m.group(2)) if m.group(1) else (m.group(4),m.group(3))
        out.append({"kind":"grim","mean":float(mean),"n":int(n),"decimals":len(mean.split(".")[1])})
    for m in PVAL.finditer(t):
        v,pp=m.group(4),m.group(6)
        out.append({"kind":"pval","stat":m.group(1),"df1":float(m.group(2)),"df2":float(m.group(3)) if m.group(3) else None,
                    "value":float(v),"op":m.group(5),"p":float(pp),
                    "value_decimals":len(v.split(".")[1]) if "." in v else 0,"decimals":len(pp.split(".")[1]) if "." in pp else 0})
    return out

# ---------- tablas: celdas "k (p%)" bajo una columna con N conocido ----------
from xml.etree import ElementTree as _ET
_NPCT=re.compile(r"^\s*(\d+)\s*\(\s*(\d+(?:\.\d+)?)\s*%?\s*\)\s*$")
_HDRN=re.compile(r"\(?\s*[nN]\s*=\s*(\d+)\s*\)?")
def _clean(x): return html.unescape(x).replace("\u00a0"," ").replace("\u200a"," ").replace("−","-").strip()
def _grid(tw):
    """Aplana la tabla respetando colspan/rowspan: cada celda ocupa sus columnas reales."""
    grid=[]; pending={}   # pending[(row,col)] = texto por rowspan
    for ri,tr in enumerate(tw.iter("tr")):
        row=[]; ci_=0
        cells=[td for td in tr if td.tag in("td","th")]
        for td in cells:
            while (ri,ci_) in pending: row.append(pending.pop((ri,ci_))); ci_+=1
            txt=_clean(" ".join(td.itertext()))
            cs=int(td.get("colspan","1") or 1); rs=int(td.get("rowspan","1") or 1)
            for c in range(cs):
                row.append(txt)
                for r in range(1,rs): pending[(ri+r,ci_+c)]=txt
            ci_+=cs
        while (ri,ci_) in pending: row.append(pending.pop((ri,ci_))); ci_+=1
        grid.append(row)
    return grid
def table_items(path, min_consistent=0.7):
    out=[]
    try: root=_ET.parse(path).getroot()
    except Exception: return out
    for tw in root.iter("table-wrap"):
        rows=_grid(tw)
        if len(rows)<3: continue
        width=max(len(r) for r in rows)
        # cabecera = filas con <th> o las 2 primeras; N por columna = ultimo "n = X" visto en ella
        nhdr=max(1,sum(1 for tr in list(tw.iter("tr"))[:3] if any(td.tag=="th" for td in tr)))
        nhdr=max(nhdr,1)
        colN=[None]*width
        for r in rows[:max(nhdr,2)]:
            for i,c in enumerate(r):
                m=_HDRN.search(c)
                if m: colN[i]=int(m.group(1))
        if not any(colN): continue
        cols={}
        for r in rows[max(nhdr,2):]:
            for i,cell in enumerate(r):
                N=colN[i] if i<width else None
                m=_NPCT.match(cell) if N else None
                if m:
                    k,pc=int(m.group(1)),m.group(2)
                    cols.setdefault(i,[]).append((k,N,float(pc),len(pc.split(".")[1]) if "." in pc else 0))
        for i,items_ in cols.items():
            # puerta de autoconsistencia: si el N de cabecera no explica la mayoria de celdas,
            # es que lo lei mal -> no chequear esa columna (nunca marcar por un N mal leido)
            ok=sum(1 for k,N,pc,d in items_ if abs(100*k/N-pc)<=0.5*10**(-d)+1e-9)
            if len(items_)>=3 and ok/len(items_)<min_consistent: continue
            for k,N,pc,d in items_:
                out.append({"kind":"pct","k":k,"N":N,"pct":pc,"decimals":d,"src":"table"})
    return out
