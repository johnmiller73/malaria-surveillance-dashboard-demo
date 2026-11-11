"""Generate the synthetic sample data used by the demo dashboard.

Run from the repository root:  python scripts/make_sample_data.py
Writes data/geo_2025.csv, data/trend_2021_2025.csv and data/data.js.
All values are synthetic (fixed random seed) and are NOT real surveillance data.
"""
import random, csv, math, json, os
random.seed(42)
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","data")
S = [  # (internal code, unused, population index, burden weight, urbanisation index)
("A01","",4.4,0.9,0.4),
("A02","",5.0,1.2,0.25),
("A03","",6.0,1.0,0.35),
("A04","",6.0,0.8,0.6),
("A05","",8.3,1.35,0.2),
("A06","",2.6,1.0,0.3),
("A07","",6.5,1.15,0.25),
("A08","",6.4,1.2,0.25),
("A09","",4.7,1.0,0.35),
("A10","",6.2,0.9,0.5),
("A11","",3.2,1.05,0.25),
("A12","",4.9,0.85,0.55),
("A13","",3.6,0.9,0.35),
("A14","",4.7,0.85,0.55),
("A15","",4.0,0.7,0.85),
("A16","",3.9,1.25,0.25),
("A17","",5.9,0.9,0.4),
("A18","",7.0,1.45,0.15),
("A19","",9.0,1.2,0.55),
("A20","",15.5,1.3,0.5),
("A21","",10.4,1.4,0.2),
("A22","",5.6,1.6,0.15),
("A23","",5.0,1.05,0.3),
("A24","",3.6,0.95,0.35),
("A25","",15.4,0.45,0.9),
("A26","",2.9,1.1,0.3),
("A27","",6.8,1.45,0.25),
("A28","",6.3,0.85,0.55),
("A29","",5.3,0.95,0.35),
("A30","",5.0,0.9,0.4),
("A31","",8.0,0.95,0.6),
("A32","",4.7,1.0,0.35),
("A33","",7.9,0.85,0.75),
("A34","",6.4,1.5,0.2),
("A35","",3.3,1.15,0.2),
("A36","",3.7,1.3,0.15),
("A37","",5.3,1.55,0.15)]
EMR_LIVE={'A04', 'A33', 'A25', 'A20', 'A19', 'A28', 'A15', 'A12', 'A31', 'A14'}
# district urban flags per state, in generation order (1 = urban district)
DISTRICT_URBAN={'A20': '00000010000100000100100010000010000001000100', 'A25': '10100001001111110111', 'A19': '01000000110000000010001', 'A31': '010011111100000000000000000000001', 'A33': '00000000100000100000110', 'A08': '000000000000100000001000000', 'A22': '000001000000000000000', 'A27': '0000110000000000000000100', 'A15': '010001'}
SYS=[("public","Public facilities (HMIS)"),("private","Private facilities (HMIS)"),("emr","EMR exchange"),("community","Community (cHMIS)")]
NATC,NATD=68_500_000,185_000  # national totals for the synthetic Country X
YEARS=[2021,2022,2023,2024,2025]
def cl(x,a=0.02,b=0.97): return max(a,min(b,x))
def J(s): return random.gauss(0,s)
tot_w=sum(p*w for _,_,p,w,_ in S)

def profile(u, emr_live, perf):
    sc={"public":0.40-0.10*u+J(.02),"private":0.12+0.20*u+J(.02),"emr":0.01+0.07*u+J(.005),"community":0.16-0.10*u+J(.015)}
    sd={"public":0.28-0.05*u+J(.02),"private":0.08+0.10*u+J(.015),"emr":0.01+0.04*u+J(.004),"community":0.14-0.06*u+J(.015)}
    for d in (sc,sd):
        for k in d: d[k]=max(0.005,d[k])
    comp={"public":cl(0.86+perf+J(.04),.4,.99),"private":cl(0.48+perf+0.15*u+J(.08),.1,.95),
          "emr":cl((0.55+0.3*u+J(.08)) if emr_live else 0.05+J(.02),.01,.97),"community":cl(0.55+perf+J(.1),.1,.95)}
    acc={"public":cl(0.90+J(.04),.6,.98),"private":cl(0.70+J(.08),.35,.95),"emr":cl(0.85+J(.05),.5,.98),"community":cl(0.62+J(.1),.3,.92)}
    dacc={"public":cl(0.55+perf+J(.07),.2,.9),"private":cl(0.32+J(.07),.08,.7),"emr":cl(0.45+J(.08),.1,.85),"community":cl(0.18+J(.06),.03,.5)}
    lift={"public":0.14+J(.03),"private":0.15+J(.04),"emr":None,"community":0.18+J(.05)}
    return sc,sd,comp,acc,dacc,lift

def build_leaf(estc,estd,u,emr_live,perf):
    sc,sd,comp,acc,dacc,lift=profile(u,emr_live,perf)
    r={}
    for k,_ in SYS:
        ec=round(estc*sc[k]); ed=round(estd*sd[k])
        cc=comp[k]*acc[k]; cd=comp[k]*dacc[k]
        ue=max(1,round(ec/{"public":800,"private":1000,"emr":3000,"community":150}[k]))
        ur=round(ue*comp[k])
        if k=="emr": c21c=c21d=0.0
        else:
            c21c=cl(cc-lift[k],0.01); c21d=cl(cd-lift[k]*0.6,0.005)
        r[k]=dict(ec=ec,ed=ed,rc=round(ec*cc),rd=round(ed*cd),ue=ue,ur=ur,
                  ec21=ec*0.94, ed21=ed*0.95, rc21=ec*0.94*c21c, rd21=ed*0.95*c21d,
                  emr_live=emr_live)
    r["_estc"]=estc; r["_estd"]=estd
    return r

def agg(children):
    r={}
    for k,_ in SYS:
        r[k]={f:sum(c[k][f] for c in children) for f in ["ec","ed","rc","rd","ue","ur","ec21","ed21","rc21","rd21"]}
        r[k]["emr_live"]=any(c[k]["emr_live"] for c in children)
    r["_estc"]=sum(c["_estc"] for c in children); r["_estd"]=sum(c["_estd"] for c in children)
    return r

geos=[]  # (level, geo_id, parent_id, state, name, data)
_anon=random.Random(7); _order=list(range(len(S))); _anon.shuffle(_order)
SIDX={S[i][0]:k+1 for k,i in enumerate(_order)}  # internal code -> anonymised state number
state_data=[]
for code,name,pop,w,u in S:
    estc=NATC*pop*w/tot_w; estd=NATD*pop*w**1.15/sum(p*ww**1.15 for _,_,p,ww,_ in S)
    perf=J(.06); live=code in EMR_LIVE
    sid=f"CX-S{SIDX[code]:02d}"; sname=f"State {SIDX[code]:02d}"
    if code in DISTRICT_URBAN:
        names=list(DISTRICT_URBAN[code]); dnum=list(range(1,len(names)+1)); _anon.shuffle(dnum); ws=[random.lognormvariate(0,.45)*(1.6 if n=="1" else 1) for n in names]
        tw=sum(ws); kids=[]
        for i,(n,ww) in enumerate(zip(names,ws)):
            lu=cl(u+(0.25 if n=="1" else -0.12)+J(.05),0.05,0.98)
            lp=perf+J(.07)
            d=build_leaf(estc*ww/tw,estd*ww/tw,lu,live and (lu>0.35 or random.random()<.3),lp)
            kids.append(d)
            geos.append(("District",f"{sid}-D{dnum[i]:02d}",sid,sname,f"District {SIDX[code]:02d}-{dnum[i]:02d}",d))
        sd_=agg(kids)
    else:
        sd_=build_leaf(estc,estd,u,live,perf)
    sd_["_perf"]=perf; sd_["_u"]=u
    state_data.append((sid,sname,sd_))
    geos.append(("State",sid,"CX",sname,sname,sd_))
nat=agg([d for _,_,d in state_data])
geos.append(("National","CX","","Country X","Country X",nat))

geos.sort(key=lambda g:({"National":0,"State":1,"District":2}[g[0]],g[1]))
def pct(a,b): return round(100*a/b,1) if b else 0.0
rows=[]
for level,gid,pid,st,nm,d in geos:
    for metric,E,R,E21,R21,ESTK in [("cases","ec","rc","ec21","rc21","_estc"),("deaths","ed","rd","ed21","rd21","_estd")]:
        est_total=round(d[ESTK]); 
        sysrows=[]
        for k,lab in SYS:
            x=d[k]; e=x[E]; r=x[R]; cap=pct(r,e); c21=pct(x[R21],x[E21])
            comp=pct(x["ur"],x["ue"]); 
            accu=round(100*r/(e*x["ur"]/x["ue"]),1) if x["ur"] else 0.0
            if k=="emr" and not x["emr_live"]: act="Roll out EMR exchange"
            elif comp<70: act="Raise reporting completeness"
            elif accu<70: act="Improve recording & data quality"
            else: act="Maintain; verify through DQA"
            sysrows.append([k,lab,e,r,cap,c21,x["ue"],x["ur"],comp,accu,act])
        rep_e=sum(s[2] for s in sysrows); rep_r=sum(s[3] for s in sysrows)
        r21e=sum(d[k][E21] for k,_ in SYS); r21r=sum(d[k][R21] for k,_ in SYS)
        noc=est_total-rep_e
        sysrows.append(["nocare","No formal care (not reportable)",noc,0,0.0,0.0,"","","","",""])
        sysrows.append(["reportable","All reporting systems",rep_e,rep_r,pct(rep_r,rep_e),pct(r21r,r21e),"","","","",""])
        tot21_e=est_total*0.945
        sysrows.append(["total","WHO estimate (all cases)" if metric=="cases" else "WHO estimate (all deaths)",est_total,rep_r,pct(rep_r,est_total),pct(r21r,tot21_e),"","","","",""])
        for s in sysrows:
            k,lab,e,r,cap,c21,ue,ur,comp,accu,act=s
            rows.append(dict(row_id=f"{gid}_{k}_{metric[0]}",level=level,geo_id=gid,parent_id=pid,state=st,name=nm,
              system=k,system_label=lab,metric=metric,est=e,rep=r,gap=e-r,cap=cap,cap_2021=c21,
              cap_change=round(cap-c21,1) if k!="nocare" else "",units_expected=ue,units_reporting=ur,
              completeness=comp,accuracy=accu,action=act))
cols=list(rows[0].keys())
with open(os.path.join(OUT,"geo_2025.csv"),"w",newline="") as f:
    w=csv.DictWriter(f,cols); w.writeheader(); w.writerows(rows)

# trend: national + state, by year
tr=[]
def trend_for(gid,d):
    for metric,E,R,E21,R21,ESTK in [("cases","ec","rc","ec21","rc21","_estc"),("deaths","ed","rd","ed21","rd21","_estd")]:
        for yi,y in enumerate(YEARS):
            t=yi/4; tot_e=0; tot_r=0; rep_e=0
            for k,lab in SYS:
                x=d[k]
                e=round(x[E21]+(x[E]-x[E21])*t)
                if k=="emr":
                    f=[0,0,0,0.45,1][yi]; r=round(x[R]*f*(e/x[E] if x[E] else 0))
                else:
                    c0=x[R21]/x[E21] if x[E21] else 0; c1=x[R]/x[E] if x[E] else 0
                    c=c0+(c1-c0)*(t**0.9)+ (J(.006) if 0<yi<4 else 0)
                    r=round(e*max(0,c))
                rep_e+=e; tot_r+=r
                tr.append(dict(row_id=f"{gid}_{y}_{k}_{metric[0]}",geo_id=gid,year=y,system=k,system_label=lab,metric=metric,est=e,rep=r,cap=pct(r,e)))
            te=round(d[ESTK]*(0.945+0.055*t))
            tr.append(dict(row_id=f"{gid}_{y}_reportable_{metric[0]}",geo_id=gid,year=y,system="reportable",system_label="All reporting systems",metric=metric,est=rep_e,rep=tot_r,cap=pct(tot_r,rep_e)))
            tr.append(dict(row_id=f"{gid}_{y}_total_{metric[0]}",geo_id=gid,year=y,system="total",system_label="WHO estimate",metric=metric,est=te,rep=tot_r,cap=pct(tot_r,te)))
trend_for("CX",nat)
for sid,name,d in sorted(state_data): trend_for(sid,d)
with open(os.path.join(OUT,"trend_2021_2025.csv"),"w",newline="") as f:
    w=csv.DictWriter(f,list(tr[0].keys())); w.writeheader(); w.writerows(tr)
with open(os.path.join(OUT,"data.js"),"w") as f:
    g=open(os.path.join(OUT,"geo_2025.csv")).read(); t=open(os.path.join(OUT,"trend_2021_2025.csv")).read()
    f.write("// Generated from the CSV files in this folder so the page also works when opened straight from disk.\nwindow.SAMPLE_CSV = "+json.dumps({"geo":g,"trend":t})+";\n")
print(len(rows),"geo rows,",len(tr),"trend rows")
