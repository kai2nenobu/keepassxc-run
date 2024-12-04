import os
from pathlib import Path

import pytest

from keepassxc_run.cli import run


def test_help():
    rc = run(["--help"])
    assert rc == 0


def test_exit_with_error_when_no_command_is_specified():
    rc = run([])
    assert rc == 2


@pytest.mark.skipif(os.name != "nt", reason="test case for Windows only")
def test_call_command_successfully_in_windows(capfd):
    rc = run(["cmd.exe", "/C", "echo", "%USERPROFILE%"])
    assert rc == 0
    out, _ = capfd.readouterr()
    assert out.startswith(str(Path.home()))


@pytest.mark.skipif(os.name == "nt", reason="test case for OS other than Windows")
def test_call_command_successfully_other_than_windows(capfd):
    rc = run(["printenv", "HOME"])
    assert rc == 0
    out, _ = capfd.readouterr()
    assert out == str(Path.home())


def test_call_command_with_option(capfd):
    rc = run(["--", "python", "--version"])
    assert rc == 0
    out, _ = capfd.readouterr()
    assert out.startswith("Python 3.")
