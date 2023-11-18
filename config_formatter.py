"""The `config-parser` module provides utilities to format .ini and .cfg files."""
from typing import Tuple

import configupdater
import configupdater.builder
import configupdater.container
import configupdater.parser

__version__ = "1.2.0"
__all__ = ["ConfigFormatter"]


class ConfigFormatter:
    """A class used to reformat .ini/.cfg configurations."""

    def prettify(self, string: str) -> str:
        """Transform the content of a .ini/.cfg file to make it more pleasing to the eye.

        It preserves comments and ensures that it stays semantically identical to the input string
        (the built-in Python module "configparser" serves as reference).

        The accepted entry format is relatively strict, in particular:
            - no duplicated section or option are allowed ;
            - only "=" and ":" delimiters are considered ;
            - only "#" and ";" comment prefixes are considered ;
            - comments next to values are left untouched ;
            - options without assigned value are not allowed ;
            - empty lines in values are allowed but discouraged.

        These settings are those used by default in the "ConfigParser" from the standard library.
        """
        string = string.strip()
        if not string:
            return "\n"
        base_config, has_dummy_top_section = self._load_config(string)
        return self._format_config(base_config, has_dummy_top_section=has_dummy_top_section)

    def _load_config(self, string: str) -> Tuple[configupdater.parser.Document, bool]:
        """Load the given string as a configuration document.

        It also implements a workaround to handle configs that do not have a top section header.
        """
        parser = configupdater.parser.Parser(
            strict=True,
            delimiters=("=", ":"),
            comment_prefixes=("#", ";"),
            inline_comment_prefixes=None,
            allow_no_value=False,
            empty_lines_in_values=True,
        )

        try:
            return parser.read_string(string), False
        except configupdater.MissingSectionHeaderError:
            i = 1
            while True:
                dummy_section = f"[config-formatter-dummy-section-name-{i}]"
                if dummy_section in string:
                    i += 1
                    continue
                return parser.read_string(f"{dummy_section}\n{string}"), True

    def _format_config(
        self, source: configupdater.container.Container, *, has_dummy_top_section: bool
    ) -> str:
        """Recursively construct a normalized string of the given configuration."""
        output = ""

        for block in source.iter_blocks():
            if isinstance(block, configupdater.Section):
                if has_dummy_top_section:
                    has_dummy_top_section = False
                else:
                    comment = block.raw_comment.strip()
                    if comment:
                        output += f"[{block.name}]  {comment}\n"
                    else:
                        output += f"[{block.name}]\n"
                output += self._format_config(block, has_dummy_top_section=False)
            elif isinstance(block, configupdater.Comment):
                for line in block.lines:
                    comment = line.strip()
                    output += f"{comment}\n"
            elif isinstance(block, configupdater.Space):
                if block.lines:
                    output += "\n"
            elif isinstance(block, configupdater.Option):
                key = block.raw_key
                value = block.value
                if value is None:  # Should never happen in theory as "allow_no_value" is disabled.
                    output += f"{key}\n"
                elif "\n" in value:
                    first, *lines = (line.strip() for line in value.splitlines())
                    if not first:
                        output += f"{key} =\n"
                        indent = 4
                    else:
                        output += f"{key} = {first}\n"
                        indent = len(key) + 3
                    for line in lines:
                        if line:
                            output += f"{' ' * indent}{line}\n"
                        else:
                            output += "\n"
                else:
                    value = value.strip()
                    if value:
                        output += f"{key} = {value}\n"
                    else:
                        output += f"{key} =\n"
            else:
                raise ValueError("Encountered an unexpected block type: '%s'", type(block).__name__)

        return output
