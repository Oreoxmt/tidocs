import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional

import platformdirs


class Pandoc:
    """Manage Pandoc installation and execution across different platforms.

    This class handles downloading, installing, and running Pandoc in a user's data directory.
    It supports macOS, Linux, and Windows platforms and manages version control of the installed binary.

    Attributes:
        VERSION: String representing the required Pandoc version.
        DOWNLOAD_URLS_BY_PLATFORM: Dict mapping (OS, architecture) tuples to download URLs.
    """

    VERSION = "3.5"

    DOWNLOAD_URLS_BY_PLATFORM = {
        ("Darwin", "arm64"):
            f"https://github.com/jgm/pandoc/releases/download/{VERSION}/pandoc-{VERSION}-arm64-macOS.zip",
        ("Linux", "x86_64"):
            f"https://github.com/jgm/pandoc/releases/download/{VERSION}/pandoc-{VERSION}-linux-amd64.tar.gz",
        ("Windows", "AMD64"):
            f"https://github.com/jgm/pandoc/releases/download/{VERSION}/pandoc-{VERSION}-windows-x86_64.zip"
    }

    def __init__(self) -> None:
        """Initialize paths for Pandoc binary and version tracking.

        Sets up platform-specific paths for the Pandoc binary and version information using the platformdirs library for cross-platform compatibility.
        """
        appname = "tidocs"
        user_data_dir = Path(platformdirs.user_data_dir(appname))
        self.binary_name = "pandoc.exe" if platform.system() == "Windows" else "pandoc"
        self.pandoc_binary = user_data_dir / self.binary_name
        user_state_dir = Path(platformdirs.user_state_dir(appname))
        self.version_file = user_state_dir / "pandoc_version.txt"

    def is_installed(self) -> bool:
        """Check if Pandoc is properly installed.

        Returns:
            bool: True if Pandoc binary exists and is executable, False otherwise.
        """
        if not self.pandoc_binary.is_file():
            return False

        if not os.access(self.pandoc_binary, os.X_OK):
            return False

        return True

    def is_version_matched(self) -> bool:
        """Verify if installed Pandoc version matches required version.

        Returns:
            bool: True if version matches required VERSION, False otherwise.
        """
        if not self.version_file.is_file():
            return False

        try:
            with open(self.version_file, "r") as f:
                version_info = f.read().strip()
                return version_info == self.VERSION
        except (PermissionError, FileNotFoundError):
            return False

    def save_version_info(self) -> None:
        """Store current Pandoc version information.

        Creates version file directory if it doesn't exist and writes current VERSION to the file.
        """
        self.version_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.version_file, 'w') as f:
            f.write(self.VERSION)

    def install(self) -> Path:
        """Download and install Pandoc if necessary.

        Downloads and extracts the appropriate Pandoc binary for the current platform if it's not already installed or if the version doesn't match requirements.

        Returns:
            Path: Path to the installed Pandoc binary.

        Raises:
            FileNotFoundError: If Pandoc binary cannot be found in downloaded archive.
            AssertionError: If installation fails.
        """
        if self.is_installed() and self.is_version_matched():
            return self.pandoc_binary

        def _progress_callback(count: int, block_size: int, total_size: int) -> None:
            """Display download progress as percentage."""
            percent = int(count * block_size * 100 / total_size)
            sys.stdout.write(f"\rDownloading Pandoc: {percent}%")
            sys.stdout.flush()

        # Clean existing binary if present
        if self.pandoc_binary.exists():
            self.pandoc_binary.unlink()

        # Clean existing version file if present
        if self.version_file.exists():
            self.version_file.unlink()

        # Get the appropriate download URL for the current platform.
        system = platform.system()
        arch = platform.machine()
        platform_key = (system, arch)
        url = self.DOWNLOAD_URLS_BY_PLATFORM.get(platform_key)

        # Download and extract Pandoc
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir_path = Path(tmp_dir)
            _, _, archive_name = url.rpartition("/")
            archive_path = tmp_dir_path / archive_name

            print(f"Downloading from {url} to {archive_path}")
            urllib.request.urlretrieve(url, archive_path, _progress_callback)
            print()  # New line after progress

            # Extract archive
            extracted = None
            if archive_name.endswith(".zip"):
                with zipfile.ZipFile(archive_path, "r") as file:
                    for info in file.infolist():
                        # No need to check whether info is a file because directories always end with / and basename will be empty.
                        _, _, basename = info.filename.rpartition("/")
                        if basename == self.binary_name:
                            file.extract(info, tmp_dir_path)
                            extracted = tmp_dir_path / info.filename
                            extracted.chmod(info.external_attr >> 16)
                            break
            elif archive_name.endswith(".tar.gz"):
                with tarfile.open(archive_path, "r") as file:
                    for info in file.getmembers():
                        if not info.isfile():
                            continue
                        _, _, basename = info.name.rpartition("/")
                        if basename == self.binary_name:
                            file.extract(info, tmp_dir_path, filter="tar")
                            extracted = tmp_dir_path / info.name
                            break
            if extracted is None:
                raise FileNotFoundError(f"pandoc binary {self.binary_name} not found in downloaded archive")

            self.pandoc_binary.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(extracted, self.pandoc_binary)

        if not self.is_installed():
            raise AssertionError("Pandoc installation failed.")

        # Save version information after successful installation
        self.save_version_info()
        if not self.is_version_matched():
            raise AssertionError("Pandoc version does not match requirements.")

        return self.pandoc_binary

    def run(self, args: list, stdin: Optional[bytes] = None) -> (bytes, bytes):
        """Execute Pandoc with specified arguments.

        Installs or updates Pandoc if necessary before running the command.

        Args:
            args: List of command-line arguments to pass to Pandoc.
            stdin: Optional bytes to pass to Pandoc's standard input.

        Returns:
            bytes: Output from Pandoc's stdout.

        Example:
            >>> pandoc = Pandoc()
            >>> output, err = pandoc.run(["--version"])
            >>> output.decode("utf-8").startswith(f"pandoc {pandoc.VERSION}")
            True
            >>> err.decode("utf-8") == ""
            True
            >>> _, unknown_err = pandoc.run(["--vv"])
            >>> unknown_err.decode("utf-8").startswith(f"Unknown option --vv")
            True
        """
        self.install()  # Handle any needed updates
        p = subprocess.Popen(
            [str(self.pandoc_binary), *args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = p.communicate(stdin)
        return stdout, stderr
