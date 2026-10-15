# CICAN RAIL

**Ireland's Railway Companion** — *Every station. Every journey. Ireland connected.*

CICAN RAIL is an independent, free-first railway information project starting with Dublin's DART and designed to expand across Ireland. Created by **CICAN GEORGE ALIN**.

## Current prototype
- Responsive static website.
- Search the initial DART corridor station directory.
- Save/remove favourite stations using browser local storage; no account required.
- Visible, optional Buy Me a Coffee support link; donations unlock no features.
- Free-by-design feature roadmap that distinguishes prototype features from planned work.
- Official Irish Rail station directory and an in-app request for station departure data (live browser/API access still requires real-device verification).
- Journey search now stays in CICAN RAIL: it displays departures for the starting station when the official feed responds, and offers Google Maps as an optional external route fallback.
- Saved stations remain on the device; no account required.

## Not implemented yet
A complete native station-to-station timetable/route engine, verified browser access to live departures, NTA GTFS-Realtime integration, vehicle positions, service alerts, walking directions, notifications, offline timetables, ticketing and Android distribution.

## Product principle: premium-style features free
We will study public feature descriptions, user needs and publicly available reviews, then build original features using authorised data and open standards. We will not copy proprietary code, bypass paywalls, or misuse private APIs. Essential passenger information and planned premium-style convenience features should remain free wherever feasible.

## Free-by-design promise

CICAN RAIL aims to keep essential passenger features free: station search, saved stations/journeys, journey planning, departures and core service information. Planned convenience features such as alerts, offline access and richer journey tools are not presented as complete until implemented and tested. Optional donations at https://buymeacoffee.com/cican support development; they do not unlock features. We build original functionality and respect third-party data licences and terms rather than copying competitors’ proprietary code or bypassing paid services.

## First milestones
1. Verify live departures from a real mobile browser and document API/CORS behaviour.
2. Register for NTA developer resources and obtain a private API key for GTFS-Realtime where required.
3. Validate the static GTFS schedule feed, licence, attribution, coverage and update cadence.
4. Build a native route engine from verified schedule data, with transfers and service calendars handled correctly.
5. Combine scheduled times with live estimates and service alerts; mark stale or unavailable data.
6. Test all external links and keep essential station/departure information inside CICAN RAIL wherever data rights and reliability permit.
7. Expand verified coverage to the wider Irish passenger railway network.
8. Evaluate Android packaging and publication.

## Data integrity and safety rules
- Never invent train times, delays, cancellations, train positions or accessibility claims.
- Clearly label scheduled times, live estimates, last-updated timestamps and unavailable/stale feeds.
- Prefer official NTA and Irish Rail sources for Irish railway operations.
- Follow licences, attribution requirements, API terms, request limits and caching rules.
- Never expose private API credentials in frontend JavaScript or a public repository.
- Ask permission before using device location; always retain manual station search.
- Keep support donations optional and separate from essential features.
- Test each feature and deployed change before calling it complete.

## Links
- Website (after GitHub Pages is enabled): https://cicangeorgealin.github.io/cican-rail/
- Repository: https://github.com/CicanGeorgeAlin/cican-rail
- Support: https://buymeacoffee.com/cican
- Data source register: [DATA_SOURCES.md](DATA_SOURCES.md)

## Independence
CICAN RAIL is not affiliated with or endorsed by Iarnród Éireann, the National Transport Authority, Google or any other transport operator. Names are used only to identify relevant services and sources.

## GTFS schedule validation tool

Before using a downloaded NTA GTFS Schedule ZIP for route calculations, run the structural validator:

```bash
python scripts/validate_gtfs.py /path/to/GTFS_All.zip
```

The validator checks for core schedule files, required columns, and references between routes, trips, stops, stop times and service calendars. It reports errors and a summary of rail-route coverage. The test suite includes a small synthetic feed:

```bash
python -m unittest discover -s tests -p "*_test.py" -v
```

**Important:** passing structural checks does not prove that a feed is current, contains all Irish Rail services, is matched to a particular GTFS-Realtime version, or is ready for production. Verify the feed date, rail coverage, licence, attribution and update process before implementing journey calculations. The validator does not download any data or contain API credentials.
