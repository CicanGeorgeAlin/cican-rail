from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")


class RailAppSmokeTests(unittest.TestCase):
    def test_document_has_mobile_viewport_and_cican_rail_brand(self):
        self.assertIn('<meta name="viewport"', HTML)
        self.assertIn("<title>CICAN RAIL", HTML)
        self.assertIn('name="theme-color" content="#f5f8f5"', HTML)
        self.assertIn('id="home"', HTML)
        self.assertIn('id="journeySection"', HTML)
        self.assertIn('id="heroNearMe"', HTML)
        self.assertIn('id="heroDepartures"', HTML)
        self.assertIn('id="heroJourney"', HTML)
        self.assertIn('data-target="journeySection"', HTML)
        self.assertIn('grid-template-columns:repeat(4,1fr)', HTML)

    def test_minimal_homepage_and_free_core_tools(self):
        self.assertIn("Your next train,", HTML)
        self.assertIn("--teal:#00843d", HTML)
        self.assertIn("--lime:#f4d35e", HTML)
        self.assertIn("FREE CORE TOOLS", HTML)
        self.assertIn("Free core tools", HTML)
        self.assertNotIn("A calmer way to commute", HTML)
        self.assertNotIn("Your local network", HTML)
        self.assertNotIn("Trackline", HTML)

    def test_simple_free_core_and_optional_donation_are_visible(self):
        self.assertNotIn("Powerful features. Free by design.", HTML)
        self.assertNotIn("Planned free essentials", HTML)
        self.assertIn('href="https://buymeacoffee.com/cican"', HTML)
        self.assertIn("No feature is unlocked by donating.", HTML)
        self.assertIn("FREE CORE TOOLS", HTML)

    def test_station_search_and_results_exist(self):
        self.assertIn('id="stationSearch"', HTML)
        self.assertIn('id="stationResults"', HTML)
        self.assertIn("function renderStations()", HTML)
        self.assertIn("function loadStationDirectory()", HTML)
        self.assertIn("getAllStationsXML", HTML)
        self.assertIn("StationLatitude", HTML)
        self.assertIn("StationLongitude", HTML)
        self.assertIn('id="stationFeedStatus"', HTML)
        self.assertIn("Official station directory loaded.", HTML)
        self.assertIn("Using the built-in station list; official refresh is unavailable right now.", HTML)
        self.assertIn('id="nearMe"', HTML)
        self.assertIn("navigator.geolocation.getCurrentPosition", HTML)
        self.assertIn("Your location stays on this device", HTML)
        self.assertIn("Nearby stations are unavailable because station coordinates could not be loaded.", HTML)
        self.assertIn("Nearby stations are unavailable. Search by station name instead.", HTML)
        self.assertIn('stationDirectoryStatus="loading"', HTML)
        self.assertIn('stationDirectoryStatus="fallback"', HTML)

    def test_route_planner_validates_stations_without_external_redirect(self):
        self.assertIn('id="journeyForm"', HTML)
        self.assertIn('id="fromStation"', HTML)
        self.assertIn('id="toStation"', HTML)
        self.assertIn('id="plannerMessage"', HTML)
        self.assertIn("Choose a station from the suggestions.", HTML)
        self.assertIn("Choose two different stations.", HTML)
        self.assertNotIn("https://www.google.com/maps/dir/?api=1", HTML)
        self.assertIn('id="journeyResults"', HTML)
        self.assertNotIn("view full route in Google Maps", HTML)
        self.assertIn("loadDepartures(from,journeyResults)", HTML)
        self.assertIn("not yet a complete station-to-station timetable", HTML)
        self.assertNotIn('window.open(url,"_blank","noopener,noreferrer")', HTML)
        self.assertIn('data-route="Connolly|Howth"', HTML)
        self.assertIn('document.getElementById("journeyForm").requestSubmit()', HTML)

    def test_favourites_are_local_and_migrate_old_storage(self):
        self.assertIn("cicanrail.favourites.v1", HTML)
        self.assertIn("trackline.favourites.v1", HTML)
        self.assertIn("function renderFavorites()", HTML)
        self.assertIn("localStorage", HTML)
        self.assertIn('value.filter(x=>typeof x==="string")', HTML)

    def test_departures_use_official_feed_and_fail_honestly(self):
        self.assertIn("function loadDepartures(stationName,card)", HTML)
        self.assertIn("api.irishrail.ie/realtime/realtime.asmx", HTML)
        self.assertIn("No times have been invented", HTML)
        self.assertIn('retry.textContent="Try again"', HTML)
        self.assertIn('retry.addEventListener("click",()=>{panel.remove();loadDepartures(stationName,card)})', HTML)
        self.assertIn("Duein", HTML)
        self.assertIn("item.localName||item.nodeName", HTML)
        self.assertIn("toLocaleLowerCase()===wanted", HTML)
        self.assertIn("Expdepart", HTML)
        self.assertIn("Locationtype", HTML)
        self.assertIn("Estimated and scheduled times are not guarantees", HTML)

    def test_empty_departure_feed_is_not_reported_as_a_generic_failure(self):
        self.assertIn("No train records were returned for this station.", HTML)
        self.assertIn("The feed may have no services listed in this window", HTML)
        self.assertNotIn("Check official Irish Rail information ↗", HTML)
        self.assertIn("Try again in a moment. No times have been invented.", HTML)

    def test_departure_request_is_aborted_after_timeout_and_timer_is_cleared(self):
        self.assertIn("const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),9000)", HTML)
        self.assertIn("fetch(url,{signal:controller.signal,headers:{Accept:\"application/xml, text/xml\"}})", HTML)
        self.assertIn(".finally(()=>clearTimeout(timeout))", HTML)

    def test_official_operator_links_and_independence_disclosure_exist(self):
        self.assertNotIn('href="https://www.irishrail.ie/"', HTML)
        self.assertNotIn('href="https://www.transportforireland.ie/available-apps/tfi-live/"', HTML)
        self.assertIn("Independent project", HTML)
        self.assertNotIn("Open official Irish Rail information ↗", HTML)
        self.assertNotIn('class="official-link"', HTML)
        self.assertIn('href="https://buymeacoffee.com/cican"', HTML)

    def test_optional_api_proxy_is_configurable_and_used_by_both_live_feeds(self):
        self.assertIn('<script src="./api-config.js"></script>', HTML)
        self.assertIn('window.CICAN_RAIL_API_BASE = ""', (ROOT / "api-config.js").read_text(encoding="utf-8"))
        self.assertIn('window.CICAN_RAIL_API_BASE||"https://api.irishrail.ie/realtime/realtime.asmx"', HTML)
        self.assertIn('IRISH_RAIL_API_BASE+"/getStationDataByNameXML?StationDesc="', HTML)
        self.assertIn('fetch(IRISH_RAIL_API_BASE+"/getAllStationsXML"', HTML)

    def test_primary_buttons_and_navigation_have_handlers(self):
        required_handlers = [
            'document.getElementById("heroNearMe").addEventListener("click"',
            'document.getElementById("heroDepartures").addEventListener("click"',
            'document.getElementById("heroJourney").addEventListener("click"',
            'document.getElementById("swapStations").addEventListener("click"',
            'document.getElementById("clearSearch").addEventListener("click"',
            'document.getElementById("nearMe").addEventListener("click"',
            'allFilter.addEventListener("click"',
            'savedFilter.addEventListener("click"',
            'document.querySelectorAll("[data-route]").forEach(button=>button.addEventListener("click"',
            'document.querySelectorAll(".nav-item").forEach(button=>button.addEventListener("click"',
            'departures.addEventListener("click",()=>loadDepartures(name,card))',
            'save.addEventListener("click",()=>toggleSaved(name))',
            'open.addEventListener("click",()=>{showSaved=false;search.value=name',
            'remove.addEventListener("click",()=>toggleSaved(name))',
        ]
        for handler in required_handlers:
            with self.subTest(handler=handler):
                self.assertIn(handler, HTML)
        for target in ("home", "journeySection", "stationsSection", "savedSection"):
            with self.subTest(target=target):
                self.assertIn(f'id="{target}"', HTML)
                self.assertIn(f'data-target="{target}"', HTML)

    def test_every_anchor_destination_is_expected_and_donation_opens_safely(self):
        anchors = re.findall(r'<a\\b([^>]*)href=["\\']([^"\\']+)["\\']([^>]*)>', HTML, flags=re.IGNORECASE)
        self.assertGreaterEqual(len(anchors), 3)
        destinations = [item[1] for item in anchors]
        self.assertIn("./", destinations)
        self.assertEqual(destinations.count("https://buymeacoffee.com/cican"), 2)
        self.assertTrue(all(href in ("./", "https://buymeacoffee.com/cican") for href in destinations))
        for before, href, after in anchors:
            if href.startswith("https://"):
                attrs = before + after
                self.assertIn('target="_blank"', attrs)
                self.assertIn('rel="noopener noreferrer"', attrs)

    def test_forbidden_project_word_is_absent(self):
        self.assertIsNone(re.search(r"\bblink\b", HTML, flags=re.IGNORECASE))

    def test_required_dart_stations_exist_in_fallback_directory(self):
        for station in ("Connolly", "Pearse", "Dún Laoghaire", "Howth", "Bray"):
            self.assertIn(f'"{station}"', HTML)


if __name__ == "__main__":
    unittest.main(verbosity=2)
