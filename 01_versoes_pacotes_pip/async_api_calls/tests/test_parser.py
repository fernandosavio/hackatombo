from io import StringIO
import pytest
from ..version_checker.parser import Package, Version


@pytest.mark.parametrize("line", [
    "",
    "  \t  ",
    "# comments",
    "    # comments",
    "-r outro-arquivo.txt",
    "-r folder/outro-arquivo.txt",
])
def test_ignore_invalid_lines(line):
    assert Package.parse(line) is None


@pytest.mark.parametrize("line, expected_version", [
    ("   pytest   ==   10.20.30  ", (10, 20, 30)),
    ("pytest==10.20.30", (10, 20, 30)),
    ("pytest==10.20", (10, 20, None)),
    ("pytest==10.20.*", (10, 20, None)),
    ("pytest==10", (10, None, None)),
    ("pytest==10.*", (10, None, None)),
    ("pytest==10.*.*", (10, None, None)),
    ("pytest==10.20.30dev", (10, 20, 30)),
    ("pytest==10.20.30rc2", (10, 20, 30)),
    ("pytest==10.20.30a1", (10, 20, 30)),
    ("pytest==10.20.30b3", (10, 20, 30)),
    ("pytest[extra1, extra2]==10.20.30", (10, 20, 30)),
])
def test_whitespaces(line, expected_version):
    package = Package.parse(line)
    assert package.name == 'pytest'
    assert package.version == expected_version


@pytest.mark.parametrize('major,minor,patch,expected', [
    (1, 2, 3, '1.2.3'),
    (1, 2, None, '1.2.*'),
    (1, None, None, '1.*.*'),
    (70, 20, 100, '70.20.100'),
    ('1', '2', '3', '1.2.3'),
])
def test_version_str(major, minor, patch, expected):
    assert str(Version(major, minor, patch)) == expected


def test_file_parsing():
    with StringIO("""
        # Comment
        pytest == 1.2.3
        httpx[extra]==100.200.300

    """) as pseudo_file:
        packages =  list(Package.from_file(pseudo_file))

    assert len(packages) == 2
    
    package_1, package_2 = packages
    
    assert package_1.name == 'pytest'
    assert package_1.version == (1, 2, 3)

    assert package_2.name == 'httpx'
    assert package_2.version == (100, 200, 300)
