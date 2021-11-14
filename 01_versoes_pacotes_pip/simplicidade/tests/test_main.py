import sys

import pytest

from ..main import extract_line_info, iter_specs


@pytest.mark.parametrize('line,version_expected', [
    ('pytest==1.20.300', (1, 20, 300)),
    ('pytest==1.20', (1, 20, -1)),
    ('pytest==1', (1, -1, -1)),
    ('   pytest  ==  1.20.300 ', (1, 20, 300)),
    (' pytest [extra] ==  1.20.300 ', (1, 20, 300)),
    (' pytest[extra1, extra2] == 1.20', (1, 20, -1)),
    (' pytest[extra1,extra2] == 1', (1, -1, -1)),
    (' PyTest == 1.20.300', (1, 20, 300)),
    (' pytest == 1.20.300dev', (1, 20, -1)),
    (' pytest == 1.20.300rc1', (1, 20, -1)),
    (' pytest == 1.20.300a1', (1, 20, -1)),
    (' pytest == 1.20.300b1', (1, 20, -1)),
])
def test_info_extraction(line, version_expected):
    assert extract_line_info(line) == ('pytest', version_expected)


@pytest.mark.parametrize("line", [
    "",
    "  \t  ",
    "# comments",
    "    # comments",
    "  -r outro-arquivo.txt",
    "-r folder/outro-arquivo.txt",
    " pytest == 1.2.3, == 1.2.4",
])
def test_ignored_lines(line):
    assert extract_line_info(line) is None


@pytest.mark.parametrize('line', [
    ' pytest >= 1.20.300 ',
    ' pytest <= 1.20.300 ',
    ' pytest ~= 1.20.300 ',
    ' pytest != 1.20.300 ',
    ' pytest < 1.20.300 ',
    ' pytest > 1.20.300 ',
    ' pytest === 1.20.300 ',
    ' pytest ',
    ' pytest [extra] ',
    ' pytest [extra1, extra2] ',
])
def test_info_extraction_no_version(line):
    assert extract_line_info(line) == ('pytest', (-1, -1, -1))


@pytest.mark.parametrize('line', [
    ' pytest >= 1.2.3, < 2.0.0, == 1.5.5 ',
    ' pytest >= 1.2.3, == 1.5.5, < 2.0.0 ',
    ' pytest == 1.5.5, >= 1.2.3, < 2.0.0 ',
])
def test_info_extraction_multiple_version_especifiers(line):
    assert extract_line_info(line) == ('pytest', (1, 5, 5))


@pytest.mark.parametrize('line,expected', [
    (
        ' pytest >= 1.2.3, < 2.0.0, == 1.5.5 ', 
        ('pytest', '>=1.2.3', '<2.0.0', '==1.5.5')
    ),
    (
        ' pytest [extras] >= 1.2.3, == 1.5.5, < 2.0.0 ',
        ('pytest', '>=1.2.3', '==1.5.5', '<2.0.0')
    ),
    (
        ' pytest [extra1, extra2] == 1.5.5, >= 1.2.3, < 2.0.0 ',
        ('pytest', '==1.5.5', '>=1.2.3', '<2.0.0')
    ),
])
def test_iter_specs(line, expected):
    specs = tuple(iter_specs(line))
    assert specs == expected
