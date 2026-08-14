package twitter_spark;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.LocalFileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.RawLocalFileSystem;
import org.apache.hadoop.fs.permission.FsPermission;

/**
 * Local-only Windows adapter that skips POSIX chmod/chown calls.
 *
 * Hadoop's RawLocalFileSystem invokes winutils.exe for those calls. NTFS access
 * remains governed by Windows ACLs; this class is never enabled outside Windows.
 */
public final class NoPermissionLocalFileSystem extends LocalFileSystem {
    public NoPermissionLocalFileSystem() {
        super(new NoPermissionRawLocalFileSystem());
    }

    private static final class NoPermissionRawLocalFileSystem extends RawLocalFileSystem {
        @Override
        public void setPermission(Path path, FsPermission permission) throws IOException {
            // No POSIX permission bits are available in the local Windows demo.
        }

        @Override
        public void setOwner(Path path, String username, String groupname) throws IOException {
            // Windows ACL ownership is outside the scope of this local Spark demo.
        }

        @Override
        public FileStatus[] listStatus(Path path) throws IOException {
            File local = pathToFile(path);
            if (!local.exists()) {
                throw new FileNotFoundException("File " + path + " does not exist");
            }
            if (local.isFile()) {
                return new FileStatus[] { getFileStatus(path) };
            }
            File[] children = local.listFiles();
            if (children == null) {
                return new FileStatus[0];
            }
            List<FileStatus> statuses = new ArrayList<>();
            for (File child : children) {
                statuses.add(getFileStatus(new Path(path, child.getName())));
            }
            return statuses.toArray(new FileStatus[0]);
        }

        @Override
        public FileStatus getFileStatus(Path path) throws IOException {
            File local = pathToFile(path);
            if (!local.exists()) {
                throw new FileNotFoundException("File " + path + " does not exist");
            }
            boolean directory = local.isDirectory();
            long modified = local.lastModified();
            return new FileStatus(
                local.length(),
                directory,
                1,
                getDefaultBlockSize(path),
                modified,
                modified,
                directory ? FsPermission.getDirDefault() : FsPermission.getFileDefault(),
                System.getProperty("user.name", ""),
                "",
                makeQualified(path)
            );
        }
    }
}
