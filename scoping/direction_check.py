"""Do looming cells at different positions in the visual field wire to different descending neurons?"""
import numpy as np, pandas as pd
from neuprint import Client
tok = open("../.env").read().split("=", 1)[1].strip()
c = Client("neuprint.janelia.org", dataset="male-cns:v1.0", token=tok)
pd.set_option("display.width", 200)
DNS = ["DNp01", "DNp02", "DNp04", "DNp06", "DNp11", "DNp03", "DNp05"]
for lc in ["LC4", "LPLC2"]:
    pos = c.fetch_custom(f'''MATCH (n:Neuron {{type:"{lc}"}})-[:Contains]->(:SynapseSet)-[:Contains]->(s:Synapse)
      WHERE s.type="post" AND (s["LO(R)"] OR s["LO(L)"] OR s["LOP(R)"] OR s["LOP(L)"])
      RETURN n.bodyId AS id, n.somaSide AS side, avg(s.location.x) AS x, avg(s.location.y) AS y, avg(s.location.z) AS z''')
    w = c.fetch_custom(f'''MATCH (n:Neuron {{type:"{lc}"}})-[w:ConnectsTo]->(d:Neuron) WHERE d.type IN {DNS}
      AND d.somaSide = n.somaSide RETURN n.bodyId AS id, d.type AS dn, w.weight AS w''')
    W = w.pivot_table(index="id", columns="dn", values="w", fill_value=0)
    for side in ["L", "R"]:
        p = pos[pos.side == side].set_index("id")
        X = p[["x", "y", "z"]].values; X = X - X.mean(0)
        _, S, Vt = np.linalg.svd(X, full_matrices=False)
        pcs = pd.DataFrame(X @ Vt[:2].T, index=p.index, columns=["PC1", "PC2"])
        d = pcs.join(W, how="left").fillna(0)
        cols = [k for k in DNS if k in d and d[k].sum() > 0]
        r = d[["PC1", "PC2"]].apply(lambda pc: d[cols].corrwith(pc)).round(2)
        print(f"\n{lc} side {side}: n={len(d)}  PC spread={np.round(S[:2]/np.sqrt(len(d)))}  total syn:", d[cols].sum().astype(int).to_dict())
        print("correlation of per-cell synapses with dendrite position:"); print(r.to_string())
