"""Live integration check against the official Irish Rail real-time API."""
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

BASE = "https://api.irishrail.ie/realtime/realtime.asmx"
HEADERS = {"User-Agent": "CICAN-RAIL-live-smoke-test/1.0", "Accept": "application/xml, text/xml"}

def fetch(url):
    request = Request(url, headers=HEADERS)
    with urlopen(request, timeout=15) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status} from {url}")
        body = response.read()
    return ET.fromstring(body)

stations_root = fetch(BASE + "/getAllStationsXML")
station_nodes = [node for node in stations_root.iter() if node.tag.split("}")[-1] == "objStation"]
if len(station_nodes) < 10:
    raise SystemExit(f"FAIL: official station directory returned only {len(station_nodes)} stations")
print(f"PASS: official station directory returned {len(station_nodes)} stations")

query = urlencode({"StationDesc": "Connolly", "NumMins": "90"})
departures_root = fetch(BASE + "/getStationDataByNameXML_withNumMins?" + query)
records = [node for node in departures_root.iter() if node.tag.split("}")[-1] == "objStationData"]
if not records:
    raise SystemExit("FAIL: official Connolly API response was valid XML but contained no train records for the next 90 minutes")

def value(node, key):
    for child in node.iter():
        if child.tag.split("}")[-1].lower() == key.lower():
            return (child.text or "").strip()
    return ""

usable = [node for node in records if any(value(node, key) not in ("", "00:00") for key in ("Expdepart", "Exparrival", "Schdepart", "Scharrival")) or value(node, "Duein").isdigit()]
if not usable:
    raise SystemExit(f"FAIL: API returned {len(records)} records but no usable expected/scheduled time or due-in value")
print(f"PASS: official Connolly live feed returned {len(records)} train records; {len(usable)} have a usable time field")
for node in usable[:3]:
    print("  ", value(node, "Stationfullname") or "Connolly", "|", value(node, "Destination") or "destination unavailable",
          "| expected departure", value(node, "Expdepart") or "—",
          "| scheduled departure", value(node, "Schdepart") or "—",
          "| due in", value(node, "Duein") or "—")
