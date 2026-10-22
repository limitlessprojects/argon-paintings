#!/usr/bin/env python3
"""Run on a GitHub Actions runner (US egress): render the Argon artifact
page with a real browser, capture DOM + screenshots + every artifact/api
network response body. Dump everything into out/ for upload."""
import json, re, pathlib
from playwright.sync_api import sync_playwright

AID = "9znB6dfumu3bWHPWiwwNx2"
OUT = pathlib.Path("out"); OUT.mkdir(exist_ok=True)
URLS = [
    f"https://claude.ai/artifact/{AID}",
    f"https://claude.site/artifacts/{AID}",
]
caps = []

def on_response(r):
    u = r.url
    if ("artifact" in u.lower()) or ("/api/" in u) or ("claude.site" in u):
        try:
            body = r.text()
        except Exception as e:
            body = f"<<body unavailable: {e}>>"
        caps.append({
            "url": u, "status": r.status,
            "ctype": r.headers.get("content-type", ""),
            "body": body[:400000],
        })

with sync_playwright() as p:
    b = p.chromium.launch(headless=True,
                          args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(
        user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"),
        viewport={"width": 1440, "height": 900}, locale="en-US",
    )
    pg = ctx.new_page()
    pg.on("response", on_response)
    for i, u in enumerate(URLS):
        try:
            pg.goto(u, timeout=45000, wait_until="domcontentloaded")
        except Exception as e:
            caps.append({"nav_error": str(e)[:500], "url": u})
        try:
            pg.wait_for_timeout(9000)
        except Exception:
            pass
        (OUT / f"dom_{i}.html").write_text(pg.content())
        try:
            pg.screenshot(path=str(OUT / f"shot_{i}.png"))
        except Exception as e:
            caps.append({"shot_error": str(e)[:300], "url": u})
        try:
            txt = pg.evaluate("() => document.body ? document.body.innerText.slice(0,200000) : ''")
            (OUT / f"text_{i}.txt").write_text(txt or "")
        except Exception as e:
            caps.append({"text_error": str(e)[:300], "url": u})
    try:
        (OUT / "localStorage.json").write_text(json.dumps(
            pg.evaluate("() => Object.fromEntries(Object.entries(localStorage))"), indent=1))
    except Exception as e:
        caps.append({"storage_error": str(e)[:300]})
    b.close()

(OUT / "network.json").write_text(json.dumps(caps, indent=1))
print(f"DONE: {len(caps)} api/artifact responses captured")
