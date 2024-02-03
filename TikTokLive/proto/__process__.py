import os
import pathlib
import re
from typing import Generator

# Will match "optional uint32 banana = 3;"
VALID_PROTO_MESSAGE: re.Pattern = re.compile(
    r"\s*[a-zA-Z0-9_]*\s*[a-zA-Z0-9_]+\s+[a-zA-Z0-9_]+\s*=\s[0-9]+;"
)

# Will NOT match "optional uint32 banana = 3;"
# Will match "uint32 banana = 3;"
NO_LABEL_PROTO_MESSAGE: re.Pattern = re.compile(
    r"\s*[a-zA-Z0-9_]+\s+[a-zA-Z0-9_]+\s*=\s[0-9]+;"
)


def find_proto_files(source_dir: pathlib.Path) -> Generator[pathlib.Path, None, None]:
    """Read all proto files in the source dir and yield them"""

    for file in os.listdir(str(source_dir)):
        if file.endswith(".proto"):
            yield source_dir.joinpath(file)


def process_proto_dir(source_dir: pathlib.Path, out_dir: pathlib.Path):
    """Convert all fields into optional fields as we can't guarantee the data integrity at TikTok HQ"""

    for file in find_proto_files(source_dir):
        process_proto_file(
            file_path=file,
            out_dir=out_dir
        )


def is_definition_line(text: str, no_label: bool = False) -> bool:
    """Match a line to see if it is a definition line"""
    test: re.Pattern = NO_LABEL_PROTO_MESSAGE if no_label else VALID_PROTO_MESSAGE
    return bool(test.match(text))


def process_definition_line(text: str) -> str:
    """If a line is capable of having an optional annotation, add it"""

    # Must not already have "optional" or "repeated"
    if not is_definition_line(text, no_label=True):
        return text

    for idx, char in enumerate(text):

        # Ignore spaces
        if char.isspace():
            continue

        # If it's a capital letter, it's a custom type, so it shouldn't be an optional
        # The lib nicely handles it by making an empty object.
        if char.isupper():
            return text

        return text[:idx] + "optional " + text[idx:]


"""
DO NOT DELETE

Logic to allow optionals:

# Can't process inside a "oneof" object
if one_of_run:

    if text_line.strip() == "}":
        one_of_run = False

    new_text += text_line

# Can process definition lines
elif is_definition_line(text_line):
    new_text += process_definition_line(text_line)

# Can't process non-definition lines
# Always not currently a run
else:

    if text_line.strip().startswith("oneof"):
        one_of_run = True

    new_text += text_line
    
DO NOT DELETE
"""


def process_proto_file(file_path: pathlib.Path, out_dir: pathlib.Path):
    """Process an individual proto file"""

    new_text: str = ""

    with open(file_path, mode="r", encoding="utf-8") as file:
        for text_line in file:

            # Strip comments
            comment_idx: int = text_line.find("//")
            if comment_idx >= 0:
                text_line = text_line[comment_idx:]

            if text_line.strip().startswith("//"):
                continue

            # int32 can't be a map key in Python
            # instead, we sub it out with a string.
            text_line = text_line.replace("map<int32", "map<string")

            new_text += text_line



    with open(out_dir.joinpath(file_path.name), mode='w', encoding="utf-8") as file:
        file.write(new_text)


if __name__ == '__main__':
    """Compile with __compile__.py, this file is called in there. This exists for testing."""
    mod_path: pathlib.Path = pathlib.Path(__file__).parent.resolve()

    process_proto_dir(
        source_dir=mod_path.joinpath("raw"),
        out_dir=mod_path
    )
