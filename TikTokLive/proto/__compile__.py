import ast
import io
import logging
import os
import pathlib
import subprocess
import token
import tokenize
from typing import List

import astunparse

from TikTokLive.proto.__process__ import process_proto_dir


class ProtoTranscriber:

    def __init__(self, source_dir: pathlib.Path, file_name: str, out_dir: pathlib.Path = None):
        self._source_dir: str = source_dir.__str__()
        self._file_name: str = file_name
        self._out_dir: str = out_dir.__str__() or "./"
        self._logger: logging.Logger = logging.getLogger("TikToklive")

    def clean_protos(self) -> None:

        for file in os.listdir(self._source_dir):
            fn: str = os.path.join(self._source_dir, file)

            # Only Proto
            if not file.endswith(".proto"):
                continue

            # Remove BS
            with open(fn, encoding="utf-8", mode="r+w") as proto_file:

                output: List[str] = [
                    line for line in proto_file
                    if not (line.strip().startswith("//") and ":\\" in line)
                ]

                proto_file.write("\n".join(output))

    def execute(self) -> None:
        self._logger.info("Current Working Directory: " + os.getcwd())
        self._logger.info("Starting Proto Generation...")
        self._logger.info("Running Command: " + " ".join(self.command))

        res = subprocess.run(self.command, capture_output=True, cwd=self._source_dir)

        if res.returncode:
            self._logger.info("Failed Proto Generation")
            raise RuntimeError(res.stderr.decode('utf-8'))

        self._logger.info("Finished Proto Generation...")

    def __call__(self, *args, **kwargs):
        self.execute()

    @property
    def command(self) -> List[str]:
        return [
            "protoc",
            "-I.",
            f"--python_betterproto_out={self._out_dir}",
            self._file_name
        ]


if __name__ == '__main__':
    # NOTE: Will break if "package" is specified in any of the files
    logging.basicConfig(level=logging.INFO)
    mod_path: pathlib.Path = pathlib.Path(__file__).parent.resolve()

    # First, pre-process to make everything optional fields
    process_proto_dir(
        source_dir=mod_path.joinpath("raw"),
        out_dir=mod_path.joinpath("dist")
    )

    # Then, convert it to Python betterproto
    ProtoTranscriber(
        source_dir=mod_path.joinpath("dist"),
        out_dir=mod_path,
        file_name="webcast.proto"
    )()
