# CICAN RAIL — Data Source Register

This register records the initial sources to verify before any real-time transport feature is released. Access, licences and technical behaviour must be rechecked during implementation.

## National Transport Authority (NTA)
- Developer portal: https://developer.nationaltransport.ie/
- Fair usage policy: https://developer.nationaltransport.ie/usagepolicy
- Purpose: Irish public transport schedule/stop datasets and GTFS-Realtime resources, subject to registration, API keys, access terms and usage limits.
- Important current portal notice: a newer v2 GTFS-Realtime API is available. Verify which API version and schema we use before integration.
- The published fair-use policy states that NTA GTFS data is CC BY 4.0 and requires attribution. It also describes token-based access and a once-per-60-seconds restriction for each token's GTFS-Realtime calls. Confirm current policy and exact limits at the time of implementation.
- Required attribution: identify NTA, link the source, and state that the data is provided as-is and NTA is not responsible for errors or inaccuracies.

## Iarnród Éireann / Irish Rail
- Official website: https://www.irishrail.ie/
- Official timetables: https://www.irishrail.ie/en-ie/train-timetables/timetables-by-route
- Real-time service endpoint published by NTA portal: https://api.irishrail.ie/realtime/realtime.asmx
- Purpose: verify official railway timetable information and investigate live railway data. Do not assume endpoint availability, completeness, CORS access, permitted caching, or production suitability until tested and terms are confirmed.

## Google Maps Platform
- Transit route documentation: https://developers.google.com/maps/documentation/routes/transit-route
- Purpose: optional map display and supported walking/transit route calculations.
- Before use: check Ireland coverage, current pricing, billing requirements, attribution, storage restrictions, quotas and API key security. Google Maps is not our authoritative source for Irish Rail live running status.

## Other mapping option to evaluate
- OpenStreetMap: https://www.openstreetmap.org/
- Before use: choose a suitable tile/routing provider and comply with attribution, tile usage policies, rate limits and provider-specific terms. Do not assume the public tile service is a free unlimited production backend.

## Integration checklist
For each feed, record:
- Owner and canonical documentation URL.
- Registration and authentication requirements.
- Licence, attribution and reuse restrictions.
- Static or real-time data; exact fields and schema version.
- Coverage: DART, commuter, InterCity, cross-border where applicable.
- Update cadence, request limits, cache rules and outage behaviour.
- Last checked date and a reproducible smoke-test procedure.

## Product integrity rules
- Never fabricate a departure, delay, cancellation, platform or vehicle position.
- Distinguish scheduled time from estimated real-time time.
- Show when data was updated and flag stale/unavailable feeds.
- Avoid exposing credentials in public client-side code or repository history.
- Keep user location optional and request it only when the user invokes a location feature.