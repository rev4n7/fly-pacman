"""Data layer: pull the fly escape + pursuit + hearing circuit from male-cns:v1.0.

Run:  .venv\\Scripts\\python -m flypac.fetch

Writes to data/:
  neurons.csv  one row per neuron (bodyId, type, side, NT, sign, role, visual-field position)
  edges.csv    pre -> post chemical synapse counts, summed over ROIs (real connectome weights)
  meta.json    provenance: dataset, query thresholds, selection results, anchoring checks
"""
import json
import time

import numpy as np
import pandas as pd
from neuprint import Client, fetch_adjacencies

from . import config as C


def load_token():
    for line in (C.ROOT / ".env").read_text().splitlines():
        if line.startswith("NEUPRINT_APPLICATION_CREDENTIALS="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("NEUPRINT_APPLICATION_CREDENTIALS not found in .env")


def cy_list(items):
    return "[" + ",".join(f'"{i}"' for i in items) + "]"


def select_gf_middle(c, core):
    """Interneurons that receive from looming/hearing sensors and drive a Giant Fiber."""
    return c.fetch_custom(f"""
        MATCH (m:Neuron)-[w2:ConnectsTo]->(:Neuron {{type:"DNp01"}})
        WHERE w2.weight >= {C.GF_MID_MIN_OUT} AND NOT coalesce(m.type,"") IN {cy_list(core)}
          AND NOT coalesce(m.type,"") STARTS WITH "{C.HEARING_PREFIX}"
        WITH DISTINCT m
        MATCH (a:Neuron)-[w1:ConnectsTo]->(m)
        WHERE a.type IN {cy_list(C.LOOMING_TYPES)} OR a.type STARTS WITH "{C.HEARING_PREFIX}"
        WITH m, sum(w1.weight) AS w_in WHERE w_in >= {C.GF_MID_MIN_IN}
        RETURN m.bodyId AS bodyId, m.type AS type, w_in""")


def select_steer_middle(c, core):
    """Interneurons that receive from LC10a and drive the DNa02/DNa03 steering neurons."""
    return c.fetch_custom(f"""
        MATCH (m:Neuron)-[w2:ConnectsTo]->(d:Neuron)
        WHERE d.type IN ["DNa02","DNa03"] AND w2.weight >= {C.STEER_MID_MIN_OUT}
          AND NOT coalesce(m.type,"") IN {cy_list(core)}
        WITH DISTINCT m
        MATCH (a:Neuron)-[w1:ConnectsTo]->(m) WHERE a.type IN {cy_list(C.PURSUIT_TYPES)}
        WITH m, sum(w1.weight) AS w_in WHERE w_in >= {C.STEER_MID_MIN_IN}
        RETURN m.bodyId AS bodyId, m.type AS type, w_in""")


def select_jo(c, target_ids):
    return c.fetch_custom(f"""
        MATCH (a:Neuron)-[w:ConnectsTo]->(t:Neuron)
        WHERE a.type STARTS WITH "{C.HEARING_PREFIX}" AND t.bodyId IN {list(map(int, target_ids))}
        WITH a, sum(w.weight) AS w_out WHERE w_out >= {C.JO_MIN_OUT}
        RETURN a.bodyId AS bodyId, a.type AS type, w_out""")


def select_feedback(c, circuit_ids, target_ids):
    """Neurons (any NT) driven by the circuit that project back onto its middle/output cells."""
    return c.fetch_custom(f"""
        MATCH (i:Neuron)-[w2:ConnectsTo]->(m:Neuron)
        WHERE m.bodyId IN {list(map(int, target_ids))} AND NOT i.bodyId IN {list(map(int, circuit_ids))}
        WITH i, sum(w2.weight) AS w_out WHERE w_out >= {C.FEEDBACK_MIN_OUT}
        MATCH (s:Neuron)-[w1:ConnectsTo]->(i) WHERE s.bodyId IN {list(map(int, circuit_ids))}
        WITH i, w_out, sum(w1.weight) AS w_in WHERE w_in >= {C.FEEDBACK_MIN_IN}
        RETURN i.bodyId AS bodyId, i.type AS type, i.consensusNt AS nt, w_in, w_out""")


def synapse_moments(c, where, roi):
    """Per-neuron mean and covariance of synapse positions inside `roi`."""
    df = c.fetch_custom(f"""
        MATCH (n:Neuron)-[:Contains]->(:SynapseSet)-[:Contains]->(s:Synapse)
        WHERE {where} AND s["{roi}"]
        WITH n, s.location.x AS x, s.location.y AS y, s.location.z AS z
        RETURN n.bodyId AS bodyId, count(*) AS n,
          avg(x) AS x, avg(y) AS y, avg(z) AS z,
          avg(x*x) AS xx, avg(y*y) AS yy, avg(z*z) AS zz,
          avg(x*y) AS xy, avg(x*z) AS xz, avg(y*z) AS yz""")
    return df.set_index("bodyId")


def cov_of(row):
    m = np.array([row.x, row.y, row.z])
    s = np.array([[row.xx, row.xy, row.xz], [row.xy, row.yy, row.yz], [row.xz, row.yz, row.zz]])
    return s - np.outer(m, m)


def lobula_frame(tm1):
    """Build eye coordinates for one lobula from Tm1 (one Tm1 per visual column).

    Returns (origin, az_axis, el_axis, az_range, el_range, checks). Anchoring:
      * dataset y points ventral  -> elevation axis = -y projected into the lobula sheet
      * front of lobula = front of visual field (double optic chiasm; the
        medulla->lobula flip is verified in the data, see meta.json)
      * dataset z points posterior -> azimuth increases with z
    """
    P = tm1[["x", "y", "z"]].to_numpy()
    origin = P.mean(0)
    _, _, Vt = np.linalg.svd(P - origin, full_matrices=False)
    plane = Vt[:2]
    y = np.array([0.0, 1.0, 0.0])
    el = -(plane.T @ (plane @ y))
    el /= np.linalg.norm(el)
    normal = Vt[2]
    az = np.cross(normal, el)
    az /= np.linalg.norm(az)
    if np.corrcoef((P - origin) @ az, P[:, 2])[0, 1] < 0:  # azimuth increases toward posterior (z+)
        az = -az
    pa, pe = (P - origin) @ az, (P - origin) @ el
    az_rng = np.percentile(pa, [1, 99])
    el_rng = np.percentile(pe, [1, 99])
    checks = {"az_axis": az.round(3).tolist(), "el_axis": el.round(3).tolist(),
              "corr_az_z": float(np.corrcoef(pa, P[:, 2])[0, 1]),
              "corr_el_y": float(np.corrcoef(pe, P[:, 1])[0, 1])}
    return origin, az, el, az_rng, el_rng, checks


def main():
    t0 = time.time()
    c = Client(C.SERVER, dataset=C.DATASET, token=load_token())
    meta = {"dataset": C.DATASET, "server": C.SERVER, "fetched": time.strftime("%Y-%m-%d %H:%M:%S"),
            "neuprint_python": __import__("neuprint").__version__}

    core = C.LOOMING_TYPES + C.PURSUIT_TYPES + C.ESCAPE_TYPES + C.STEER_TYPES
    print("selecting middle layers ...")
    gf_mid = select_gf_middle(c, core)
    steer_mid = select_steer_middle(c, core)
    core_ids = c.fetch_custom(f"MATCH (n:Neuron) WHERE n.type IN {cy_list(core)} RETURN n.bodyId AS bodyId")
    gf_ids = c.fetch_custom('MATCH (n:Neuron {type:"DNp01"}) RETURN n.bodyId AS bodyId').bodyId
    jo = select_jo(c, list(gf_ids) + list(gf_mid.bodyId))
    meta["selection"] = {
        "gf_middle": gf_mid.groupby("type").size().to_dict(),
        "steer_middle": steer_mid.groupby("type").size().to_dict(),
        "jo": jo.groupby("type").size().to_dict(),
        "thresholds": {k: getattr(C, k) for k in dir(C) if k.endswith(("_MIN_IN", "_MIN_OUT"))},
    }
    ids = sorted(set(core_ids.bodyId) | set(gf_mid.bodyId) | set(steer_mid.bodyId) | set(jo.bodyId))
    out_ids = c.fetch_custom(f"MATCH (n:Neuron) WHERE n.type IN {cy_list(C.ESCAPE_TYPES + C.STEER_TYPES)} "
                             "RETURN n.bodyId AS bodyId").bodyId
    fb = select_feedback(c, ids, set(out_ids) | set(gf_mid.bodyId) | set(steer_mid.bodyId))
    meta["selection"]["feedback"] = fb.groupby("nt").size().to_dict()
    meta["selection"]["feedback_types"] = fb.groupby("type").size().to_dict()
    ids = sorted(set(ids) | set(fb.bodyId))
    print(f"  {len(ids)} neurons  (gf-middle {len(gf_mid)}, steer-middle {len(steer_mid)}, JO {len(jo)}, "
          f"feedback {len(fb)}: {fb.groupby('nt').size().to_dict()})")

    print("fetching neuron properties ...")
    neurons = c.fetch_custom(f"""
        MATCH (n:Neuron) WHERE n.bodyId IN {ids}
        RETURN n.bodyId AS bodyId, n.type AS type, n.instance AS instance, n.somaSide AS side,
               n.consensusNt AS nt, n.predictedNtConfidence AS nt_conf, n.pre AS pre, n.post AS post,
               n.status AS status, n.group AS group""").set_index("bodyId")
    neurons["sign"] = neurons.nt.map(C.NT_SIGN).fillna(0).astype(int)
    role = pd.Series("middle_gf", index=neurons.index)
    role[neurons.index.isin(fb.bodyId)] = "middle_feedback"
    role[neurons.index.isin(steer_mid.bodyId)] = "middle_steer"
    role[neurons.type.isin(C.LOOMING_TYPES)] = "sense_looming"
    role[neurons.type.isin(C.PURSUIT_TYPES)] = "sense_pursuit"
    role[neurons.type.fillna("").str.startswith(C.HEARING_PREFIX)] = "sense_hearing"
    role[neurons.type.isin(C.ESCAPE_TYPES)] = "out_escape"
    role[neurons.type.isin(C.STEER_TYPES)] = "out_steer"
    neurons["role"] = role

    print("fetching connectivity (neuprint-python fetch_adjacencies) ...")
    _, roi_conn = fetch_adjacencies(sources=ids, targets=ids, client=c)
    edges = (roi_conn.groupby(["bodyId_pre", "bodyId_post"], as_index=False)["weight"].sum()
             .rename(columns={"bodyId_pre": "pre", "bodyId_post": "post"}))
    print(f"  {len(edges)} connections, {edges.weight.sum()} synapses")

    print("computing visual-field positions (retinotopy) ...")
    vis_types = C.LOOMING_TYPES + C.PURSUIT_TYPES
    for col in ["azimuth", "elevation", "rf_az_sd", "rf_el_sd"]:
        neurons[col] = np.nan
    meta["retinotopy"] = {}
    tm1_x = {}
    for side in ["R", "L"]:
        roi = f"LO({side})"
        tm1 = synapse_moments(c, f'n.type="Tm1" AND n.somaSide="{side}"', roi)
        tm1_x[side] = tm1.x.mean()
        # verify the medulla->lobula front/back flip on this side
        tm1_me = synapse_moments(c, f'n.type="Tm1" AND n.somaSide="{side}"', f"ME({side})")
        both = tm1.join(tm1_me, rsuffix="_me", how="inner")
        flip_r = float(np.corrcoef(both.z, both.z_me)[0, 1])

        origin, az, el, az_rng, el_rng, checks = lobula_frame(tm1)
        lc = synapse_moments(c, f'n.type IN {cy_list(vis_types)} AND n.somaSide="{side}" AND s.type="post"', roi)
        az_scale = (C.AZ_BACK - C.AZ_FRONT) / (az_rng[1] - az_rng[0])
        el_scale = (C.EL_TOP - C.EL_BOTTOM) / (el_rng[1] - el_rng[0])
        for bid, row in lc.iterrows():
            d = np.array([row.x, row.y, row.z]) - origin
            cov = cov_of(row)
            neurons.loc[bid, "azimuth"] = C.AZ_FRONT + (d @ az - az_rng[0]) * az_scale
            neurons.loc[bid, "elevation"] = C.EL_BOTTOM + (d @ el - el_rng[0]) * el_scale
            neurons.loc[bid, "rf_az_sd"] = np.sqrt(max(az @ cov @ az, 0)) * az_scale
            neurons.loc[bid, "rf_el_sd"] = np.sqrt(max(el @ cov @ el, 0)) * el_scale
        meta["retinotopy"][side] = {"tm1_cells": len(tm1), "lc_cells_placed": len(lc),
                                    "corr_ME_z_vs_LO_z (expect strongly negative)": flip_r, **checks}

    # hearing sensors have no soma in the volume: side from where their axons synapse
    midline = (tm1_x["R"] + tm1_x["L"]) / 2  # dataset x increases toward fly's LEFT
    jo_ids = list(neurons.index[neurons.role == "sense_hearing"])
    if jo_ids:
        jx = c.fetch_custom(f"""
            MATCH (n:Neuron)-[:Contains]->(:SynapseSet)-[:Contains]->(s:Synapse)
            WHERE n.bodyId IN {jo_ids} AND s.type="pre"
            RETURN n.bodyId AS bodyId, avg(s.location.x) AS x""").set_index("bodyId")
        neurons.loc[jx.index, "side"] = np.where(jx.x > midline, "L", "R")
    meta["midline_x"] = float(midline)

    # sanity: direction-coding gradients expressed in real visual-field terms
    grads = {}
    for lc_type in ["LC4", "LPLC2"]:
        for dn in ["DNp01", "DNp02", "DNp04", "DNp11"]:
            for side in ["L", "R"]:
                cells = neurons[(neurons.type == lc_type) & (neurons.side == side)]
                targets = neurons.index[(neurons.type == dn) & (neurons.side == side)]
                w = (edges[edges.post.isin(targets)].groupby("pre").weight.sum()
                     .reindex(cells.index, fill_value=0))
                if w.sum() >= 100:
                    grads[f"{lc_type}->{dn} {side}"] = {
                        "synapses": int(w.sum()),
                        "corr_with_azimuth": round(float(np.corrcoef(w, cells.azimuth)[0, 1]), 2),
                        "corr_with_elevation": round(float(np.corrcoef(w, cells.elevation)[0, 1]), 2),
                        "weighted_mean_azimuth": round(float(np.average(cells.azimuth, weights=w + 1e-9)), 1)}
    meta["direction_gradients"] = grads

    C.DATA_DIR.mkdir(exist_ok=True)
    neurons.reset_index().to_csv(C.DATA_DIR / "neurons.csv", index=False)
    edges.to_csv(C.DATA_DIR / "edges.csv", index=False)
    meta["counts"] = {"neurons": len(neurons), "edges": len(edges), "synapses": int(edges.weight.sum()),
                      "by_role": neurons.role.value_counts().to_dict(),
                      "by_nt": neurons.nt.fillna("none").value_counts().to_dict()}
    meta["seconds"] = round(time.time() - t0, 1)
    (C.DATA_DIR / "meta.json").write_text(json.dumps(meta, indent=2, default=str))
    print(json.dumps({k: meta[k] for k in ["counts", "selection", "retinotopy", "direction_gradients"]},
                     indent=2, default=str))


if __name__ == "__main__":
    main()
