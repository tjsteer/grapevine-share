# Grapevine share and logos

Two small things that live outside Grapevine itself.

**Share menu (Android).** `index.html`, `manifest.webmanifest` and `sw.js` make a tiny installable page.
Open https://tjsteer.github.io/grapevine-share in Chrome on Android and choose Install. "Grapevine" then
appears in the share menu, and the home-screen icon opens the tracker.

**Organisation logos.** `logos/domains.txt` lists organisations and their own websites
(`Name|domain`). The "Build organisation logos" workflow fetches each site's icon, shrinks it to a
48px WebP and saves the set in `logos.json`. Grapevine reads logos from its own shared store, so after
the workflow runs, the new icons are copied in (`tools/make_batches.py` prepares the writes).
Grapevine also queues any organisation it shows without a logo, and those get added to the list.
