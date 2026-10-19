import json
import tempfile
import unittest
from pathlib import Path

from twitter_spark.gui import load_result_summary, powershell_command, predict_interactive, validate_sample_fraction


class GuiHelperTests(unittest.TestCase):
    def test_predict_interactive_sentiment(self):
        res_pos = predict_interactive(input_str="I love this amazing spark pipeline!")
        self.assertEqual(res_pos["prediction"], 1)
        self.assertIn("Tích cực", res_pos["label"])
        self.assertGreater(res_pos["confidence"], 0.7)

        res_neg = predict_interactive(input_str="I hate waiting in traffic so much, worst day ever.")
        self.assertEqual(res_neg["prediction"], 0)
        self.assertIn("Tiêu cực", res_neg["label"])
        self.assertGreater(res_neg["confidence"], 0.7)

    def test_validates_sample_fraction(self):
        self.assertEqual(validate_sample_fraction("0.10"), 0.10)
        self.assertEqual(validate_sample_fraction("1"), 1.0)
        with self.assertRaises(ValueError):
            validate_sample_fraction("0")
        with self.assertRaises(ValueError):
            validate_sample_fraction("abc")

    def test_builds_safe_powershell_argument_list(self):
        command = powershell_command("run_full.ps1", "-DataPath", r"D:\data folder\input.csv")
        self.assertEqual(command[:5], ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File"])
        self.assertEqual(command[-2:], ["-DataPath", r"D:\data folder\input.csv"])

    def test_loads_result_cards(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outputs = root / "outputs"
            outputs.mkdir()
            (outputs / "data_quality.json").write_text(
                json.dumps({"source": "data/demo/input.csv", "raw_rows": 100, "clean_rows": 95}),
                encoding="utf-8",
            )
            (outputs / "evaluation.json").write_text(
                json.dumps({"test_results": {"tfidf_logistic_regression": {"macro_f1": 0.875}}}),
                encoding="utf-8",
            )
            result = load_result_summary(root)
            self.assertEqual(result["raw_rows"], "100")
            self.assertEqual(result["clean_rows"], "95")
            self.assertEqual(result["macro_f1"], "0.8750")
            self.assertEqual(result["result_type"], "Dữ liệu demo")


if __name__ == "__main__":
    unittest.main()
