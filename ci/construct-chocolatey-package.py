#!/usr/bin/env python
"""
Construct a chocolatey package directory from template package directory ("package/chocolatey" directory)
"""

import argparse
import hashlib
from pathlib import Path
import shutil
import sys

from jinja2 import Template


def parse_args(argv: list[str]):
    parser = argparse.ArgumentParser("")
    parser.add_argument("--version", type=str, required=True, help="package version")
    parser.add_argument("--archive", type=str, required=True, help="path to zip archive")
    parser.add_argument("--template-dir", type=str, required=True, help="directory including package templates")
    parser.add_argument("--output-dir", type=str, required=True, help="output directory")
    args = parser.parse_args(argv)
    return args


def render_template(template_dir: Path, output_dir: Path, template_name: str, variables: dict):
    source = template_dir / template_name
    dest = output_dir / template_name
    template = Template(source=source.read_text(encoding="utf-8"))
    rendered = template.render(variables)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(rendered, encoding="utf-8")


def construct_package(template_dir: Path, output_dir: Path, archive: Path, version: str):
    archive_checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    variables = {
        "version": version,
        "tag_version": f"v{version}",
        "zip_file": archive.name,
        "zip_checksum": archive_checksum,
    }
    render_template(template_dir, output_dir, "keepassxc-run.nuspec", variables)
    render_template(template_dir, output_dir, "tools/chocolateyInstall.ps1", variables)
    shutil.copy(archive, output_dir / "tools" / archive.name)


def main():
    args = parse_args(sys.argv[1:])
    archive = Path(args.archive)
    template_dir = Path(args.template_dir)
    output_dir = Path(args.output_dir)

    construct_package(template_dir, output_dir, archive, args.version)


if __name__ == "__main__":
    main()
