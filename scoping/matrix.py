from rawq import q
import pandas as pd
pd.set_option("display.width", 300); pd.set_option("display.max_columns", 60)
T = ["LC4","LPLC2","LC6","LC10a","PVLP151","AOTU019","AOTU001","AOTU012","AOTU025","AOTU015",
     "DNp01","DNp11","DNa02","DNa03","DNa01","DNp09","TTMn","PSI"]
tl = "[" + ",".join(f'"{t}"' for t in T) + "]"
df = q(f'''MATCH (a:Neuron)-[w:ConnectsTo]->(b:Neuron)
 WHERE a.type IN {tl} AND b.type IN {tl}
 RETURN a.type+"_"+coalesce(a.somaSide,"?") AS pre, b.type+"_"+coalesce(b.somaSide,"?") AS post, sum(w.weight) AS syn''')
m = df.pivot_table(index="pre", columns="post", values="syn", aggfunc="sum", fill_value=0)
m = m.loc[:, (m >= 20).any()].loc[(m >= 20).any(axis=1)]
print(m.to_string())
nt = q(f'MATCH (n:Neuron) WHERE n.type IN {tl} RETURN n.type, n.somaSide, count(n) AS n, collect(DISTINCT n.consensusNt) AS nt ORDER BY n.type')
print(nt.to_string())
df.to_csv("scope_matrix_long.csv", index=False)
