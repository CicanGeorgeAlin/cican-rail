from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")


class RailAppSmokeTests(unittest.TestCase):
    def test_document_has_mobile_viewport_and_cican_rail_brand(self):
        self.assertIn('<meta name="viewport"', HTML)
        self.assertIn("<title>CICAN RAIL", HTML)
        self.assertIn('name="theme-color" content="#f5f6fa"', HTML)
        self.assertIn('id="home"', HTML)

    def test_minimal_homepage_and_free_core_tools(self):
        self.assertIn("Your next train,", HTML)
        self.assertIn("FREE · IRELAND", HTML)
        self.assertIn("Free core tools", HTML)
        self.assertNotIn("A calmer way to commute", HTML)
        self.assertNotIn("Your local network", HTML)

    def test_station_search_and_results_exist(self):
        self.assertIn('id="stationSearch"', HTML)
        self.assertIn('id="stationResults"', HTML)
        self.assertIn("function renderStations()", HTML)
        self.assertIn("function loadStationDirectory()", HTML)
        self.assertIn("getAllStationsXML", HTML)

    def test_route_planner_validates_stations_and_opens_transit_directions(self):
        self.assertIn('id="journeyForm"', HTML)
        self.assertIn('id="fromStation"', HTML)
        self.assertIn('id="toStation"', HTML)
        self.assertIn('id="plannerMessage"', HTML)
        self.assertIn("Choose a station from the suggestions.", HTML)
        self.assertIn("Choose two different stations.", HTML)
        self.assertIn("https://www.google.com/maps/dir/?api=1", HTML)
        self.assertIn('data-route="Connolly|Howth"', HTML)

    def test_favourites_are_local_and_migrate_old_storage(self):
        self.assertIn("cicanrail.favourites.v1", HTML)
        self.assertIn("trackline.favourites.v1", HTML)
        self.assertIn("function renderFavorites()", HTML)
        self.assertIn("localStorage", HTML)

    def test_departures_use_official_feed_and_fail_honestly(self):
        self.assertIn("function loadDepartures(stationName,card)", HTML)
        self.assertIn("api.irishrail.ie/realtime/realtime.asmx", HTML)
        self.assertIn("No times have been invented", HTML)
        self.assertIn("Duein", HTML)
        self.assertIn("Estimated and scheduled times are not guarantees", HTML)

    def test_official_operator_links_and_independence_disclosure_exist(self):
        self.assertIn("https://www.irishrail.ie/", HTML)
        self.assertIn("https://www.transportforireland.ie/available-apps/tfi-live/", HTML)
        self.assertIn("Independent project", HTML)

    def test_forbidden_project_word_is_absent(self):
        self.assertIsNone(re.search(r"\bblink\b", HTML, flags=re.IGNORECASE))

    def test_required_dart_stations_exist_in_fallback_directory(self):
        for station in ("Connolly", "Pearse", "Dún Laoghaire", "Howth", "Bray"):
            self.assertIn(f'"{station}"', HTML)


if __name__ == "__main__":
    unittest.main(verbosity=2)
