from configparser import ConfigParser, DuplicateSectionError
from textwrap import dedent

import pytest

from config_formatter import ConfigFormatter


def compare_formatting(config: str, expected: str, *, verify_parsing: bool = True) -> None:
    config = dedent(config)
    expected = dedent(expected)

    formatter = ConfigFormatter()
    result = formatter.prettify(config)
    assert result == expected

    if verify_parsing:
        parser_before, parser_after = ConfigParser(), ConfigParser()
        parser_before.read_string(config)
        parser_after.read_string(result)
        assert parser_before == parser_after


@pytest.mark.parametrize("string", ["", "\n", "\n\n\n", "\r\n", " ", "\t", "\n \n\t\n"])
def test_empty_string(string: str):
    formatter = ConfigFormatter()
    assert formatter.prettify(string) == "\n"


def test_unique_section():
    formatter = ConfigFormatter()
    assert formatter.prettify("[section]") == "[section]\n"


def test_removing_leading_newlines():
    formatter = ConfigFormatter()
    assert formatter.prettify("\n\n[section]") == "[section]\n"


def test_removing_trailing_newlines():
    formatter = ConfigFormatter()
    assert formatter.prettify("[section]\n\n") == "[section]\n"


def test_removing_trailing_spaces():
    formatter = ConfigFormatter()
    assert formatter.prettify("[section]   \nkey = value\t") == "[section]\nkey = value\n"


def test_removing_leading_spaces():
    formatter = ConfigFormatter()
    assert formatter.prettify("\t[section]\n\tkey = value") == "[section]\nkey = value\n"


def test_formatting_sections():
    config = """\


    [section1]
    [section2]

        [section3]



        [section4]
        key = value

    [section5]


    key = value

    [section6]

    # [section6.5]

      # Indented comment.

    key = value
    key2 = value2
    [ section7  ]

        [section8]  # Comment 1

          # Comment 2
        # Comment 3

        [section9]
            key = value

    key2 = value2
    # key3 = value3
    [section10]
        # Another comment.
    """
    expected = """\
    [section1]
    [section2]

    [section3]

    [section4]
    key = value

    [section5]

    key = value

    [section6]

    # [section6.5]

    # Indented comment.

    key = value
    key2 = value2
    [ section7  ]

    [section8]  # Comment 1

    # Comment 2
    # Comment 3

    [section9]
    key = value

    key2 = value2
    # key3 = value3
    [section10]
    # Another comment.
    """
    compare_formatting(config, expected)


def test_formatting_mixed_comments():
    config = """\

    # This is a top comment.
    #   And a second line.
    ## And a third one.
    ; Want more?


    # A comment before the section.
    [section]     ## A comment for the section name.

        # A comment before the option.
    key = value

    [section2];   A different comment.
    #

    [section3]#
    """
    expected = """\
    # This is a top comment.
    #   And a second line.
    ## And a third one.
    ; Want more?

    # A comment before the section.
    [section]  ## A comment for the section name.

    # A comment before the option.
    key = value

    [section2]  ;   A different comment.
    #

    [section3]  #
    """
    compare_formatting(config, expected)


def test_formatting_options_delimiters():
    config = """\
    [section]
    key1 = value1
    key2 : value2
    key3=value3
    key4:value4
    key5    =    value5
    key6   =:value6
    key7:=   value7
    key8 ==value8
    """
    expected = """\
    [section]
    key1 = value1
    key2 = value2
    key3 = value3
    key4 = value4
    key5 = value5
    key6 = :value6
    key7 = =   value7
    key8 = =value8
    """
    compare_formatting(config, expected)


def test_ambiguous_separator():
    config = """\
    [section]
    key1 : value1=value2
    key2:key3 = "value"
    key3 = value3:value4
    key4=key5 = "value6"
    """
    expected = """\
    [section]
    key1 = value1=value2
    key2 = key3 = "value"
    key3 = value3:value4
    key4 = key5 = "value6"
    """
    compare_formatting(config, expected)


def test_formatting_multiline_values():
    config = """\
    [section]
    key =
                       value
    [section2]
    key1 = 1
        2
      3

    key2 =
      1
        2
          3
    key3 =\t
     a

      key4 =
     a
    """
    expected = """\
    [section]
    key =
        value
    [section2]
    key1 = 1
           2
           3

    key2 =
        1
        2
        3
    key3 =
        a

        key4 =
        a
    """
    compare_formatting(config, expected)


def test_no_extra_newline_added_to_multiline_value():
    config = """\
    [section]
    key =
            foo

     bar
    """
    expected = """\
    [section]
    key =
        foo

        bar
    """
    compare_formatting(config, expected)


def test_indented_options():
    config = """\
    [section1]
        key1 = value1
        key2 = value2
      key3 = value3

    [section2]
        [section3]

        key1 = value1
        key2 = value2
      key3 = value3
    """
    expected = """\
    [section1]
    key1 = value1
    key2 = value2
    key3 = value3

    [section2]
    [section3]

    key1 = value1
    key2 = value2
    key3 = value3
    """
    compare_formatting(config, expected)


def test_formatting_key_with_empty_value():
    config = """\
    [section1]
    key1 =
    key2=
    key3:

    [section2]
        key1=
    key2    =
    key3 :

    [section3]
    key1=#
    key2   :   # Comment 1.
    key3  =#Comment 2.
    """
    expected = """\
    [section1]
    key1 =
    key2 =
    key3 =

    [section2]
    key1 =
    key2 =
    key3 =

    [section3]
    key1 = #
    key2 = # Comment 1.
    key3 = #Comment 2.
    """
    compare_formatting(config, expected)


def test_comments_inside_multiline_values():
    config = """\
    [section]
    key1 =
        1
          # 2
        3

    key2 = 1
     # 2

    key3 = # 1
            # 2
    # Comment.
             3

    key4 = 1
    # 2
                val
    """
    expected = """\
    [section]
    key1 =
        1
        # 2
        3

    key2 = 1
           # 2

    key3 = # 1
           # 2
           # Comment.
           3

    key4 = 1
           # 2
           val
    """
    compare_formatting(config, expected)


def test_comment_along_multiline_values():
    config = """\
    [section]
    key1 =
          1   # Comment 1
           2#Comment 2

            3 #Comment 3
    key2 = 1   # Comment 1
     2#Comment 2

     3 #Comment 3
    """
    expected = """\
    [section]
    key1 =
        1   # Comment 1
        2#Comment 2

        3 #Comment 3
    key2 = 1   # Comment 1
           2#Comment 2

           3 #Comment 3
    """
    compare_formatting(config, expected)


def test_bracket_inside_comment():
    config = """\
    [root]
    key1=value1
    ; [root]
    key2=value2
    ; b = 2 [b]
    key3=value3
    # [root]
    key4=value4
    # c = 3 [[c]]
    key5=value5
    """
    expected = """\
    [root]
    key1 = value1
    ; [root]
    key2 = value2
    ; b = 2 [b]
    key3 = value3
    # [root]
    key4 = value4
    # c = 3 [[c]]
    key5 = value5
    """
    compare_formatting(config, expected)


@pytest.mark.skip("Requires a fix in ConfigUpdater.")
def test_non_alpha_numeric_characters_in_section_name():
    config = """\
    [ ]
    key:value

    [.abc]
    key:value

    [*[a.b.c].abc]
    key:value

    [~!@#$%^&*()_+{}|:"<>?`-=[]\\;',./]
    key:value

    [[[]]]
    key:value

    [[][]]
    key:value
    """
    expected = """\
    [ ]
    key = value

    [.abc]
    key = value

    [*[a.b.c].abc]
    key = value

    [~!@#$%^&*()_+{}|:"<>?`-=[]\\;',./]
    key = value

    [[[]]]
    key = value

    [[][]]
    key = value
    """

    compare_formatting(config, expected)


def test_semicolon_comment_and_multiline_value():
    config = """\
    [options]
    packages = find:
    package_dir =
        =src
    # Somme comment.
    # On multiple lines.
    install_requires =
        mccabe>=0.6.0,<0.7.0 # Comment 1.
        pycodestyle>=2.8.0,<2.9.0 ;python_version>"3.6"   # Comment 2.
        pyflakes>=2.4.0,<2.5.0
        importlib-metadata<4.3;python_version<"3.8"
    python_requires = >=3.6.1
    """
    expected = """\
    [options]
    packages = find:
    package_dir =
        =src
    # Somme comment.
    # On multiple lines.
    install_requires =
        mccabe>=0.6.0,<0.7.0 # Comment 1.
        pycodestyle>=2.8.0,<2.9.0 ;python_version>"3.6"   # Comment 2.
        pyflakes>=2.4.0,<2.5.0
        importlib-metadata<4.3;python_version<"3.8"
    python_requires = >=3.6.1
    """
    compare_formatting(config, expected)


def test_case_unchanged():
    config = """\
    [SECTION]    # Comment 1.
    My Key = 123

    [\tsection\t]
       MY  OTHER  KEY    =    Foo    Bar
    KEY=X#X

    [ ]
        [SeCtIoN N°2]
        # Comment 2.
        FOO=BAR
    """
    expected = """\
    [SECTION]  # Comment 1.
    My Key = 123

    [\tsection\t]
    MY  OTHER  KEY = Foo    Bar
    KEY = X#X

    [ ]
    [SeCtIoN N°2]
    # Comment 2.
    FOO = BAR
    """
    compare_formatting(config, expected)


def test_end_of_line_trimmed():
    config = """\
    [section] # Comment.\t \t
    key = value \t
    other_key = other_value\t\t \t
    # Other comment.\t
    """
    expected = """\
    [section]  # Comment.
    key = value
    other_key = other_value
    # Other comment.
    """
    compare_formatting(config, expected)


def test_section_inside_multiline_option():
    config = """\
    [section]
    key =
          value

          [section2]
          key2 = value2

    key2 = value2

      [section2]
      key2 = value2
    """
    expected = """\
    [section]
    key =
        value

        [section2]
        key2 = value2

    key2 = value2

           [section2]
           key2 = value2
    """
    compare_formatting(config, expected)


def test_properties_without_section():
    config = """\
            key1 = value1
    key2 = value2 # Comment.
    key3:value3
    """
    expected = """\
    key1 = value1
    key2 = value2 # Comment.
    key3 = value3
    """
    compare_formatting(config, expected, verify_parsing=False)


def test_property_before_any_section():
    config = """\

    root = true

    [section]
    foo = bar
    baz = 123
    """
    expected = """\
    root = true

    [section]
    foo = bar
    baz = 123
    """
    compare_formatting(config, expected, verify_parsing=False)


def test_comment_and_properties_before_any_section():
    config = """\

        # Comment before.
        abc = 123
            # 456
            789

    [section-1]
    foo= bar
    [section-2]
    bar =foo
    """
    expected = """\
    # Comment before.
    abc = 123
          # 456
          789

    [section-1]
    foo = bar
    [section-2]
    bar = foo
    """
    compare_formatting(config, expected, verify_parsing=False)


def test_no_error_if_dummy_section_name_exists_without_top_section():
    # The section names here are derived from the internal ConfigFormatter implementation.
    config = """\
    root:true
    [config-formatter-dummy-section-name]
    key:value
    [config-formatter-dummy-section-name-0]
    key0:value0
    [config-formatter-dummy-section-name-1]
    key1:value1
    """
    expected = """\
    root = true
    [config-formatter-dummy-section-name]
    key = value
    [config-formatter-dummy-section-name-0]
    key0 = value0
    [config-formatter-dummy-section-name-1]
    key1 = value1
    """
    compare_formatting(config, expected, verify_parsing=False)


def test_duplicate_section_error_reported_when_no_top_section():
    config = """\
    key1 = value1

    [section]
    key = value

    [section]
    key = value
    """
    with pytest.raises(DuplicateSectionError):
        ConfigFormatter().prettify(dedent(config))


def test_testenv_example():
    config = """\
    [testenv]
    usedevelop = True
    skip_install =\tFalse
    parallel_show_output = false
    commands = \te
      \tf  \\
      \t \\
      \t g
    extras = \tc,d
    description = \tdesc\t
    deps = \t
           \tb\t
      \ta\t
    basepython=\tpython3.8\t
    passenv=z y x
    setenv= C=D
        E =F

                A = B
    """
    expected = """\
    [testenv]
    usedevelop = True
    skip_install = False
    parallel_show_output = false
    commands = e
               f  \\
               \\
               g
    extras = c,d
    description = desc
    deps =
        b
        a
    basepython = python3.8
    passenv = z y x
    setenv = C=D
             E =F

             A = B
    """
    compare_formatting(config, expected)


def test_flake8_example():
    config = """\
    [flake8]
    exclude =
      # Trash and cache:
      .git
      __pycache__
      .venv
      .eggs
      *.egg
      temp
      # Bad code that I write to test things:
      ex.py
    new = value

    per-file-ignores =
      # Disable imports in `__init__.py`:
      lambdas/__init__.py: WPS226, WPS413
      lambdas/contrib/mypy/lambdas_plugin.py: WPS437
      # There are multiple assert's in tests:
      tests/*.py: S101, WPS226, WPS432, WPS436, WPS450
      # We need to write tests to our private class:
      tests/test_math_expression/*.py: S101, WPS432, WPS450
    """
    expected = """\
    [flake8]
    exclude =
        # Trash and cache:
        .git
        __pycache__
        .venv
        .eggs
        *.egg
        temp
        # Bad code that I write to test things:
        ex.py
    new = value

    per-file-ignores =
        # Disable imports in `__init__.py`:
        lambdas/__init__.py: WPS226, WPS413
        lambdas/contrib/mypy/lambdas_plugin.py: WPS437
        # There are multiple assert's in tests:
        tests/*.py: S101, WPS226, WPS432, WPS436, WPS450
        # We need to write tests to our private class:
        tests/test_math_expression/*.py: S101, WPS432, WPS450
    """
    compare_formatting(config, expected)


def test_configparser_example():
    config = """\
    [Simple Values]
    key=value
    spaces in keys=allowed
    spaces in values=allowed as well
    spaces around the delimiter = obviously
    you can also use : to delimit keys from values

    [All Values Are Strings]
    values like this: 1000000
    or this: 3.14159265359
    are they treated as numbers? : no
    integers, floats and booleans are held as: strings
    can use the API to get converted values directly: true

    [Multiline Values]
    chorus: I'm a lumberjack, and I'm okay
        I sleep all night and I work all day

    [No Values]
    # key_without_value (NOT SUPPORTED)
    empty string value here =

    [You can use comments]
    # like this
    ; or this

    # By default only in an empty line.
    # Inline comments can be harmful because they prevent users
    # from using the delimiting characters as parts of values.
    # That being said, this can be customized.

        [Sections Can Be Indented]
            can_values_be_as_well = True
            does_that_mean_anything_special = False
            purpose = formatting for readability
            multiline_values = are
                handled just fine as
                long as they are indented
                deeper than the first line
                of a value
            # Did I mention we can indent comments, too?
    """
    expected = """\
    [Simple Values]
    key = value
    spaces in keys = allowed
    spaces in values = allowed as well
    spaces around the delimiter = obviously
    you can also use = to delimit keys from values

    [All Values Are Strings]
    values like this = 1000000
    or this = 3.14159265359
    are they treated as numbers? = no
    integers, floats and booleans are held as = strings
    can use the API to get converted values directly = true

    [Multiline Values]
    chorus = I'm a lumberjack, and I'm okay
             I sleep all night and I work all day

    [No Values]
    # key_without_value (NOT SUPPORTED)
    empty string value here =

    [You can use comments]
    # like this
    ; or this

    # By default only in an empty line.
    # Inline comments can be harmful because they prevent users
    # from using the delimiting characters as parts of values.
    # That being said, this can be customized.

    [Sections Can Be Indented]
    can_values_be_as_well = True
    does_that_mean_anything_special = False
    purpose = formatting for readability
    multiline_values = are
                       handled just fine as
                       long as they are indented
                       deeper than the first line
                       of a value
    # Did I mention we can indent comments, too?
    """
    compare_formatting(config, expected)
