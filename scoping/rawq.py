"""Tiny anonymous neuPrint HTTP helper, used ONLY for pre-token scoping.
The real data layer uses neuprint-python (needs a token)."""
import json, sys, urllib.request
import pandas as pd

URL = "https://neuprint.janelia.org/api/custom/custom"
DATASET = "male-cns:v1.0"

def q(cypher):
    body = json.dumps({"cypher": cypher, "dataset": DATASET}).encode()
    req = urllib.request.Request(URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.load(r)
    if "error" in d:
        raise RuntimeError(d["error"])
    return pd.DataFrame(d["data"], columns=d["columns"])

if __name__ == "__main__":
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200); pd.set_option("display.max_columns", 30)
    print(q(sys.argv[1]).to_string())
