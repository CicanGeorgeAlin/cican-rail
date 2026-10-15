# CICAN RAIL

**Ireland's Railway Companion** — *Every station. Every journey. Ireland connected.*

CICAN RAIL is an independent, free-first railway information project starting with Dublin's DART and designed to expand across Ireland. Created by **CICAN GEORGE ALIN**.

## Current prototype
- Responsive static website.
- Search the initial DART corridor station directory.
- Save/remove favourite stations using browser local storage; no account required.
- Buy Me a Coffee support link.
- Clear disclosure that live departures and disruption alerts are not connected yet.

## Not implemented yet
Verified live departures, vehicle positions, service alerts, GPS/nearest station, walking directions, journey routing, notifications, offline timetables, ticketing and Android distribution.

## Product principle: premium-style features free
We will study public feature descriptions, user needs and publicly available reviews, then build original features using authorised data and open standards. We will not copy proprietary code, bypass paywalls, or misuse private APIs. Essential passenger information and planned premium-style convenience features should remain free wherever feasible.

## First milestones
1. Validate the initial station list against official data.
2. Register for NTA developer resources and document API access rules.
3. Verify available static and real-time feeds, licence, attribution, coverage, update cadence and request limits.
4. Build a data adapter that separates scheduled times from live estimates and marks stale/unavailable data.
5. Add a departure board and disruption notices; test against official information.
6. Add optional location, walking directions, saved journeys and reminders.
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