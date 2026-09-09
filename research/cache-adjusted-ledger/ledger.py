R = {
 "query_v2 (request-cond. evidence)": {
   "luna": {"off":(27366,532,22016,289), "on":(28336,533,17920,345)},
   "sol":  {"off":(56598,820,36352,388), "on":(28543,410,24064,186)},
   "astra":{"off":(44405,277,39040,0),   "on":(33006,170,27648,38)},
 },
 "sol_caller_completion": {"sol":  {"off":(45393,1427,26240,632), "on":(14824,401,0,364)}},
 "luna_cold_plan":        {"luna": {"off":(134824,3140,118016,1501), "on":(218973,4519,191232,1788)}},
 "memory_followup(ret.ctl)":{"luna":{"off":(194759,1659,167424,674), "on":(117385,1908,95488,852)}},
}
def pct(a,b): return (a-b)/a*100 if a else float('nan')
print("=== GROSS vs UNCACHED-INPUT SAVINGS ===")
print(f"{'experiment':34s} {'model':6s} {'grossIn%':>9s} {'uncIn%':>9s} {'out%':>8s} {'reason%':>9s} {'offUnc':>7s} {'onUnc':>7s} {'offCache%':>10s}")
for exp,md in R.items():
    for m,d in md.items():
        oi,oo,oc,orr=d["off"]; ni,no,nc,nrr=d["on"]; ou,nu=oi-oc,ni-nc
        rs=f"{pct(orr,nrr):9.2f}" if orr else "      n/a"
        print(f"{exp:34s} {m:6s} {pct(oi,ni):9.2f} {pct(ou,nu):9.2f} {pct(oo,no):8.2f} {rs} {ou:7d} {nu:7d} {oc/oi*100:9.1f}%")

print("\n=== BILLING-WEIGHTED INPUT SAVING (cached read priced at k x full rate) ===")
ks=(0.0,0.10,0.25,0.50,1.00)
print(f"{'experiment':34s} {'model':6s} " + " ".join(f"{'k='+str(k):>8s}" for k in ks))
for exp,md in R.items():
    for m,d in md.items():
        oi,oo,oc,orr=d["off"]; ni,no,nc,nrr=d["on"]; ou,nu=oi-oc,ni-nc
        print(f"{exp:34s} {m:6s} " + " ".join(f"{((ou+k*oc)-(nu+k*nc))/(ou+k*oc)*100:8.1f}" for k in ks))

print("\n=== PROJECT-WIDE (results/cost-audit.json this_frontier_snapshot) ===")
ti,to,tc,tr = 20728819,158659,14609152,71073
print(f"calls=897 input={ti:,} output={to:,} cached={tc:,} reasoning={tr:,}")
print(f"cached share of input = {tc/ti:.2%}; reasoning share of output = {tr/to:.2%}")
print(f"uncached input = {ti-tc:,}; non-reasoning output = {to-tr:,}")
print(f"EVEN IF Helix removed 100% of cached input -> max gross saving {tc/ti:.2%}, $ saving at k=0.1 only {(0.1*tc)/(ti-tc+0.1*tc):.2%}")
print(f"EVEN IF Helix removed 100% of non-reasoning output -> max output saving {(to-tr)/to:.2%}")

print("\n=== SOL COMPOSITION ===")
A_in,A_out=0.4957,0.5000; B_in,B_out=0.6734,0.7190
print(f"naive residual-independence GROSS: in={1-(1-A_in)*(1-B_in):.4f} out={1-(1-A_out)*(1-B_out):.4f}")
Aiu=pct(56598-36352,28543-24064); Biu=pct(45393-26240,14824-0)
print(f"uncached-input: A={Aiu:.4f} B={Biu:.4f} naive={1-(1-Aiu)*(1-Biu):.4f}")
# overlap/sharing bound: assume mechanisms attack disjoint token sets at best
print(f"\nIf both applied to Sol caller-completion baseline (45393/1427 gross):")
print(f"  gross both = {1-(1-A_in)*(1-B_in):.4f} -> {45393*(1-(1-(1-(1-A_in)*(1-B_in)))):,.0f} in, {1427*(1-(1-A_out)*(1-B_out)):,.0f} out")
print(f"  but B already subsumes: B arm had 0 tool calls; A attacks tool-output evidence -> HIGH OVERLAP")
