import argparse
import logging
import os
import sys
import subprocess

from dotenv import dotenv_values

import keepassxc_run
from keepassxc_run.secret import SecretStore

logger = logging.getLogger(__name__)


def _read_envs(env_files: list[str], secret_store: SecretStore) -> dict[str, str]:
    """Read environment variables from running environment and env files."""
    envs = os.environ.copy()
    for env_file in env_files:
        env_file_values = dotenv_values(env_file)
        envs.update(env_file_values)
    for key, value in envs.items():
        if value.startswith("keepassxc://"):
            envs[key] = secret_store.fetch(value)
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
    secret_store = SecretStore(debug=args.debug)
    envs = _read_envs(args.env_file, secret_store)
    process = subprocess.run(args=args.command, check=False, env=envs)
    return process.returncode


def main():
    try:
        rc = run(sys.argv[1:])
    except Exception as e:
        logger.error("keepassxc-run aborted with some error: %s", e)
        rc = 2
    sys.exit(rc)


if __name__ == "__main__":
    main()
