# CONDITIONAL dollar analysis. Price vector from public GPT-5.x rate card (OpenAI, Dec 2025):
#   full input $1.25/M, cached input $0.125/M (90% discount), output $10/M (incl. reasoning).
#   => cached_k = 0.10, output:input price ratio = 8.0
# Helix's actual models (gpt-5.6-luna/sol, gpt-6-astra) have NO published rate card -> UNKNOWN.
PIN, PCACHE, POUT = 1.25, 0.125, 10.0
def cost(i,c,o): return (i-c)*PIN + c*PCACHE + o*POUT
R = {
 "query_v2": {"luna":((27366,22016,532),(28336,17920,533)),
              "sol":((56598,36352,820),(28543,24064,410)),
              "astra":((44405,39040,277),(33006,27648,170))},
 "sol_caller_completion": {"sol":((45393,26240,1427),(14824,0,401))},
 "luna_cold_plan": {"luna":((134824,118016,3140),(218973,191232,4519))},
 "memory_followup": {"luna":((194759,167424,1659),(117385,95488,1908))},
}
print("=== CONDITIONAL DOLLAR SAVINGS @ GPT-5.x rate card (input $1.25 / cached $0.125 / output $10) ===")
print(f"{'experiment':24s} {'model':6s} {'grossIn%':>9s} {'grossOut%':>10s} {'TOKEN-unwt%':>12s} {'DOLLAR%':>9s}")
for exp,md in R.items():
    for m,(off,on) in md.items():
        oi,oc,oo=off; ni,nc,no=on
        gi=(oi-ni)/oi*100; go=(oo-no)/oo*100
        tu=((oi+oo)-(ni+no))/(oi+oo)*100
        d=(1-cost(ni,nc,no)/cost(oi,oc,oo))*100
        print(f"{exp:24s} {m:6s} {gi:9.2f} {go:10.2f} {tu:12.2f} {d:9.2f}")

# V3 aggregates
V3={"luna":((1892382,1128448,14900),(1414009,1059840,9994)),
    "sol":((1934151,1143424,5040),(1528202,1061760,4770)),
    "astra":((1938334,1192448,3447),(1606616,1142784,3599))}
print("\n=== V3 AGGREGATE (Q4+A+W50+L40) ===")
print(f"{'model':6s} {'grossIn%':>9s} {'grossOut%':>10s} {'TOKEN-unwt%':>12s} {'DOLLAR%':>9s}  {'baseline $':>11s} {'helix $':>10s}")
for m,(off,on) in V3.items():
    oi,oc,oo=off; ni,nc,no=on
    gi=(oi-ni)/oi*100; go=(oo-no)/oo*100
    tu=((oi+oo)-(ni+no))/(oi+oo)*100
    d=(1-cost(ni,nc,no)/cost(oi,oc,oo))*100
    print(f"{m:6s} {gi:9.2f} {go:10.2f} {tu:12.2f} {d:9.2f}  {cost(oi,oc,oo)/1e6:11.4f} {cost(ni,nc,no)/1e6:10.4f}")
print("\n  price-sensitivity of V3 dollar saving (output:input ratio p, cache discount k):")
for m,(off,on) in V3.items():
    oi,oc,oo=off; ni,nc,no=on
    row=[]
    for p in (4,8,16):
        for k in (1.0,0.25,0.10):
            c0=(oi-oc)*1+oc*k+oo*p; c1=(ni-nc)*1+nc*k+no*p
            row.append(f"p{p}/k{k}:{100*(1-c1/c0):5.1f}")
    print(f"   {m:6s} " + "  ".join(row))
