import json, subprocess, time, os
EP="https://www.ebi.ac.uk/europepmc/webservices/rest"
fab=json.load(open("fab.json"))
def get(u): return subprocess.run(["curl","-sgL","--max-time","45",u],capture_output=True,text=True).stdout
have=0; out=[]
for i,p in enumerate(fab,1):
    d=get(f"{EP}/search?query=EXT_ID:{p['pmid']}&resultType=core&format=json")
    try: r=json.loads(d)["resultList"]["result"][0]
    except Exception: r={}
    pmcid=r.get("pmcid"); oa=r.get("isOpenAccess")=="Y"; ft=0
    if pmcid and oa and not os.path.exists(f"xml/{pmcid}.xml"):
        x=get(f"{EP}/{pmcid}/fullTextXML")
        if len(x)>5000: open(f"xml/{pmcid}.xml","w").write(x); ft=len(x)
    elif pmcid and os.path.exists(f"xml/{pmcid}.xml"): ft=os.path.getsize(f"xml/{pmcid}.xml")
    have+=bool(ft); out.append({**p,"pmcid":pmcid,"oa":oa,"fulltext":ft})
    if i%100==0: print(f"{i}/{len(fab)} texto={have}",flush=True)
    time.sleep(0.25)
json.dump(out,open("fab_ft_all.json","w"),indent=1)
print(f"DONE fabricados con texto: {have}/{len(fab)}")
