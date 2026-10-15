import { chromium } from "playwright";
import { spawn } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";

const server = spawn("python", ["-m", "http.server", "8000", "--bind", "127.0.0.1"], {
  stdio: "ignore",
  cwd: process.cwd()
});
let browser;
try {
  await delay(800);
  browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    permissions: ["geolocation"],
    geolocation: { latitude: 53.3498, longitude: -6.2603 }
  });
  const page = await context.newPage();
  const names = [
    "Connolly", "Howth", "Pearse", "Bray", "Dún Laoghaire", "Malahide",
    "Blackrock", "Greystones", "Drogheda", "Cork", "Galway", "Limerick"
  ];
  const stationXml = `<?xml version="1.0"?><ArrayOfObjStation xmlns="http://api.irishrail.ie/realtime/">${names.map((name, i) => `<objStation><StationDesc>${name}</StationDesc><StationLatitude>${53.35 + i * 0.01}</StationLatitude><StationLongitude>${-6.26 + i * 0.01}</StationLongitude><StationCode>${i}</StationCode></objStation>`).join("")}</ArrayOfObjStation>`;
  const departureXml = `<?xml version="1.0"?><ArrayOfObjStationData xmlns="http://api.irishrail.ie/realtime/"><objStationData><Destination>Howth</Destination><Origin>Connolly</Origin><Status>On time</Status><Locationtype>O</Locationtype><Expdepart>15:35</Expdepart><Schdepart>15:35</Schdepart><Duein>5</Duein><Late>0</Late></objStationData></ArrayOfObjStationData>`;
  let connollyRequests = 0;
  await page.route("https://api.irishrail.ie/**", async route => {
    const url = new URL(route.request().url());
    if (url.pathname.endsWith("/getAllStationsXML")) {
      return route.fulfill({ status: 200, contentType: "application/xml", body: stationXml });
    }
    if (url.pathname.endsWith("/getStationDataByNameXML")) {
      if (url.searchParams.get("StationDesc") === "Connolly" && ++connollyRequests === 1) {
        return route.fulfill({ status: 502, contentType: "text/plain", body: "simulated upstream failure" });
      }
      return route.fulfill({ status: 200, contentType: "application/xml", body: departureXml });
    }
    return route.fulfill({ status: 404, body: "not found" });
  });

  await page.goto("http://127.0.0.1:8000", { waitUntil: "domcontentloaded" });
  await page.getByText("Official station directory loaded.").waitFor({ timeout: 5000 });

  // Check every anchor target; don't navigate away from the local test page.
  const links = await page.locator("a").evaluateAll(as => as.map(a => ({
    href: a.getAttribute("href"), target: a.getAttribute("target"), rel: a.getAttribute("rel")
  })));
  if (links.length < 3) throw new Error("Expected brand and donation links");
  for (const link of links) {
    if (!["./", "https://buymeacoffee.com/cican"].includes(link.href)) throw new Error("Unexpected anchor: " + link.href);
    if (link.href.startsWith("https://") && (link.target !== "_blank" || !link.rel?.includes("noopener") || !link.rel?.includes("noreferrer"))) {
      throw new Error("Donation link is not safely configured");
    }
  }

  // Hero actions and navigation targets.
  await page.getByRole("button", { name: /Plan journey/ }).first().click();
  await page.getByRole("heading", { name: "Plan a journey" }).waitFor();
  await page.getByRole("button", { name: /Departures/ }).click();
  await page.getByRole("heading", { name: "Find a station" }).waitFor();
  await page.getByRole("button", { name: /Near me/ }).first().click();
  await page.getByText(/Showing the closest stations/).waitFor({ timeout: 3000 });

  // Station search, clear, filters, saving, and the in-app departures/retry flow.
  const search = page.locator("#stationSearch");
  await search.fill("Connolly");
  await page.getByRole("button", { name: "Save Connolly" }).click();
  await page.getByRole("button", { name: "Saved", exact: true }).first().click();
  await page.getByRole("button", { name: "All stations" }).click();
  await page.locator("#clearSearch").click();
  await page.getByRole("button", { name: "Check departures for Connolly" }).click();
  await page.getByText("Live data could not be loaded in this browser. No times have been invented.").waitFor();
  await page.getByRole("button", { name: "Try again" }).click();
  await page.getByText("Irish Rail information · Connolly").waitFor();

  // Test the second dynamically generated station-time button and saved-stop actions.
  await search.fill("Pearse");
  await page.getByRole("button", { name: "Check departures for Pearse" }).click();
  await page.getByText("Irish Rail information · Pearse").waitFor();
  await page.getByRole("button", { name: "Clear station search" }).click();
  await page.getByRole("button", { name: "Saved", exact: true }).last().click();
  await page.getByRole("button", { name: "Find", exact: true }).first().click();
  await page.getByRole("button", { name: "Save Connolly" }).click();

  // Swap, form validation, valid route submission and all quick-route buttons.
  await page.locator("#fromStation").fill("Connolly");
  await page.locator("#toStation").fill("Howth");
  await page.getByRole("button", { name: "Swap starting station and destination" }).click();
  if (await page.locator("#fromStation").inputValue() !== "Howth") throw new Error("Swap button failed");
  await page.locator("#fromStation").fill("not a station");
  await page.locator("#toStation").fill("Howth");
  await page.getByRole("button", { name: "Go" }).click();
  await page.getByText("Choose a station from the suggestions.").waitFor();
  for (const routeName of ["Connolly → Howth", "Pearse → Bray", "Dún Laoghaire → Malahide"]) {
    await page.getByRole("button", { name: routeName, exact: true }).click();
    await page.getByRole("heading", { name: /→/ }).waitFor();
  }

  // Every bottom-navigation destination must remain reachable.
  for (const [name, heading] of [
    ["Home", "Your next train,"],
    ["Journey", "Plan a journey"],
    ["Stations", "Find a station"],
    ["Saved", "Saved stations"]
  ]) {
    await page.getByRole("button", { name, exact: true }).last().click();
    await page.getByRole("heading", { name: new RegExp(heading.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")) }).waitFor();
  }

  console.log("Browser smoke test passed: anchors, hero actions, navigation, geolocation, search, filters, clear, save/remove/find, departures/retry, swap, validation, submit, and all quick routes.");
} finally {
  if (browser) await browser.close();
  server.kill("SIGTERM");
}
