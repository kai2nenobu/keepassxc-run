import os
from pathlib import Path
from unittest.mock import patch

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
    assert out.rstrip() == str(Path.home())


@pytest.mark.skipif(os.name == "nt", reason="test case for OS other than Windows")
def test_call_command_successfully_other_than_windows(capfd):
    rc = run(["printenv", "HOME"])
    assert rc == 0
    out, _ = capfd.readouterr()
    assert out.rstrip() == str(Path.home())


def test_call_command_with_option(capfd):
    rc = run(["--", "python", "--version"])
    assert rc == 0
    out, _ = capfd.readouterr()
    assert out.startswith("Python 3.")


@pytest.mark.require_db
class TestKeePassXC:
    def printenv(self, env: str):
        code = f"import os; print(os.environ['{env}'], end='')"
        return run(["--no-masking", "--", "python", "-c", code])

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            pytest.param("keepassxc://example.com/login", "testuser", id="login"),
            pytest.param("keepassxc://example.com/username", "testuser", id="username is alias for login"),
            pytest.param("keepassxc://example.com/password", "testuser*p@ssw0rd", id="password"),
            pytest.param("keepassxc://example.com/api_key", "my*api*key", id="advanced_field"),
        ],
    )
    def test_example_com(self, capfd, url, expected):
        with patch.dict("os.environ", {"TEST_SECRET": url}):
            rc = self.printenv("TEST_SECRET")
            assert rc == 0
            out, _ = capfd.readouterr()
            assert out == expected

    def test_unknown_field_returns_url_asis(self, capfd):
        with patch.dict("os.environ", {"TEST_SECRET": "keepassxc://example.com/UNKNOWN_FIELD"}):
            rc = self.printenv("TEST_SECRET")
            assert rc == 0
            out, _ = capfd.readouterr()
            assert out == "keepassxc://example.com/UNKNOWN_FIELD"

    def test_masking_stdout(self, capfd):
        code = "import os; print(os.environ['TEST_SECRET'], end='')"
        with patch.dict("os.environ", {"TEST_SECRET": "keepassxc://example.com/password"}):
            rc = run(["--", "python", "-c", code])
            assert rc == 0
            out, _ = capfd.readouterr()
            assert out == "<concealed by keepassxc-run>"

    def test_masking_stderr(self, capfd):
        code = "import os; import sys; print(os.environ['TEST_SECRET'], end='', file=sys.stderr)"
        with patch.dict("os.environ", {"TEST_SECRET": "keepassxc://example.com/password"}):
            rc = run(["--", "python", "-c", code])
            assert rc == 0
            _, err = capfd.readouterr()
            assert err == "<concealed by keepassxc-run>"
