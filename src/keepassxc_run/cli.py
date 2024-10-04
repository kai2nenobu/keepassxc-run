import argparse
import sys
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="+", help="command to execute")
    args = parser.parse_args(sys.argv[1:])

    process = subprocess.run(args=args.command, check=False)
    sys.exit(process.returncode)


if __name__ == "__main__":
    main()
