from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")


class CicanRailSmokeTests(unittest.TestCase):
    def test_document_has_mobile_viewport_and_title(self):
        self.assertIn('<meta name="viewport"', HTML)
        self.assertIn("<title>CICAN RAIL", HTML)

    def test_station_search_and_results_exist(self):
        self.assertIn('id="stationSearch"', HTML)
        self.assertIn('id="stationResults"', HTML)
        self.assertIn('function renderStations()', HTML)

    def test_favourites_are_local_and_account_free(self):
        self.assertIn("cicanRail.favourites.v1", HTML)
        self.assertIn("function renderFavorites()", HTML)
        self.assertIn("localStorage", HTML)

    def test_departure_lookup_is_explicitly_experimental(self):
        self.assertIn("function loadDepartures(stationName,card)", HTML)
        self.assertIn("api.irishrail.ie/realtime/realtime.asmx", HTML)
        self.assertIn("No times have been invented", HTML)
        self.assertIn("Live departures are experimental.", HTML)

    def test_support_link_and_project_disclosure_exist(self):
        self.assertIn("https://buymeacoffee.com/cican", HTML)
        self.assertIn("Your next stop, made simpler.", HTML)
        self.assertIn("not affiliated with or endorsed by", HTML)

    def test_forbidden_project_word_is_absent(self):
        self.assertIsNone(re.search(r"\bblink\b", HTML, flags=re.IGNORECASE))

    def test_required_dart_stations_exist(self):
        for station in ("Connolly", "Pearse", "Dún Laoghaire", "Howth", "Bray"):
            self.assertIn(f'"{station}"', HTML)


if __name__ == "__main__":
    unittest.main(verbosity=2)
