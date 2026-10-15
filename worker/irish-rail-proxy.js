/**
 * CICAN RAIL — narrow CORS proxy for the official Irish Rail realtime XML API.
 * Deploy as a Cloudflare Worker; see worker/README.md.
 */
const UPSTREAM = "https://api.irishrail.ie/realtime/realtime.asmx";
const ALLOWED_ORIGINS = new Set([
  "https://cicangeorgealin.github.io",
  "http://localhost:8000",
  "http://127.0.0.1:8000"
]);
const OPERATIONS = new Set(["getAllStationsXML", "getStationDataByNameXML"]);

function corsHeaders(origin) {
  return {
    "Access-Control-Allow-Origin": ALLOWED_ORIGINS.has(origin) ? origin : "https://cicangeorgealin.github.io",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Accept, Content-Type",
    "Vary": "Origin",
    "X-Content-Type-Options": "nosniff"
  };
}

function respond(body, status, origin, extra = {}) {
  return new Response(body, {
    status,
    headers: {
      ...corsHeaders(origin),
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      ...extra
    }
  });
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }
    if (request.method !== "GET") {
      return respond(JSON.stringify({ error: "Method not allowed" }), 405, origin, { Allow: "GET, OPTIONS" });
    }
    if (origin && !ALLOWED_ORIGINS.has(origin)) {
      return respond(JSON.stringify({ error: "Origin not allowed" }), 403, origin);
    }

    const operation = url.pathname.replace(/^\/+|\/+$/g, "");
    if (!OPERATIONS.has(operation)) {
      return respond(JSON.stringify({ error: "Endpoint not allowed" }), 404, origin);
    }

    const upstream = new URL(UPSTREAM + "/" + operation);
    let ttl = 0;
    if (operation === "getStationDataByNameXML") {
      const station = (url.searchParams.get("StationDesc") || "").trim();
      const minutesRaw = url.searchParams.get("NumMins") || "90";
      const minutes = Number(minutesRaw);
      if (!station || station.length > 100 || /[\u0000-\u001f]/.test(station)) {
        return respond(JSON.stringify({ error: "A valid StationDesc is required" }), 400, origin);
      }
      if (!Number.isInteger(minutes) || minutes < 5 || minutes > 90) {
        return respond(JSON.stringify({ error: "NumMins must be an integer from 5 to 90" }), 400, origin);
      }
      upstream.searchParams.set("StationDesc", station);
      upstream.searchParams.set("NumMins", String(minutes));
      ttl = 8;
    } else {
      ttl = 3600;
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);
    try {
      const response = await fetch(upstream.toString(), {
        method: "GET",
        headers: { Accept: "application/xml, text/xml" },
        signal: controller.signal,
        cf: ttl ? { cacheTtl: ttl, cacheEverything: true } : undefined
      });
      if (!response.ok) {
        return respond(JSON.stringify({ error: "Irish Rail service returned an error", upstreamStatus: response.status }), 502, origin);
      }
      const body = await response.text();
      if (!body || !body.includes("<")) {
        return respond(JSON.stringify({ error: "Irish Rail returned an unexpected response" }), 502, origin);
      }
      return new Response(body, {
        status: 200,
        headers: {
          ...corsHeaders(origin),
          "Content-Type": "application/xml; charset=utf-8",
          "Cache-Control": ttl ? "public, max-age=" + ttl : "no-store"
        }
      });
    } catch (error) {
      const isTimeout = error && error.name === "AbortError";
      return respond(JSON.stringify({ error: isTimeout ? "Irish Rail request timed out" : "Irish Rail service is unavailable" }), 502, origin);
    } finally {
      clearTimeout(timeout);
    }
  }
};
