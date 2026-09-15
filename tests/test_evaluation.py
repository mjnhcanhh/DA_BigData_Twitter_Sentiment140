import unittest

from twitter_spark.evaluation import metrics_from_cells


class MetricsTests(unittest.TestCase):
    def test_binary_metrics_and_confusion_orientation(self):
        metrics = metrics_from_cells({(0, 0): 8, (0, 1): 2, (1, 0): 1, (1, 1): 9})
        self.assertEqual(metrics["rows"], 20)
        self.assertAlmostEqual(metrics["accuracy"], 0.85)
        self.assertEqual(metrics["confusion_matrix"], [[8, 2], [1, 9]])
        self.assertAlmostEqual(metrics["per_class"]["0"]["precision"], 8 / 9)
        self.assertAlmostEqual(metrics["per_class"]["1"]["recall"], 9 / 10)

    def test_empty_predictions_are_safe(self):
        metrics = metrics_from_cells({})
        self.assertEqual(metrics["rows"], 0)
        self.assertEqual(metrics["accuracy"], 0.0)
        self.assertEqual(metrics["macro_f1"], 0.0)


if __name__ == "__main__":
    unittest.main()

