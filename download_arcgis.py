import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import requests


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def request_json(
    session: requests.Session,
    url: str,
    params: Dict[str, Any],
    timeout: int,
    max_retries: int,
    backoff_base: float,
) -> Dict[str, Any]:
    last_err: Optional[Exception] = None
    for attempt in range(max_retries):
        try:
            resp = session.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                raise RuntimeError(f"ArcGIS error: {data['error']}")
            return data
        except Exception as e:
            last_err = e
            sleep_s = backoff_base * (2 ** attempt) + random.random() * 0.25
            time.sleep(sleep_s)
    raise RuntimeError(f"Failed after {max_retries} retries. Last error: {last_err}")


def get_count(
    session: requests.Session,
    layer_url: str,
    where: str,
    timeout: int,
    max_retries: int,
    backoff_base: float,
) -> int:
    query_url = layer_url.rstrip("/") + "/query"
    params = {
        "where": where,
        "returnCountOnly": "true",
        "f": "json",
    }
    data = request_json(session, query_url, params, timeout, max_retries, backoff_base)
    return int(data.get("count", 0))


def download_layer(
    layer_url: str,
    out_path: Path,
    where: str,
    out_fields: str,
    page_size: int,
    include_geometry: bool,
    out_sr: Optional[int],
    timeout: int,
    max_retries: int,
    backoff_base: float,
    log_every_pages: int,
) -> None:
    query_url = layer_url.rstrip("/") + "/query"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "propbot-downloader/1.0",
            "Accept": "application/json",
        }
    )

    total = get_count(session, layer_url, where, timeout, max_retries, backoff_base)
    print(f"[{now_iso()}] Total matching records (countOnly): {total}")

    downloaded = 0
    page = 0
    offset = 0

    with out_path.open("w", encoding="utf-8") as f_out:
        while True:
            params = {
                "where": where,
                "outFields": out_fields,
                "returnGeometry": "true" if include_geometry else "false",
                "resultOffset": offset,
                "resultRecordCount": page_size,
                "f": "json",
            }
            if include_geometry and out_sr is not None:
                params["outSR"] = str(out_sr)

            data = request_json(session, query_url, params, timeout, max_retries, backoff_base)

            features = data.get("features", [])
            if not features:
                break

            for feat in features:
                row = {
                    "attributes": feat.get("attributes", {}),
                    "geometry": feat.get("geometry") if include_geometry else None,
                    "source": layer_url,
                    "ingested_at": now_iso(),
                }
                f_out.write(json.dumps(row, ensure_ascii=False) + "\n")

            downloaded += len(features)
            page += 1
            offset += page_size

            if page % log_every_pages == 0:
                print(f"[{now_iso()}] Downloaded {downloaded}/{total} records...")

            if len(features) < page_size:
                break

    meta = {
        "layer_url": layer_url,
        "where": where,
        "out_fields": out_fields,
        "include_geometry": include_geometry,
        "out_sr": out_sr,
        "page_size": page_size,
        "downloaded": downloaded,
        "expected_count": total,
        "completed_at": now_iso(),
    }
    meta_path = out_path.with_suffix(out_path.suffix + ".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"[{now_iso()}] Done. Wrote {downloaded} records to: {out_path}")
    print(f"[{now_iso()}] Metadata saved to: {meta_path}")

    if total and downloaded != total:
        print(
            f"Warning: downloaded ({downloaded}) != expected_count ({total}). "
            "This can happen if the dataset changes during download."
        )


def main() -> None:
    ap = argparse.ArgumentParser(description="Download ArcGIS REST Feature Layer to JSONL with pagination.")
    ap.add_argument("--layer-url", required=True, help="Full layer URL, e.g. .../MapServer/0 or .../FeatureServer/1")
    ap.add_argument("--out", required=True, help="Output JSONL path")
    ap.add_argument("--where", default="1=1", help="ArcGIS where clause (default: 1=1)")
    ap.add_argument("--out-fields", default="*", help="Fields to fetch, comma-separated or *")
    ap.add_argument("--page-size", type=int, default=2000, help="Records per page (default 2000)")
    ap.add_argument("--geometry", action="store_true", help="Include geometry in output")
    ap.add_argument("--out-sr", type=int, default=4326, help="Output spatial reference when geometry is on (default 4326)")
    ap.add_argument("--timeout", type=int, default=60, help="Request timeout seconds")
    ap.add_argument("--retries", type=int, default=6, help="Max retries per page")
    ap.add_argument("--backoff", type=float, default=0.6, help="Backoff base seconds")
    ap.add_argument("--log-every-pages", type=int, default=5, help="Log progress every N pages")

    args = ap.parse_args()

    out_sr = args.out_sr if args.geometry else None
    download_layer(
        layer_url=args.layer_url,
        out_path=Path(args.out),
        where=args.where,
        out_fields=args.out_fields,
        page_size=args.page_size,
        include_geometry=args.geometry,
        out_sr=out_sr,
        timeout=args.timeout,
        max_retries=args.retries,
        backoff_base=args.backoff,
        log_every_pages=args.log_every_pages,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)