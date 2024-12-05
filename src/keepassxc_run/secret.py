import json
import logging
import shutil
import subprocess


logger = logging.getLogger(__name__)


class SecretStore:
    """Object to fetch secrets. This class fetch secrets by using 'git-credential-keepassxc' command."""

    def __init__(self, debug: bool = False):
        self._debug = debug
        self._exe = self._find_git_credential_keepassxc()

    def _find_git_credential_keepassxc(self) -> str:
        exe = shutil.which("git-credential-keepassxc")
        if exe is None:
            raise FileNotFoundError(
                '"git-credential-keepassxc" command not found in PATH. '
                "Please ensure it is installed and available in your PATH."
            )
        return exe

    def fetch(self, url: str) -> str:
        """Fetch a secret value from a KeePassXC entry which matches specified URL."""
        debug_flag = ["-vvv"] if self._debug else []
        command = [self._exe, *debug_flag, "--unlock", "10,3000", "get", "--json", "--advanced-fields"]
        stdin = f"url={url}"
        process = subprocess.run(
            args=command,
            check=False,
            capture_output=True,
            encoding="utf-8",
            input=stdin,
        )
        if process.returncode > 0:
            logger.warning("Fail to fetch a secret value by %s: URL=%s, error=%s", self._exe, url, process.stderr)
            return url
        logger.debug("%s execution log: %s", self._exe, process.stderr)
        credential = json.loads(process.stdout)
        field = url.split("/")[-1]
        if field in ("username", "password", "url"):
            return credential[field]
        elif ("string_fields" in credential) and (field in credential["string_fields"]):
            return credential["string_fields"][field]
        else:
            logger.warning("Database entry doesn't have field '%s': URL=%s", field, url)
            return url
