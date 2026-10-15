#!/usr/bin/env python3
"""Validate a downloaded NTA GTFS Schedule ZIP before CICAN RAIL uses it.

This intentionally validates data structure and key references only. It does not
claim that a feed is current, complete for rail, or suitable for live routing.
"""
from __future__ import annotations

import argparse
import csv
import io
import zipfile
from dataclasses import dataclass
from pathlib import Path

REQUIRED_COLUMNS = {
    "agency.txt": {"agency_name"},
    "routes.txt": {"route_id", "agency_id", "route_type"},
    "trips.txt": {"route_id", "service_id", "trip_id"},
    "stops.txt": {"stop_id", "stop_name"},
    "stop_times.txt": {"trip_id", "stop_id", "stop_sequence", "departure_time", "arrival_time"},
    "calendar.txt": {"service_id", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "start_date", "end_date"},
    "calendar_dates.txt": {"service_id", "date", "exception_type"},
}


@dataclass
class FeedReport:
    files: dict[str, list[dict[str, str]]]
    errors: list[str]
    warnings: list[str]


def _read_csv(archive: zipfile.ZipFile, name: str) -> list[dict[str, str]]:
    try:
        raw = archive.read(name).decode("utf-8-sig")
    except KeyError as exc:
        raise ValueError(f"Missing required GTFS file: {name}") from exc
    reader = csv.DictReader(io.StringIO(raw))
    headers = set(reader.fieldnames or [])
    missing = REQUIRED_COLUMNS[name] - headers
    if missing:
        raise ValueError(f"{name} is missing required columns: {', '.join(sorted(missing))}")
    return list(reader)


def validate_gtfs(path: str | Path) -> FeedReport:
    errors: list[str] = []
    warnings: list[str] = []
    files: dict[str, list[dict[str, str]]] = {}
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            for name in REQUIRED_COLUMNS:
                if name not in names:
                    errors.append(f"Missing required GTFS file: {name}")
            if errors:
                return FeedReport(files, errors, warnings)
            for name in REQUIRED_COLUMNS:
                try:
                    files[name] = _read_csv(archive, name)
                except (ValueError, UnicodeDecodeError) as exc:
                    errors.append(str(exc))
    except (OSError, zipfile.BadZipFile) as exc:
        return FeedReport({}, [f"Cannot read GTFS ZIP: {exc}"], [])

    if errors:
        return FeedReport(files, errors, warnings)

    for name in REQUIRED_COLUMNS:
        if not files[name]:
            errors.append(f"{name} contains no data rows")

    routes = files["routes.txt"]
    trips = files["trips.txt"]
    stops = files["stops.txt"]
    times = files["stop_times.txt"]
    services = {row["service_id"] for row in files["calendar.txt"]}
    services.update(row["service_id"] for row in files["calendar_dates.txt"])
    route_ids = {row["route_id"] for row in routes}
    trip_ids = {row["trip_id"] for row in trips}
    stop_ids = {row["stop_id"] for row in stops}

    if not any(row["route_type"] == "2" for row in routes):
        warnings.append("No route_type 2 (rail) routes found; verify this feed includes Irish Rail/DART.")
    if not trips:
        errors.append("trips.txt contains no trips")
    if not stops:
        errors.append("stops.txt contains no stops")

    for row in trips:
        if row["route_id"] not in route_ids:
            errors.append(f"Trip {row['trip_id']} references missing route {row['route_id']}")
        if row["service_id"] not in services:
            errors.append(f"Trip {row['trip_id']} references service {row['service_id']} absent from calendar files")

    for row in times:
        if row["trip_id"] not in trip_ids:
            errors.append(f"stop_times references missing trip {row['trip_id']}")
        if row["stop_id"] not in stop_ids:
            errors.append(f"stop_times for trip {row['trip_id']} references missing stop {row['stop_id']}")

    rail_routes = sum(row["route_type"] == "2" for row in routes)
    warnings.append(f"Found {len(routes)} routes, {len(trips)} trips, {len(stops)} stops, and {len(times)} stop-time rows; rail routes: {rail_routes}.")
    warnings.append("Structural validation only: check feed date, rail coverage, licence, attribution and matching realtime version before production use.")
    return FeedReport(files, errors, warnings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zipfile", type=Path, help="path to the downloaded GTFS Schedule ZIP")
    args = parser.parse_args()
    report = validate_gtfs(args.zipfile)
    for message in report.errors:
        print(f"ERROR: {message}")
    for message in report.warnings:
        print(f"INFO: {message}")
    if not report.errors:
        print("PASS: GTFS structural checks completed.")
        return 0
    print("FAIL: do not use this feed for route calculations until errors are fixed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
