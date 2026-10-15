from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")


class RailAppSmokeTests(unittest.TestCase):
    def test_document_has_mobile_viewport_and_app_title(self):
        self.assertIn('<meta name="viewport"', HTML)
        self.assertIn("<title>Trackline", HTML)
        self.assertIn('name="theme-color" content="#f5f7f2"', HTML)

    def test_station_search_and_results_exist(self):
        self.assertIn('id="stationSearch"', HTML)
        self.assertIn('id="stationResults"', HTML)
        self.assertIn("function renderStations()", HTML)

    def test_route_planner_uses_station_options_and_transit_directions(self):
        self.assertIn('id="journeyForm"', HTML)
        self.assertIn('id="fromStation"', HTML)
        self.assertIn('id="toStation"', HTML)
        self.assertIn("https://www.google.com/maps/dir/?api=1", HTML)
        self.assertIn('data-route="Connolly|Howth"', HTML)

    def test_favourites_are_local_and_account_free(self):
        self.assertIn("trackline.favourites.v1", HTML)
        self.assertIn("function renderFavorites()", HTML)
        self.assertIn("localStorage", HTML)

    def test_departure_lookup_is_clearly_experimental_and_does_not_guess(self):
        self.assertIn("function loadDepartures(stationName,card)", HTML)
        self.assertIn("api.irishrail.ie/realtime/realtime.asmx", HTML)
        self.assertIn("No times have been invented", HTML)
        self.assertIn("departure lookup is experimental", HTML)

    def test_official_operator_links_and_project_disclosure_exist(self):
        self.assertIn("https://www.irishrail.ie/", HTML)
        self.assertIn("https://www.transportforireland.ie/available-apps/tfi-live/", HTML)
        self.assertIn("not affiliated with or endorsed by", HTML)

    def test_forbidden_project_word_is_absent(self):
        self.assertIsNone(re.search(r"\bblink\b", HTML, flags=re.IGNORECASE))

    def test_required_dart_stations_exist(self):
        for station in ("Connolly", "Pearse", "Dún Laoghaire", "Howth", "Bray"):
            self.assertIn(f'"{station}"', HTML)


if __name__ == "__main__":
    unittest.main(verbosity=2)
