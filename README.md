# CICAN RAIL

**Ireland's Railway Companion** — *Every station. Every journey. Ireland connected.*

CICAN RAIL is an independent, free-first railway information project starting with Dublin's DART and designed to expand across Ireland. Created by **CICAN GEORGE ALIN**.

## Current prototype
- Responsive static website.
- Search the initial DART corridor station directory.
- Save/remove favourite stations using browser local storage; no account required.
- Buy Me a Coffee support link.
- Official Irish Rail station directory and an in-app request for station departure data (live browser/API access still requires real-device verification).
- Journey search now stays in CICAN RAIL: it displays departures for the starting station when the official feed responds, and offers Google Maps as an optional external route fallback.
- Saved stations remain on the device; no account required.

## Not implemented yet
A complete native station-to-station timetable/route engine, verified browser access to live departures, NTA GTFS-Realtime integration, vehicle positions, service alerts, walking directions, notifications, offline timetables, ticketing and Android distribution.

## Product principle: premium-style features free
We will study public feature descriptions, user needs and publicly available reviews, then build original features using authorised data and open standards. We will not copy proprietary code, bypass paywalls, or misuse private APIs. Essential passenger information and planned premium-style convenience features should remain free wherever feasible.

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