"""Validate archive paths and entry types before extraction."""

import ntpath
import stat
import sys
import tarfile
import zipfile
import zlib


class UnsafeArchive(Exception):
    """The archive contains an entry that must not be extracted."""


def validate_name(name):
    if not name or "\x00" in name or "\\" in name:
        raise UnsafeArchive("invalid archive member path")
    if name.startswith("/") or ntpath.splitdrive(name)[0]:
        raise UnsafeArchive("absolute archive member path")
    if ".." in name.split("/"):
        raise UnsafeArchive("path traversal archive member")


def inspect_tar(archive_path):
    with tarfile.open(archive_path, mode="r:gz") as archive:
        members = archive.getmembers()
        if not members:
            raise UnsafeArchive("archive is empty")
        for member in members:
            validate_name(member.name)
            if member.issym() or member.islnk():
                raise UnsafeArchive("archive contains a symbolic or hard link")
            if not (member.isfile() or member.isdir()):
                raise UnsafeArchive("archive contains an unsupported entry type")
            if member.isfile():
                stream = archive.extractfile(member)
                if stream is None:
                    raise UnsafeArchive("malformed archive file entry")
                with stream:
                    while stream.read(1024 * 1024):
                        pass
    return len(members)


def inspect_zip(archive_path):
    with zipfile.ZipFile(archive_path, mode="r") as archive:
        members = archive.infolist()
        if not members:
            raise UnsafeArchive("archive is empty")
        for member in members:
            validate_name(member.filename)
            mode = member.external_attr >> 16
            entry_type = stat.S_IFMT(mode)
            if entry_type == stat.S_IFLNK:
                raise UnsafeArchive("archive contains a symbolic link")
            if entry_type not in (0, stat.S_IFREG, stat.S_IFDIR):
                raise UnsafeArchive("archive contains an unsupported entry type")
        bad_member = archive.testzip()
        if bad_member is not None:
            raise UnsafeArchive("malformed archive member data")
    return len(members)


def main():
    archive_path, archive_format = sys.argv[1:3]
    try:
        if archive_format == "tar.gz":
            count = inspect_tar(archive_path)
        elif archive_format == "zip":
            count = inspect_zip(archive_path)
        else:
            raise UnsafeArchive("unsupported archive format")
    except UnsafeArchive as error:
        print(str(error), file=sys.stderr)
        return 1
    except (EOFError, OSError, tarfile.TarError, zipfile.BadZipFile,
            RuntimeError, zlib.error) as error:
        print("malformed archive: {}".format(type(error).__name__), file=sys.stderr)
        return 1

    print(count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
