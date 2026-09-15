import csv
import tempfile
import unittest
from pathlib import Path

from twitter_spark.demo_data import generate_demo_csv


class DemoDataTests(unittest.TestCase):
    def test_demo_csv_has_six_columns_and_both_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "demo.csv"
            count = generate_demo_csv(path, rows=120)
            with path.open(encoding="ISO-8859-1", newline="") as handle:
                rows = list(csv.reader(handle))
            self.assertEqual(len(rows), count)
            self.assertTrue(all(len(row) == 6 for row in rows))
            self.assertEqual({row[0] for row in rows}, {"0", "4"})

    def test_rejects_too_few_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                generate_demo_csv(Path(directory) / "demo.csv", rows=50)


if __name__ == "__main__":
    unittest.main()

