from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_gtfs import validate_gtfs  # noqa: E402


VALID_FILES = {
    "agency.txt": "agency_name,agency_url,agency_timezone\nIrish Rail,https://www.irishrail.ie,Europe/Dublin\n",
    "routes.txt": "route_id,agency_id,route_type\nDART,IR,2\n",
    "trips.txt": "route_id,service_id,trip_id\nDART,WKD,T1\n",
    "stops.txt": "stop_id,stop_name\nCONN,Connolly\nPEAR,Pearse\n",
    "stop_times.txt": "trip_id,arrival_time,departure_time,stop_id,stop_sequence\nT1,08:00:00,08:00:00,CONN,1\nT1,08:05:00,08:05:00,PEAR,2\n",
    "calendar.txt": "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\nWKD,1,1,1,1,1,0,0,20260101,20271231\n",
    "calendar_dates.txt": "service_id,date,exception_type\n",
}


class GtfsValidatorTests(unittest.TestCase):
    def make_zip(self, directory, files):
        path = Path(directory) / "feed.zip"
        with zipfile.ZipFile(path, "w") as archive:
            for name, content in files.items():
                archive.writestr(name, content)
        return path

    def test_accepts_structurally_valid_rail_feed(self):
        with tempfile.TemporaryDirectory() as directory:
            report = validate_gtfs(self.make_zip(directory, VALID_FILES))
        self.assertEqual(report.errors, [])
        self.assertTrue(any("rail routes: 1" in message for message in report.warnings))

    def test_accepts_calendar_dates_only_feed(self):
        files = dict(VALID_FILES)
        del files["calendar.txt"]
        files["calendar_dates.txt"] = "service_id,date,exception_type\nWKD,20261015,1\n"
        with tempfile.TemporaryDirectory() as directory:
            report = validate_gtfs(self.make_zip(directory, files))
        self.assertEqual(report.errors, [])

    def test_accepts_calendar_only_feed_without_exceptions_file(self):
        files = dict(VALID_FILES)
        del files["calendar_dates.txt"]
        with tempfile.TemporaryDirectory() as directory:
            report = validate_gtfs(self.make_zip(directory, files))
        self.assertEqual(report.errors, [])

    def test_requires_at_least_one_service_calendar_file(self):
        files = dict(VALID_FILES)
        del files["calendar.txt"]
        del files["calendar_dates.txt"]
        with tempfile.TemporaryDirectory() as directory:
            report = validate_gtfs(self.make_zip(directory, files))
        self.assertTrue(any("must include calendar.txt, calendar_dates.txt, or both" in e for e in report.errors))

    def test_reports_missing_required_file(self):
        files = dict(VALID_FILES)
        del files["stop_times.txt"]
        with tempfile.TemporaryDirectory() as directory:
            report = validate_gtfs(self.make_zip(directory, files))
        self.assertTrue(any("Missing required GTFS file: stop_times.txt" in e for e in report.errors))

    def test_reports_dangling_trip_and_stop_references(self):
        files = dict(VALID_FILES)
        files["stop_times.txt"] = "trip_id,arrival_time,departure_time,stop_id,stop_sequence\nMISSING,08:00:00,08:00:00,UNKNOWN,1\n"
        with tempfile.TemporaryDirectory() as directory:
            report = validate_gtfs(self.make_zip(directory, files))
        self.assertTrue(any("missing trip MISSING" in e for e in report.errors))
        self.assertTrue(any("missing stop UNKNOWN" in e for e in report.errors))

    def test_rejects_unreadable_zip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.zip"
            path.write_text("not a zip", encoding="utf-8")
            report = validate_gtfs(path)
        self.assertTrue(any("Cannot read GTFS ZIP" in e for e in report.errors))


if __name__ == "__main__":
    unittest.main(verbosity=2)
