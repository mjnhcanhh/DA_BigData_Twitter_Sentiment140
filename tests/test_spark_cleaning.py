import os
import unittest


RUN_SPARK_TESTS = os.environ.get("RUN_SPARK_TESTS") == "1"


@unittest.skipUnless(RUN_SPARK_TESTS, "Set RUN_SPARK_TESTS=1 to run Spark integration tests")
class SparkCleaningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from twitter_spark.spark_session import create_spark

        cls.spark = create_spark("local[1]", 2)

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_cleaning_removes_url_and_mention_but_keeps_negation(self):
        from pyspark.sql import functions as F

        from twitter_spark.data import clean_text_expr

        frame = self.spark.createDataFrame(
            [("The movie was NOT good! @person https://example.com",)], ["text"]
        ).withColumn("clean_text", clean_text_expr(F.col("text")))
        cleaned = frame.first()["clean_text"]
        self.assertEqual(cleaned, "the movie was not good")


if __name__ == "__main__":
    unittest.main()

