# Argon Paintings — full mirror (534)

**Art and code by Surya Narreddi ([@kickingkeys](https://x.com/kickingkeys)).**
This is an unofficial preservation mirror of his public **"Argon Paintings"** claude.ai artifact
([original artifact](https://claude.ai/artifact/9znB6dfumu3bWHPWiwwNx2)), extracted in full on **2026-10-23**
(1,966 views on the artifact at capture time).

The trending X post that showcased this project:

> **Direct X post:** [x.com/kickingkeys/status/2110037855452180633](https://x.com/kickingkeys/status/2110037855452180633)
>
> 534 procedural code paintings — instead of raster/diffusion image generation, the models
> (including **Gemini 4 Argon**) were prompted to output **pure executable JavaScript** that
> renders the art in real time.

All credit for every image and every line of painting code belongs to the author. If you enjoy
these, go follow/boost the original post and the author's channels.

## What is in here

| Path | Contents |
|---|---|
| `paintings/` | **534 full-res paintings** (1200×1200 webp, ~134 MB) — every one validated after extraction |
| `code/` | **27 code bundles** (`c00.json` … `c26.json`, 20 paintings per bundle) — the actual p5.js v2 + p5.brush (WEBGL) source for each painting |
| `contact-sheets/` | 9 contact sheets (8×8 grid, 64 thumbnails per sheet, `s0.webp` … `s8.webp`) |
| `manifest.json` | The gallery's own manifest: `[hash8, slug, bundle, pos, byteOffset, x, y, byteLen]` × 534, plus picks / sheet layout / round metadata |
| `artifact/` | The original single-file gallery HTML + its loader script, exactly as served from the artifact frame |
| `tools/` | The extraction scripts used to produce this mirror (GitHub Actions fetch job + byte-range reassembler) |
| `make_wallpaper.py` | Turn any painting into a 1920×1080 wallpaper (edge-sampled background pad) |

## The paintings

Every painting is procedurally painted by code — `p5.js` v2 with the `p5.brush` add-on in WEBGL
mode: brush strokes, ink washes and canvas textures, all from loops and vector paths. The code
bundles contain the verbatim painting program for each image (title comment, palette, brush
parameters, composition logic). Slugs describe the subject, e.g.
`pinstripe-candy-bowling-ball.webp`, `abalone-magpie-feathers-slate.webp`,
`adire-indigo-cracked-riverbed.webp`.

## Wallpaper use

```bash
python3 make_wallpaper.py paintings/pinstripe-candy-bowling-ball.webp wallpaper.png
# optional: python3 make_wallpaper.py <in.webp> <out.png> 2560 1440
```

Pads the 1200×1200 square onto your desktop resolution using the painting's own edge colours,
so no art is cropped away.

## How this was extracted (transparency)

The artifact's share page is geo-fenced for some regions/hosts, so the capture was done with a
GitHub Actions runner (Azure US egress, real headless browser). Loading the public share page
revealed the artifact frame endpoint on `claudeusercontent.com` — a **public, unauthenticated**
content host — which serves the gallery's manifest, the byte-ranged full-res webp bundles and
the code JSONs. `tools/extract_all.py` reassembles each painting from its manifest byte range
and validates the result. No auth was bypassed and no private data was accessed: the share page
was public, the frame host is public, everything here is what any visitor to that artifact sees.

## Rights and takedown

The upstream project carries **no open-source license**, so all rights remain with the author
(default copyright). This mirror exists for access, study and wallpaper use; if the author wants
it removed or re-licensed, open an issue or reach out and it will be taken down immediately.
