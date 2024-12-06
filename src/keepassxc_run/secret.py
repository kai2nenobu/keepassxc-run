import json
import logging
import shutil
import subprocess
from typing import Optional


logger = logging.getLogger(__name__)


class SecretEntry:
    """Object which represents an entry in KeePassXC database."""

    @staticmethod
    def from_json(json_str: str) -> "SecretEntry":
        entries_dict = json.loads(json_str)
        return SecretEntry(entries_dict["entries"][0])

    def __init__(self, entry_dict: dict):
        self._raw = entry_dict

    def field(self, name: str) -> Optional[str]:
        """Return a field value matching the specified name."""
        if name == "username":
            # "username" is an alias for "login"
            name = "login"
        if name in ("login", "password"):
            return self._raw[name]
        advanced_name = f"KPH: {name}"
        advanced_field = [f for f in self._raw["stringFields"] if advanced_name in f]
        if advanced_field:
            return advanced_field[0][advanced_name]
        # no field matched
        return None

    @property
    def fullname(self) -> str:
        return f"{self._raw['group']}/{self._raw['name']}"


class SecretStore:
    """Object to fetch secrets. This class fetch secrets by using 'git-credential-keepassxc' command."""

    def __init__(self, debug: bool = False):
        self._debug = debug
        self._exe: Optional[str] = None

    def _find_git_credential_keepassxc(self) -> str:
        exe = shutil.which("git-credential-keepassxc")
        if exe is None:
            raise FileNotFoundError(
                '"git-credential-keepassxc" command not found in PATH. '
                "Please ensure it is installed and available in your PATH."
            )
        return exe

    def _run_git_credential_keepassxc(self, url: str) -> subprocess.CompletedProcess:
        if self._exe is None:
            self._exe = self._find_git_credential_keepassxc()
        debug_flag = ["-vvv"] if self._debug else []
        command = [self._exe, *debug_flag, "--unlock", "20,1500", "get", "--raw"]
        stdin = f"url={url}"
        process = subprocess.run(
            args=command,
            check=False,
            capture_output=True,
            encoding="utf-8",
            input=stdin,
        )
        return process

    def fetch(self, url: str) -> str:
        """Fetch a secret value from a KeePassXC entry which matches specified URL."""
        process = self._run_git_credential_keepassxc(url)
        if process.returncode > 0:
            logger.warning("Fail to fetch a secret value by %s: URL=%s, error=%s", self._exe, url, process.stderr)
            return url
        logger.debug("%s execution log: %s", self._exe, process.stderr)
        field = url.split("/")[-1]
        entry = SecretEntry.from_json(process.stdout)
        field_value = entry.field(field)
        if field_value is None:
            logger.warning("Database entry doesn't have field '%s': entry=%s", field, entry.fullname)
            return url
        return field_value
