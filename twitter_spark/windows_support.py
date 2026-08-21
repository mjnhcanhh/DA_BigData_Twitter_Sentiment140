from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def build_local_filesystem_jar() -> Path | None:
    """Build the tiny Windows local-FS adapter when winutils is unavailable."""
    if os.name != "nt":
        return None
    hadoop_home = os.environ.get("HADOOP_HOME")
    if hadoop_home and (Path(hadoop_home) / "bin" / "winutils.exe").is_file():
        return None

    import pyspark

    project_root = Path(__file__).resolve().parents[1]
    source = project_root / "java" / "twitter_spark" / "NoPermissionLocalFileSystem.java"
    build_root = project_root / ".spark-support"
    classes = build_root / "classes"
    output_jar = build_root / "no-permission-local-fs.jar"
    if output_jar.exists() and output_jar.stat().st_mtime >= source.stat().st_mtime:
        return output_jar.resolve()

    javac = shutil.which("javac")
    jar_tool = shutil.which("jar")
    if not javac or not jar_tool:
        raise RuntimeError(
            "Windows needs either HADOOP_HOME with winutils.exe or a full JDK with "
            "javac/jar so the local filesystem adapter can be built. Install JDK 17."
        )

    jars = Path(pyspark.__file__).resolve().parent / "jars" / "*"
    classes.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            [javac, "-cp", str(jars), "-d", str(classes), str(source)],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [jar_tool, "--create", "--file", str(output_jar), "-C", str(classes), "."],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or exc.stdout or str(exc)).strip()
        raise RuntimeError(f"Could not build Windows Spark filesystem adapter: {details}") from exc
    return output_jar.resolve()
