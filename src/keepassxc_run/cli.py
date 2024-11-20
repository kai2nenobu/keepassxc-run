import argparse
import json
import os
import sys
import subprocess


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="+", help="command to execute")
    args = parser.parse_args(sys.argv[1:])

    envs = os.environ.copy()
    for key, value in envs.items():
        if value.startswith("keepassxc://"):
            envs[key] = _git_credential_keepassxc(value)
    process = subprocess.run(args=args.command, check=False, env=envs)
    sys.exit(process.returncode)


if __name__ == "__main__":
    main()
