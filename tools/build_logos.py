"""Fetch each organisation's site icon and package them for Grapevine.

Reads logos/domains.txt ("Organisation|domain" per line), keeps icons already
built, fetches missing ones from public favicon services, and writes
logos.json at the repo root: {"orgs": {name: domain}, "domains": {domain: data URI}}.
Grapevine reads these from its shared store, so after a run, sync them in
(see README).
"""
import base64, io, json, os, urllib.request
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "logos", "domains.txt")
OUT_JSON = os.path.join(ROOT, "logos.json")
UA = {"User-Agent": "Mozilla/5.0 (Grapevine logo builder)"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def to_data_uri(raw):
    im = Image.open(io.BytesIO(raw))
    if getattr(im, "n_frames", 1) > 1 or im.format == "ICO":
        try:
            sizes = sorted(im.info.get("sizes", [im.size]), key=lambda s: s[0])
            im.size = sizes[-1]
        except Exception:
            pass
    im = im.convert("RGBA")
    if max(im.size) < 32:          # a 16px default globe means "no real icon"
        return None
    im.thumbnail((48, 48), Image.LANCZOS)
    canvas = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    canvas.paste(im, ((48 - im.width) // 2, (48 - im.height) // 2), im)
    buf = io.BytesIO()
    canvas.save(buf, "WEBP", quality=88, method=6)
    data = base64.b64encode(buf.getvalue()).decode()
    return "data:image/webp;base64," + data if len(data) < 55000 else None


def fetch(domain):
    for url in (f"https://www.google.com/s2/favicons?domain={domain}&sz=128",
                f"https://icons.duckduckgo.com/ip3/{domain}.ico"):
        try:
            uri = to_data_uri(get(url))
            if uri:
                return uri
        except Exception as e:
            print(f"  {domain}: {url.split('/')[2]} failed ({e.__class__.__name__})")
    return None


def main():
    orgs = {}
    for line in open(SRC, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "|" not in line:
            continue
        name, domain = (x.strip() for x in line.split("|", 1))
        domain = domain.lower().removeprefix("https://").removeprefix("http://").removeprefix("www.").strip("/")
        if name and domain:
            orgs[name] = domain
    old = {}
    if os.path.exists(OUT_JSON):
        old = json.load(open(OUT_JSON, encoding="utf-8")).get("domains", {})
    domains = {}
    for d in sorted(set(orgs.values())):
        if d in old:
            domains[d] = old[d]
            continue
        print("fetching", d)
        uri = fetch(d)
        if uri:
            domains[d] = uri
    out = {"orgs": orgs, "domains": domains}
    json.dump(out, open(OUT_JSON, "w", encoding="utf-8"), separators=(",", ":"))
    print(f"{len(domains)} of {len(set(orgs.values()))} domains have logos")


if __name__ == "__main__":
    main()
