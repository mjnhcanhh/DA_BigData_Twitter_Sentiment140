from pathlib import Path
import unittest

from twitter_spark.report_filler import build_replacement_dict, populate_report


class ReportFillerTests(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(__file__).resolve().parents[1]
        self.outputs_dir = self.project_root / "outputs"
        self.template_path = self.project_root / "report" / "bao_cao_cuoi_ky_template.md"

    def test_build_replacement_dict(self):
        replacements = build_replacement_dict(self.outputs_dir)
        self.assertIn("RAW_ROWS", replacements)
        self.assertIn("CLEAN_ROWS", replacements)
        self.assertIn("LR_ACCURACY", replacements)
        self.assertIn("LR_MACRO_F1", replacements)
        self.assertGreater(int(replacements["RAW_ROWS"].replace(",", "")), 0)
        self.assertGreater(int(replacements["CLEAN_ROWS"].replace(",", "")), 0)

    def test_populate_report_no_missing_keys(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            filled_count, missing = populate_report(
                self.template_path, tmp_path, self.outputs_dir
            )
            self.assertGreater(filled_count, 50)
            self.assertEqual(missing, [], f"Missing template keys: {missing}")
            content = tmp_path.read_text(encoding="utf-8")
            self.assertNotIn("{{RAW_ROWS}}", content)
            self.assertNotIn("{{CLEAN_ROWS}}", content)
        finally:
            if tmp_path.is_file():
                tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()

