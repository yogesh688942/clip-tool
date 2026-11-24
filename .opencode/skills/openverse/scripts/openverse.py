#!/usr/bin/env python3
r"""Tiny stdlib-only client for the public Openverse audio API.

No API key and no extra packages needed. Searches free Creative-Commons
recorded sounds and can download a result with its attribution line.

Examples:
    python openverse.py search "cartoon boing" --license cc0 --limit 8
    python openverse.py download <id> --out assets\sfx\boing.mp3
    python openverse.py fetch "whoosh" --dir assets\sfx --limit 3
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.openverse.org/v1/audio/"
UA = {"User-Agent": "clip-tool-openverse/1.0 (local sound search)"}


def _get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def search(query, license_id="cc0", limit=10, page=1, mature=False):
    params = {"q": query, "page_size": max(1, min(limit, 100)), "page": page}
    if license_id and license_id.lower() != "any":
        params["license"] = license_id.lower()
    if mature:
        params["mature"] = "true"
    data = _get(API + "?" + urllib.parse.urlencode(params))
    return data.get("results", []), data.get("result_count", 0)


def detail(audio_id):
    return _get(API + urllib.parse.quote(audio_id, safe="") + "/")


def fmt_duration(ms):
    if not ms:
        return "?"
    s = ms / 1000.0
    return f"{s:.2f}s"


def show(results, total):
    print(f"Openverse: {total} matches (showing {len(results)})")
    for i, r in enumerate(results, 1):
        dur = fmt_duration(r.get("duration"))
        print(
            f'{i:2}. {r.get("id")}  [{r.get("license", "?")}]  {dur}\n'
            f'    {r.get("title", "(untitled)")} - {r.get("creator", "unknown")} '
            f'({r.get("source", "?")})\n'
            f'    {r.get("foreign_landing_url", "")}'
        )


def _safe_name(text):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text or "sound").strip("_")[:70] or "sound"


def download(item, out_path, credits_path=None, timeout=120):
    url = item.get("url") or ""
    if not url:
        raise RuntimeError(f"no downloadable URL for {item.get('id')}")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp, open(out_path, "wb") as fh:
        while True:
            chunk = resp.read(1 << 16)
            if not chunk:
                break
            fh.write(chunk)
    line = item.get("attribution") or (
        f'"{item.get("title", "sound")}" by {item.get("creator", "unknown")} '
        f'({item.get("license", "?")}) - {item.get("foreign_landing_url", "")}'
    )
    if credits_path:
        first = not credits_path.exists()
        with open(credits_path, "a", encoding="utf-8") as fh:
            if first:
                fh.write("# Sound credits (Openverse)\n\n")
            fh.write(f"- {line}\n")
    return line


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="search for recorded sounds")
    s.add_argument("query")
    s.add_argument("--license", default="cc0", help="cc0, cc-by, etc, or 'any' (default: cc0)")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--page", type=int, default=1)
    s.add_argument("--mature", action="store_true")
    s.add_argument("--json", action="store_true")

    d = sub.add_parser("download", help="download one result by id")
    d.add_argument("id")
    d.add_argument("--out", required=True, help="output file path")
    d.add_argument("--credits", help="append the attribution line to this CREDITS.md")

    f = sub.add_parser("fetch", help="search and download the top N results")
    f.add_argument("query")
    f.add_argument("--dir", required=True, help="folder for the sounds")
    f.add_argument("--limit", type=int, default=3)
    f.add_argument("--license", default="cc0")
    f.add_argument("--prefix", default="")

    c = sub.add_parser("credits", help="print the attribution line for an id")
    c.add_argument("id")

    a = p.parse_args(argv)
    try:
        if a.cmd == "search":
            results, total = search(a.query, a.license, a.limit, a.page, a.mature)
            if a.json:
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                show(results, total)
        elif a.cmd == "credits":
            r = detail(a.id)
            print(r.get("attribution") or json.dumps(r, indent=2, ensure_ascii=False))
        elif a.cmd in ("download", "fetch"):
            from pathlib import Path
            if a.cmd == "download":
                item = detail(a.id)
                out = Path(a.out)
                out.parent.mkdir(parents=True, exist_ok=True)
                line = download(item, out, Path(a.credits) if a.credits else None)
                print(f"saved {out} ({out.stat().st_size} bytes)\ncredit: {line}")
            else:
                folder = Path(a.dir)
                folder.mkdir(parents=True, exist_ok=True)
                results, _ = search(a.query, a.license, max(a.limit, 1))
                if not results:
                    raise RuntimeError("no results")
                credits = folder / "CREDITS.md"
                for n, item in enumerate(results[: a.limit], 1):
                    ext = "." + (item.get("filetype") or "mp3").lower()
                    name = f"{a.prefix}{n:02d}_{_safe_name(item.get('title'))}{ext}"
                    out = folder / name
                    line = download(item, out, credits)
                    print(f"saved {out.name} - {line}")
                print(f"credits: {credits}")
    except (urllib.error.URLError, RuntimeError, OSError) as e:
        print(f"openverse: error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
