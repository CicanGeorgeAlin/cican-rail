from pathlib import Path
import json
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch
from io import BytesIO

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from download_gtfs import download_and_validate  # noqa: E402


VALID_FILES = {
    "agency.txt": "agency_id,agency_name,agency_url,agency_timezone\nIR,Irish Rail,https://www.irishrail.ie,Europe/Dublin\n",
    "routes.txt": "route_id,agency_id,route_short_name,route_type\nDART,IR,DART,2\n",
    "trips.txt": "route_id,service_id,trip_id\nDART,WKD,T1\n",
    "stops.txt": "stop_id,stop_name\nCONN,Connolly\nPEAR,Pearse\n",
    "stop_times.txt": "trip_id,arrival_time,departure_time,stop_id,stop_sequence\nT1,08:00:00,08:00:00,CONN,1\nT1,08:05:00,08:05:00,PEAR,2\n",
    "calendar.txt": "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\nWKD,1,1,1,1,1,0,0,20260101,20271231\n",
    "calendar_dates.txt": "service_id,date,exception_type\n",
}


def make_feed_bytes(files):
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return stream.getvalue()


class FakeResponse:
    status = 200

    def __init__(self, content):
        self.stream = BytesIO(content)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stream.close()

    def read(self, size=-1):
        return self.stream.read(size)


class DownloadGtfsTests(unittest.TestCase):
    def test_downloads_validates_and_writes_manifest(self):
        payload = make_feed_bytes(VALID_FILES)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "build" / "GTFS_All.zip"
            with patch("download_gtfs.urlopen", return_value=FakeResponse(payload)):
                manifest = download_and_validate("https://example.test/feed.zip", output)
            self.assertEqual(output.read_bytes(), payload)
            manifest_path = Path(str(output) + ".manifest.json")
            saved = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["sha256"], manifest["sha256"])
            self.assertEqual(saved["validation"], "passed_structural_checks")
            self.assertEqual(saved["counts"]["trips"], 1)
            self.assertEqual(saved["source_url"], "https://example.test/feed.zip")

    def test_rejects_invalid_feed_without_replacing_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "GTFS_All.zip"
            output.write_bytes(b"keep-existing-file")
            with patch("download_gtfs.urlopen", return_value=FakeResponse(b"not a zip")):
                with self.assertRaises(ValueError):
                    download_and_validate("https://example.test/bad.zip", output)
            self.assertEqual(output.read_bytes(), b"keep-existing-file")
            self.assertFalse(Path(str(output) + ".manifest.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
