#!/usr/bin/env python3
"""Download and structurally validate the official NTA GTFS Schedule feed.

The ZIP and its manifest are generated locally and should not be committed to the
website repository. The validator checks structure/references, not freshness or
complete rail coverage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_gtfs import validate_gtfs  # noqa: E402

DEFAULT_URL = "https://www.transportforireland.ie/transitData/Data/GTFS_All.zip"
USER_AGENT = "CICAN-RAIL-GTFS-Validator/1.0"


def download_and_validate(url: str, output: str | Path, timeout: int = 90) -> dict:
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    byte_count = 0
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=".gtfs-download-", suffix=".zip",
            dir=destination.parent, delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=timeout) as response:
                status = getattr(response, "status", 200)
                if status < 200 or status >= 300:
                    raise RuntimeError(f"Download failed with HTTP status {status}")
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    temporary.write(chunk)
                    digest.update(chunk)
                    byte_count += len(chunk)

        report = validate_gtfs(temporary_path)
        if report.errors:
            details = "; ".join(report.errors[:8])
            raise ValueError("Downloaded GTFS failed validation: " + details)

        temporary_path.replace(destination)
        temporary_path = None
        manifest = {
            "source_url": url,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "sha256": digest.hexdigest(),
            "size_bytes": byte_count,
            "validation": "passed_structural_checks",
            "counts": {
                "routes": len(report.files.get("routes.txt", [])),
                "trips": len(report.files.get("trips.txt", [])),
                "stops": len(report.files.get("stops.txt", [])),
                "stop_times": len(report.files.get("stop_times.txt", [])),
            },
            "warnings": report.warnings,
            "limitations": [
                "Structural validation does not prove the feed is current.",
                "Confirm DART/Irish Rail coverage and licence attribution before production routing.",
                "Do not pair this static feed with real-time data unless the versions match."
            ],
        }
        manifest_path = destination.with_suffix(destination.suffix + ".manifest.json")
        manifest_temp = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
        manifest_temp.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        manifest_temp.replace(manifest_path)
        return manifest
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="official or approved GTFS ZIP URL")
    parser.add_argument("--output", type=Path, default=Path("build/GTFS_All.zip"),
                        help="local output ZIP (default: build/GTFS_All.zip)")
    parser.add_argument("--timeout", type=int, default=90, help="network timeout in seconds")
    args = parser.parse_args()
    try:
        manifest = download_and_validate(args.url, args.output, args.timeout)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: structurally validated GTFS saved to {args.output}")
    print(f"SHA-256: {manifest['sha256']}")
    print(f"Counts: {json.dumps(manifest['counts'], sort_keys=True)}")
    print(f"Manifest: {args.output}.manifest.json")
    for warning in manifest["warnings"]:
        print(f"INFO: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
