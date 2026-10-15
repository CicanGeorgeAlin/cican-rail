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
        return ET.fromstring(response.read())

def value(node, key):
    for child in node.iter():
        if child.tag.split("}")[-1].lower() == key.lower():
            return (child.text or "").strip()
    return ""

def main():
    stations_root = fetch(BASE + "/getAllStationsXML")
    station_nodes = [node for node in stations_root.iter() if node.tag.split("}")[-1] == "objStation"]
    if len(station_nodes) < 10:
        raise SystemExit(f"FAIL: official station directory returned only {len(station_nodes)} stations")
    print(f"PASS: official station directory returned {len(station_nodes)} stations")

    connolly_names = list(dict.fromkeys(value(node, "StationDesc") for node in station_nodes if "connolly" in value(node, "StationDesc").lower()))
    if not connolly_names:
        raise SystemExit("FAIL: official station directory contains no Connolly station")
    print("Connolly station names from official directory:", ", ".join(connolly_names))

    last_count = 0
    for station_name in connolly_names:
        query = urlencode({"StationDesc": station_name, "NumMins": "90"})
        departures_root = fetch(BASE + "/getStationDataByNameXML_withNumMins?" + query)
        records = [node for node in departures_root.iter() if node.tag.split("}")[-1] == "objStationData"]
        last_count = max(last_count, len(records))
        usable = [node for node in records if any(value(node, key) not in ("", "00:00") for key in ("Expdepart", "Exparrival", "Schdepart", "Scharrival")) or value(node, "Duein").isdigit()]
        if usable:
            print(f"PASS: official {station_name} feed returned {len(records)} records; {len(usable)} have a usable time field")
            for node in usable[:3]:
                print("  ", value(node, "Stationfullname") or station_name, "|", value(node, "Destination") or "destination unavailable",
                      "| expected departure", value(node, "Expdepart") or "—",
                      "| scheduled departure", value(node, "Schdepart") or "—",
                      "| due in", value(node, "Duein") or "—")
            return
    raise SystemExit(f"FAIL: official Connolly feed returned no usable train times across names {connolly_names}; maximum records seen={last_count}")

if __name__ == "__main__":
    main()
