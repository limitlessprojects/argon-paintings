#!/usr/bin/env python3
"""Bulk-extract the Argon Paintings artifact from claudeusercontent frame.
Step 1 (--probe): one bundle + slice item[0], validate webp.
Step 2 (--all): parallel-download 89 bundles + sheets + code jsons, slice all 534."""
import json, pathlib, sys, subprocess, concurrent.futures as cf

BASE = "https://48da57fc-1f4e-4e6b-b748-fe5e625db31b.frame.claudeusercontent.com/_f/1791907938-cc27/"
ROOT = pathlib.Path("/home/z/my-project/paintings/argon")
BUNDLES = ROOT / "bundles"
FULL = ROOT / "full"
CODE = ROOT / "code"
SHEETS = ROOT / "sheets"
for d in (BUNDLES, FULL, CODE, SHEETS):
    d.mkdir(parents=True, exist_ok=True)

M = json.load(open(pathlib.Path(__file__).parent / "argon_manifest.json"))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0"

def fetch(url, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return str(dest), 200, dest.stat().st_size
    r = subprocess.run(["curl", "-sS", "--max-time", "120", "-A", UA, "-o", str(dest),
                        "-w", "%{http_code} %{size_download}", url],
                       capture_output=True, text=True)
    code, size = (r.stdout.split() + ["0", "0"])[:2]
    return str(dest), int(code), int(size)

def pad(n, w=2):
    return str(n).zfill(w)

def slice_items(items):
    ok = bad = 0
    for it in items:
        b, off, ln = it[5], it[6], it[7]
        src = BUNDLES / f"b{pad(b)}.webp"
        out = FULL / f"{it[1]}.webp"
        if out.exists() and out.stat().st_size == ln:
            ok += 1
            continue
        if not src.exists() or src.stat().st_size < off + ln:
            bad += 1
            continue
        data = src.read_bytes()[off:off + ln]
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            out.write_bytes(data)
            ok += 1
        else:
            bad += 1
            print(f"BAD SLICE {it[1]}: head={data[:12]!r}")
    return ok, bad

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--probe"
    if mode == "--probe":
        d, code, size = fetch(BASE + f"full/b00.webp", BUNDLES / "b00.webp")
        print(f"b00.webp: http={code} size={size}")
        d2, c2, s2 = fetch(BASE + "sheets/s0.webp", SHEETS / "s0.webp")
        print(f"s0.webp: http={c2} size={s2}")
        d3, c3, s3 = fetch(BASE + "reel/code.json", CODE / "reel_code.json")
        print(f"reel/code.json: http={c3} size={s3}")
        ok, bad = slice_items(M["items"][:3])
        print(f"slice probe: ok={ok} bad={bad}")
        if ok:
            first = FULL / f"{M['items'][0][1]}.webp"
            print("first painting:", first, first.stat().st_size, "bytes")
        return

    # --all
    bundles = sorted(set(it[5] for it in M["items"]))
    jobs = [(BASE + f"full/b{pad(b)}.webp", BUNDLES / f"b{pad(b)}.webp") for b in bundles]
    jobs += [(BASE + f"sheets/s{s}.webp", SHEETS / f"s{s}.webp") for s in range(9)]
    # code bundles: find getCodeBundle call sites -> c indices unknown; try c00..c40
    jobs += [(BASE + f"code/c{pad(c)}.json", CODE / f"c{pad(c)}.json") for c in range(0, 41)]
    print(f"downloading {len(jobs)} files ...")
    fails = []
    with cf.ThreadPoolExecutor(8) as ex:
        futs = {ex.submit(fetch, u, d): d for u, d in jobs}
        for i, f in enumerate(cf.as_completed(futs)):
            dest, code, size = f.result()
            if code != 200 or size == 0:
                fails.append((dest, code, size))
            if (i + 1) % 20 == 0:
                print(f"  {i+1}/{len(jobs)} done")
    print("fails:", fails[:20] or "none")
    # identify which code jsons are real (404s are empty files)
    real_code = sorted(p.name for p in CODE.glob("c*.json") if p.stat().st_size > 2)
    print("real code jsons:", real_code)
    ok, bad = slice_items(M["items"])
    print(f"SLICED: ok={ok}/534 bad={bad}")
    print(f"bundle disk: {sum(p.stat().st_size for p in BUNDLES.glob('*.webp'))/1e6:.1f} MB")
    print(f"full disk: {sum(p.stat().st_size for p in FULL.glob('*.webp'))/1e6:.1f} MB")

if __name__ == "__main__":
    main()
