import asyncio
import logging
import sys
import typing

logger = logging.getLogger(__name__)


async def chunked_stream(reader: asyncio.streams.StreamReader):
    """Read a stream per chunk."""
    while chunk := await reader.read(4096):
        yield chunk


class SubProcess:
    MASK = b"<concealed by keepassxc-run>"

    def __init__(self, command: list[str], envs: dict[str, str], secrets: list[str], mask: bool = True):
        self._command = command
        self._envs = envs
        self._secrets = [s.encode("utf-8") for s in secrets]  # str to bytes
        self._mask = mask

    def _mask_secrets(self, byte: bytes) -> bytes:
        for secret in self._secrets:
            byte = byte.replace(secret, SubProcess.MASK)
        return byte

    async def _mask_stream(self, stream: asyncio.streams.StreamReader, target: typing.BinaryIO):
        async for chunk in chunked_stream(stream):
            target.write(self._mask_secrets(chunk))
            target.flush()

    async def run(self) -> int:
        """
        Run and wait subprocess. Return the return code of subprocess.

        Secrets in stdout and stderr are masked.
        """
        if self._mask:
            process = await asyncio.create_subprocess_exec(
                *self._command,
                env=self._envs,
                shell=False,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            _, _, rc = await asyncio.gather(
                self._mask_stream(process.stdout, sys.stdout.buffer),
                self._mask_stream(process.stderr, sys.stderr.buffer),
                process.wait(),
            )
            return rc
        else:
            # Run process without masking
            process = await asyncio.create_subprocess_exec(
                *self._command,
                env=self._envs,
                shell=False,
            )
            return await process.wait()
