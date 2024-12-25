[![PyPI][pypi_badge]][pypi_project] ![PythonVersions][pyversions] [![LICENSE][license_badge]][license_url] [![CI][actions_status]][ci_workflow]

[pypi_project]: https://pypi.org/project/keepassxc-run/
[pypi_badge]: https://img.shields.io/badge/pypi-v0.1.0-orange
[license_badge]: https://img.shields.io/badge/license-MIT-green
[license_url]: https://github.com/kai2nenobu/keepassxc-run/blob/main/LICENSE
[pyversions]: https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue
[actions_status]: https://github.com/kai2nenobu/keepassxc-run/actions/workflows/ci.yml/badge.svg
[ci_workflow]: https://github.com/kai2nenobu/keepassxc-run/actions/workflows/ci.yml

# keepassxc-run

Pass secrets in KeePassXC databases as environment variables to an application or script. This project is inspired by [op run](https://developer.1password.com/docs/cli/reference/commands/run/) command.

```sh
usage: keepassxc-run.py [options] -- [command ...]

positional arguments:
  command              command to execute. prepend "--" if you specify command option like "--version"

options:
  --help               show this help message
  --debug              Enable debug log
  --env-file ENV_FILE  Enable Dotenv integration with specific Dotenv files to parse. For example: --env-file=.env
  --no-masking         Disable masking of secrets on stdout and stderr.  
```

`keepassxc-run` depends on [git-credential-keepassxc](https://github.com/Frederick888/git-credential-keepassxc) to fetch secrets from KeePassXC databases. Ensure that `git-credential-keepassxc` is installed and [configured](https://github.com/Frederick888/git-credential-keepassxc?tab=readme-ov-file#configuration).

## Usage

`keepassxc-run` scans environment variables for secret references, loads the corresponding secrets from KeePassXC databases, then runs the provided command in a subprocess with the secrets made available as environment variables for the duration of the subprocess.

If the same environment variable name exists in both the shell and the environment file, the environment file takes precedence. If the same environment variable name exists in multiple environment files, the last environment file takes precedence.

## Examples

Suppose the KeePassXC database contains an entry like a image below.

![images/example_com_entry.png](images/example_com_entry.png)

Assume that `TEST_PASSWORD` environment variable is configured as below.

```sh
export TEST_PASSWORD="keepassxc://example.com/password"
```

If an environment variable starts with `keepassxc://`, `keepassxc-run` searches an entry matching URL in KeePassXC databases and pass a secret to subprocess as an environment variable value. `keepassxc-run` masks secret values in stdout and stderr by default as below.

```console
$ keepassxc-run -- printenv TEST_PASSWORD
<concealed by keepassxc-run>
```

`keepassxc-run` turns off masking with `--no-masking` option.

```
$ keepassxc-run --no-masking -- printenv TEST_PASSWORD
testuser*p@ssw0rd
```

You can fetch additional attributes which start `KPH: ` like below.

![images/example_com_advanced_field.png](images/example_com_advanced_field.png)

```console
$ export TEST_PASSWORD="keepassxc://example.com/api_key"
$ keepassxc-run --no-masking -- printenv TEST_PASSWORD
my*api*key
```

Specify an environment file and use it:

```sh
echo "TEST_PASSWORD=keepassxc://example.com/password" > .env
```

```console
$ keepassxc-run --no-masking --env-file .env -- printenv TEST_PASSWORD
testuser*p@ssw0rd
```

## License

MIT License. See [LICENSE](./LICENSE) for details.
