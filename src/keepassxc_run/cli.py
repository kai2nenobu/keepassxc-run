import argparse
import json
import os
import sys
import subprocess

from dotenv import dotenv_values


def _git_credential_keepassxc(url: str) -> str:
    """Fetch a credential value by 'git-credential-keepassxc'"""
    exe = "git-credential-keepassxc"
    stdin = f"url={url}"
    output = subprocess.check_output(
        [exe, "--unlock", "10,3000", "get", "--json", "--advanced-fields"], input=stdin.encode("utf-8")
    )
    credential = json.loads(output)
    attribute = url.split("/")[-1]
    if attribute in ("username", "password", "url"):
        return credential[attribute]
    else:
        return credential["string_fields"][attribute]


def _read_envs(env_files: list[str]) -> dict[str, str]:
    """Read environment variables from running environment and env files."""
    envs = os.environ.copy()
    for env_file in env_files:
        env_file_values = dotenv_values(env_file)
        envs.update(env_file_values)
    # Fetch secret values from KeePassXC database
    for key, value in envs.items():
        if value.startswith("keepassxc://"):
            envs[key] = _git_credential_keepassxc(value)
    return envs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="+", help="command to execute")
    parser.add_argument(
        "--env-file",
        action="append",
        default=[],
        help="Enable Dotenv integration with specific Dotenv files to parse. For example: --env-file=.env",
    )
    args = parser.parse_args(sys.argv[1:])

    envs = _read_envs(args.env_file)
    process = subprocess.run(args=args.command, check=False, env=envs)
    sys.exit(process.returncode)


if __name__ == "__main__":
    main()
