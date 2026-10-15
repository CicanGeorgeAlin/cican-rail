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
    "agency.txt": {"agency_name", "agency_url", "agency_timezone"},
    # GTFS allows agency_id to be omitted when the feed has only one agency.
    "routes.txt": {"route_id", "route_type"},
    "trips.txt": {"route_id", "service_id", "trip_id"},
    "stops.txt": {"stop_id", "stop_name"},
    "stop_times.txt": {"trip_id", "stop_id", "stop_sequence", "departure_time", "arrival_time"},
}


@dataclass
class FeedReport:
    files: dict[str, list[dict[str, str]]]
    errors: list[str]
    warnings: list[str]


def _read_csv(archive: zipfile.ZipFile, name: str, required_columns: set[str] | None = None) -> list[dict[str, str]]:
    try:
        raw = archive.read(name).decode("utf-8-sig")
    except KeyError as exc:
        raise ValueError(f"Missing required GTFS file: {name}") from exc
    reader = csv.DictReader(io.StringIO(raw))
    headers = set(reader.fieldnames or [])
    missing = (required_columns if required_columns is not None else REQUIRED_COLUMNS[name]) - headers
    if missing:
        raise ValueError(f"{name} is missing required columns: {', '.join(sorted(missing))}")
    return list(reader)


def _duplicates(rows: list[dict[str, str]], field: str) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for row in rows:
        value = row.get(field, "").strip()
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def validate_gtfs(path: str | Path) -> FeedReport:
    errors: list[str] = []
    warnings: list[str] = []
    files: dict[str, list[dict[str, str]]] = {}
    try:
        with zipfile.ZipFile(path) as archive:
            # GTFS ZIPs may place files in a single top-level directory.
            members = {name: name for name in archive.namelist() if not name.endswith("/")}
            by_basename: dict[str, list[str]] = {}
            for member in members:
                by_basename.setdefault(member.rsplit("/", 1)[-1], []).append(member)
            for name in REQUIRED_COLUMNS:
                if name not in by_basename:
                    errors.append(f"Missing required GTFS file: {name}")
            calendar_names = {"calendar.txt", "calendar_dates.txt"}
            present_calendars = calendar_names & set(by_basename)
            if not present_calendars:
                errors.append("GTFS must include calendar.txt, calendar_dates.txt, or both")
            if errors:
                return FeedReport(files, errors, warnings)

            def archive_name(basename: str) -> str:
                matches = by_basename.get(basename, [])
                if len(matches) != 1:
                    raise ValueError(f"Expected exactly one {basename}; found {len(matches)}")
                return matches[0]

            for name in REQUIRED_COLUMNS:
                try:
                    files[name] = _read_csv(archive, archive_name(name))
                except (ValueError, UnicodeDecodeError) as exc:
                    errors.append(str(exc))
            calendar_columns = {
                "calendar.txt": {"service_id", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "start_date", "end_date"},
                "calendar_dates.txt": {"service_id", "date", "exception_type"},
            }
            for name in present_calendars:
                try:
                    files[name] = _read_csv(archive, archive_name(name), calendar_columns[name])
                except (ValueError, UnicodeDecodeError) as exc:
                    errors.append(str(exc))
    except (OSError, zipfile.BadZipFile) as exc:
        return FeedReport({}, [f"Cannot read GTFS ZIP: {exc}"], [])

    if errors:
        return FeedReport(files, errors, warnings)

    for name in REQUIRED_COLUMNS:
        if not files[name]:
            errors.append(f"{name} contains no data rows")
    if "calendar.txt" in files and not files["calendar.txt"] and not files.get("calendar_dates.txt"):
        errors.append("calendar.txt contains no service rows and calendar_dates.txt defines no services")

    agencies = files["agency.txt"]
    routes = files["routes.txt"]
    trips = files["trips.txt"]
    stops = files["stops.txt"]
    times = files["stop_times.txt"]
    services = {row["service_id"] for row in files.get("calendar.txt", [])}
    services.update(row["service_id"] for row in files.get("calendar_dates.txt", []))
    route_ids = {row["route_id"] for row in routes}
    trip_ids = {row["trip_id"] for row in trips}
    stop_ids = {row["stop_id"] for row in stops}
    agency_ids = {row.get("agency_id", "").strip() for row in agencies if row.get("agency_id", "").strip()}

    if not any(row.get("route_short_name", "").strip() or row.get("route_long_name", "").strip() for row in routes):
        errors.append("routes.txt must include route_short_name or route_long_name values")
    if len(agencies) > 1 and (not agency_ids or any(not row.get("agency_id", "").strip() for row in agencies)):
        errors.append("agency_id is required for every row when agency.txt has multiple agencies")
    if len(agencies) > 1 and any(not row.get("agency_id", "").strip() for row in routes):
        errors.append("routes.txt must include agency_id when agency.txt has multiple agencies")

    for filename, rows, field in (
        ("agency.txt", agencies, "agency_id"),
        ("routes.txt", routes, "route_id"),
        ("trips.txt", trips, "trip_id"),
        ("stops.txt", stops, "stop_id"),
    ):
        duplicates = _duplicates(rows, field)
        if duplicates:
            errors.append(f"{filename} contains duplicate {field} values: {', '.join(sorted(duplicates)[:5])}")

    for row in routes:
        agency_id = row.get("agency_id", "").strip()
        if agency_id and agency_id not in agency_ids:
            errors.append(f"Route {row['route_id']} references missing agency {agency_id}")

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
        try:
            int(row["stop_sequence"])
        except (ValueError, TypeError):
            errors.append(f"stop_times for trip {row['trip_id']} has invalid stop_sequence {row.get('stop_sequence', '')!r}")

    rail_routes = sum(row["route_type"] == "2" for row in routes)
    warnings.append(f"Found {len(routes)} routes, {len(trips)} trips, {len(stops)} stops, and {len(times)} stop-time rows; rail routes: {rail_routes}.")
    warnings.append("Structural validation only: check feed date, rail coverage, licence, attribution and matching realtime version before production use.")
    if not services:
        errors.append("No service IDs found in calendar.txt or calendar_dates.txt")
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
