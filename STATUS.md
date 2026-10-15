# CICAN RAIL — implementation status
Last reviewed: 15 October 2026

This is a source-code and automated-test audit, not a claim that every live data source has been verified on a physical phone.

## Working in the current prototype

- Responsive, single-page web interface with mobile bottom navigation and reduced-motion support.
- Search stations by name from the bundled fallback list.
- Attempt to refresh the station directory and station coordinates from the official Irish Rail XML endpoint.
- Save and remove favourite stations in local browser storage; no account is required.
- Request device location only after the person presses “Find stations near me”.
- Sort nearby stations by distance when coordinates are available.
- Request departure data for a selected station from the Irish Rail real-time endpoint.
- Show a useful empty/error state and a retry action when departure data cannot be loaded.
- Validate station names before the planner form accepts a route.
- Offer an optional Google Maps transit route link; the website does not silently redirect users.
- Voluntary Buy Me a Coffee support link. Donations do not unlock features.
- Automated Python smoke tests and inline JavaScript syntax checks run in GitHub Actions.

## Present but dependent on external conditions

- Full station directory: depends on the official endpoint responding with parseable XML. The bundled list remains as a fallback.
- Nearby station results: require valid coordinates from the station feed; location permission is optional.
- Departure times: depend on browser network access, API availability, response shape and cross-origin policy. Automated static tests do not establish that this works in every browser or on every device.
- The displayed departure rows are a feed view, not a proof that each train reaches the user's selected destination.

## Not yet implemented / not verified

- A native station-to-station timetable search with a verified journey itinerary.
- Correct transfer search, interchange/walking times, service calendars and journey ranking.
- Production-verified live departures, delay handling, cancellations, disruption alerts and data freshness monitoring.
- NTA GTFS-Realtime integration with a registered key and the correct schema/version.
- Reliable nationwide route coverage from a current, validated static GTFS feed.
- Push notifications, saved journeys, timetable offline mode, live vehicle positions and accessibility data.
- A dedicated installable Android app or Play Store release.
- Real-device/browser checks for geolocation, API CORS, visual layout, keyboard/screen-reader use and actual outbound links.

## Free-first product promise

The target is to provide passenger essentials without a subscription: station search, saved stations and journeys, journey planning, departures, service information and useful alerts wherever authoritative data and operating costs permit. Premium-style convenience features are targets, not claims of current availability. Build original features, respect data licences and provider terms, and never invent train information. Donations at https://buymeacoffee.com/cican are optional and do not gate features.

## Current engineering gate

1. Keep the automated test suite green.
2. Verify the official station feed and departures from a real mobile browser, recording the actual outcome.
3. Obtain and validate a current NTA static GTFS feed and document feed date, coverage and attribution.
4. Implement a tested route engine against real schedule data before replacing the current honest planner explanation.
5. Integrate real-time data only after authentication, schema/version, rate limits, cache policy and secret handling are confirmed.
6. Add each extra free feature only when its data source and failure states are reliable.

## Useful links

- Website: https://cicangeorgealin.github.io/cican-rail/
- Source repository: https://github.com/CicanGeorgeAlin/cican-rail
- Automated tests: https://github.com/CicanGeorgeAlin/cican-rail/actions
- NTA developer portal: https://developer.nationaltransport.ie/
- Official Irish Rail: https://www.irishrail.ie/
- Optional support: https://buymeacoffee.com/cican
