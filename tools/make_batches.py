"""Turn logos.json into writes for Grapevine's shared store.

Usage: python tools/make_batches.py OUT_DIR
Writes OUT_DIR/index.json (collection "logoidx", doc "orgs": {"orgs": {name: website}}) and
OUT_DIR/shards/sXX.json (collection "logos", docs s00..sff: {"m": {website: data URI}}), plus
OUT_DIR/batch-N.json lists of up to 50 writes that point at those shard files.
The shard for a website is djb2-xor(website) % 256, matching logoShard() in Grapevine.
"""
import json, os, sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.abspath(sys.argv[1])


def shard(d):
    h = 5381
    for ch in d:
        h = ((h * 33) ^ ord(ch)) & 0xFFFFFFFF
    return "s%02x" % (h % 256)


L = json.load(open(os.path.join(root, "logos.json"), encoding="utf-8"))
os.makedirs(os.path.join(out, "shards"), exist_ok=True)
orgs = {n: d for n, d in L["orgs"].items() if d in L["domains"]}
json.dump({"orgs": orgs}, open(os.path.join(out, "index.json"), "w"), separators=(",", ":"))
shards = {}
for d, u in L["domains"].items():
    shards.setdefault(shard(d), {})[d] = u
names = sorted(shards)
for sid in names:
    json.dump({"m": shards[sid]}, open(os.path.join(out, "shards", sid + ".json"), "w"), separators=(",", ":"))
for i in range(0, len(names), 50):
    w = [{"op": "set", "collection": "logos", "doc_id": sid, "file_path": os.path.join(out, "shards", sid + ".json")} for sid in names[i:i + 50]]
    json.dump(w, open(os.path.join(out, f"batch-{i // 50}.json"), "w"), separators=(",", ":"))
print(f"{len(orgs)} organisations, {len(L['domains'])} icons in {len(names)} shards, {(len(names) + 49) // 50} batches")
