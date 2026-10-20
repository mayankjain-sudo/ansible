"""Create isolated unsafe and malformed archive fixtures."""

import io
import stat
import sys
import tarfile
import zipfile
from pathlib import Path


fixture_dir = Path(sys.argv[1])
fixture_dir.mkdir(parents=True, exist_ok=True)


def add_tar_file(archive, name, data=b"unsafe fixture"):
    member = tarfile.TarInfo(name)
    member.size = len(data)
    archive.addfile(member, io.BytesIO(data))


with tarfile.open(fixture_dir / "tar-traversal.tar.gz", "w:gz") as archive:
    add_tar_file(archive, "../outside.txt")

with tarfile.open(fixture_dir / "tar-safe.tar.gz", "w:gz") as archive:
    add_tar_file(archive, "safe.txt", b"safe fixture")

with tarfile.open(fixture_dir / "tar-symlink.tar.gz", "w:gz") as archive:
    link = tarfile.TarInfo("unsafe-link")
    link.type = tarfile.SYMTYPE
    link.linkname = "../../outside.txt"
    archive.addfile(link)

with tarfile.open(fixture_dir / "tar-hardlink.tar.gz", "w:gz") as archive:
    link = tarfile.TarInfo("unsafe-hardlink")
    link.type = tarfile.LNKTYPE
    link.linkname = "../../outside.txt"
    archive.addfile(link)

with (fixture_dir / "tar-malformed.tar.gz").open("wb") as archive:
    archive.write(b"not a gzip or tar archive")

with zipfile.ZipFile(fixture_dir / "zip-traversal.zip", "w") as archive:
    archive.writestr("../outside.txt", "unsafe fixture")

with zipfile.ZipFile(fixture_dir / "zip-symlink.zip", "w") as archive:
    link = zipfile.ZipInfo("unsafe-link")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    archive.writestr(link, "../../outside.txt")

with (fixture_dir / "zip-malformed.zip").open("wb") as archive:
    archive.write(b"not a zip archive")
