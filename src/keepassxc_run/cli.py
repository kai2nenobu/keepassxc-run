import argparse
import json
import logging
import os
import sys
import subprocess

from dotenv import dotenv_values

import keepassxc_run

logger = logging.getLogger(__name__)


def _git_credential_keepassxc(url: str, debug: bool) -> str:
    """Fetch a credential value by 'git-credential-keepassxc'"""
    exe = "git-credential-keepassxc"
    debug_flag = ["-vvv"] if debug else []
    command = [exe, *debug_flag, "--unlock", "10,3000", "get", "--json", "--advanced-fields"]
    stdin = f"url={url}"
    process = subprocess.run(
        args=command,
        check=False,
        capture_output=True,
        encoding="utf-8",
        input=stdin,
    )
    if process.returncode > 0:
        logger.warning("Fail to fetch a secret value by %s: URL=%s, error=%s", exe, url, process.stderr)
        return url
    logger.debug("%s execution log: %s", exe, process.stderr)
    credential = json.loads(process.stdout)
    field = url.split("/")[-1]
    if field in ("username", "password", "url"):
        return credential[field]
    elif ("string_fields" in credential) and (field in credential["string_fields"]):
        return credential["string_fields"][field]
    else:
        logger.warning("Database entry doesn't have field '%s': URL=%s", field, url)
        return url


def _read_envs(env_files: list[str], debug: bool) -> dict[str, str]:
    """Read environment variables from running environment and env files."""
    envs = os.environ.copy()
    for env_file in env_files:
        env_file_values = dotenv_values(env_file)
        envs.update(env_file_values)
    # Fetch secret values from KeePassXC database
    for key, value in envs.items():
        if value.startswith("keepassxc://"):
            envs[key] = _git_credential_keepassxc(value, debug)
    return envs


def run(argv: list[str]) -> int:
    logging.basicConfig(format="[%(asctime)s.%(msecs)03d] %(levelname)s %(message)s", datefmt="%X")
    parser = argparse.ArgumentParser(add_help=False, exit_on_error=False)
    parser.add_argument(
        "command", nargs="*", help='command to execute. prepend "--" if you specify command option like "--version"'
    )
    parser.add_argument("--help", action="store_true", help="show this help message")
    parser.add_argument("--debug", action="store_true", help="Enable debug log")
    parser.add_argument(
        "--env-file",
        action="append",
        default=[],
        help="Enable Dotenv integration with specific Dotenv files to parse. For example: --env-file=.env",
    )
    try:
        args = parser.parse_args(argv)
    except argparse.ArgumentError as e:
        logger.error("%s", str(e))
        parser.print_help()
        return 2

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.help:
        parser.print_help()
        return 0

    if len(args.command) == 0:
        logger.error("expected at least 1 arguments for command but got 0 instead")
        parser.print_help()
        return 2

    logger.debug("keepassxc-run version: %s", keepassxc_run.__version__)
    envs = _read_envs(args.env_file, args.debug)
    process = subprocess.run(args=args.command, check=False, env=envs)
    return process.returncode


def main():
    sys.exit(run(sys.argv[1:]))


if __name__ == "__main__":
    main()
