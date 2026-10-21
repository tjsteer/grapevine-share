"""Turn logos.json into write batches for Grapevine's shared store.

Usage: python tools/make_batches.py OUT_DIR [--only-new SYNCED_LIST]
Writes OUT_DIR/index.json (the name -> website document for collection "logoidx", doc "orgs")
and OUT_DIR/batch-NN.json files, each a list of up to 50 {"op","collection","doc_id","data"}
writes for collection "logos" (one document per website: {"u": data URI}).
"""
import json, os, sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = sys.argv[1]
synced = set()
if "--only-new" in sys.argv:
    p = sys.argv[sys.argv.index("--only-new") + 1]
    if os.path.exists(p):
        synced = set(x.strip() for x in open(p) if x.strip())
L = json.load(open(os.path.join(root, "logos.json"), encoding="utf-8"))
os.makedirs(out, exist_ok=True)
orgs = {n: d for n, d in L["orgs"].items() if d in L["domains"]}
json.dump({"orgs": orgs, "updatedAt": 0}, open(os.path.join(out, "index.json"), "w"), separators=(",", ":"))
todo = [d for d in sorted(L["domains"]) if d not in synced]
for i in range(0, len(todo), 50):
    batch = [{"op": "set", "collection": "logos", "doc_id": d, "data": {"u": L["domains"][d]}} for d in todo[i:i + 50]]
    json.dump(batch, open(os.path.join(out, f"batch-{i // 50:02d}.json"), "w"), separators=(",", ":"))
print(f"{len(orgs)} organisations, {len(todo)} icons to write in {(len(todo) + 49) // 50} batches")
