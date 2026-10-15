# CICAN RAIL API proxy

This small Cloudflare Worker safely proxies only the two official Irish Rail XML endpoints currently used by CICAN RAIL:
- `getAllStationsXML` — station directory and coordinates (cached for up to 1 hour)
- `getStationDataByNameXML` — station departure/arrival records (cached for up to 8 seconds)

It does not invent train times and does not provide a full journey planner. The upstream service remains the source of truth.

## Deploy (free-tier suitable)

1. Create/sign in to a Cloudflare account and install Wrangler, or use Cloudflare's browser editor.
2. From this folder run `npx wrangler login` and `npx wrangler deploy`.
3. Copy the deployed Worker URL, usually `https://cican-rail-api.<your-subdomain>.workers.dev`.
4. Edit `api-config.js` in the repository and set `window.CICAN_RAIL_API_BASE` to that URL (no trailing slash).
5. Commit and push. GitHub Pages will redeploy CICAN RAIL.
6. Test the Worker root (it should return a JSON 404 because only explicit API operations are allowed), then test:
   - `<worker-url>/getAllStationsXML`
   - `<worker-url>/getStationDataByNameXML?StationDesc=Connolly&NumMins=90`
7. Open the live site and test the station directory and a station's **Times** button.

The Worker allows the published GitHub Pages origin and local port 8000 for development. If you change the published domain, update `ALLOWED_ORIGINS` in `irish-rail-proxy.js`.

## Why this is needed

GitHub Pages hosts static files and cannot run a server-side proxy. Some browsers/network paths block direct cross-origin calls to the Irish Rail service. This Worker gives the browser a controlled CORS-enabled endpoint while keeping the upstream API and its XML data intact. No secret API key is embedded.

## Limitations

- The proxy fixes the browser-to-upstream access path only; it cannot guarantee upstream availability or accuracy.
- This does not add scheduled timetable routing, transfer planning, or a guarantee that a train serves the selected destination. Those require timetable data and route logic, separate from the real-time departures API.
