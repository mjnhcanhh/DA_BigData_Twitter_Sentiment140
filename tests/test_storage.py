import tempfile
import unittest
from pathlib import Path

from twitter_spark.storage import ensure_local_parent, is_hdfs_uri, is_remote_uri


class StoragePathTests(unittest.TestCase):
    def test_detects_hdfs_uri(self):
        uri = "hdfs://localhost:8020/twitter/raw/sentiment140.csv"
        self.assertTrue(is_hdfs_uri(uri))
        self.assertTrue(is_remote_uri(uri))

    def test_local_windows_path_is_not_remote_uri(self):
        self.assertFalse(is_remote_uri(Path("data/raw/input.csv")))
        self.assertFalse(is_remote_uri(r"D:\data\raw\input.csv"))

    def test_creates_parent_only_for_local_path(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "processed" / "tweets"
            ensure_local_parent(target)
            self.assertTrue(target.parent.is_dir())


if __name__ == "__main__":
    unittest.main()
