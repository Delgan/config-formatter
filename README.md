# config-formatter

[![Pypi version](https://img.shields.io/pypi/v/config-formatter.svg)](https://pypi.python.org/pypi/config-formatter) [![Python version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://pypi.python.org/pypi/config-formatter) [![Build status](https://img.shields.io/github/workflow/status/Delgan/config-formatter/Tests/main)](https://github.com/Delgan/config-formatter/actions/workflows/tests.yml?query=branch:main) [![License](https://img.shields.io/github/license/delgan/config-formatter.svg)](https://github.com/Delgan/config-formatter/blob/main/LICENSE)

An automatic formatter for .ini and .cfg configuration files.


## Installation

```shell
pip install config-formatter
```

## Usage

```python
from config_formatter import ConfigFormatter

with open("config.ini", "r") as file:
    formatter = ConfigFormatter()
    formatted = formatter.prettify(file.read())
    print(formatted)
```

## Example

Before:

```ini
[main]        # Comments are preserved.

    # Error-prone indentation is removed.
    [section1]
    key1: value1
    key2=value2  # Value assignment is normalized.


[section2]
lists =
 are
 indented
# including
 comments

multiline =    text that spans
 on several lines
      is properly aligned.
```

After:

```ini
[main]  # Comments are preserved.

# Error-prone indentation is removed.
[section1]
key1 = value1
key2 = value2  # Value assignment is normalized.

[section2]
lists =
    are
    indented
    # including
    comments

multiline = text that spans
            on several lines
            is properly aligned.
```
