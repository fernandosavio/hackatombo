import re
from typing import Generator, NamedTuple, Optional, TextIO


regex_version = regex = re.compile(r'''
    (?P<package>[A-Z0-9](?:[A-Z0-9._-]*[A-Z0-9])?)
    \s*           # ignore whitespaces between name and extras
    (?:\[.*?\])?  # match extras and ignore it
    \s*           # ignore whitespaces between name and spec
    (?: 
        # (?P<spec>!=|~=|==|>=?|>=?)   # use this line to capture other specs
        (?P<spec>==)   # this line just matches `==` specs
        \s*           # ignore whitespaces between spec and version
        (?P<major>\d+)  # major only. Ex.: 1
        (?:
            \.(?P<minor>\d+)  # major only. Ex.: 1.2
            (?:
                \.(?P<patch>\d+)    # major only. Ex.: 1.2.3
            )?
        )?
    )?
''', re.VERBOSE | re.IGNORECASE)


class Version(NamedTuple):
    major: int
    minor: Optional[int] = None
    patch: Optional[int] = None

    def __str__(self) -> str:
        return f"{self.major}.{self.minor or '?'}.{self.patch or '?'}"
    

class Package:
    """
    Represents a package parsed from a file.

    If version is None means that no version was found in the file or the 
    version specifier was other than `==`, so we will assume the package
    is not up to date.
    """
    __slots__ = ("name", "version")

    def __init__(self, name: str, version: Optional[Version] = None) -> None:
        self.name = name
        self.version = version

    def __str__(self) -> str:
        version = str(self.version) if self.version else '?.?.?'
        return f"{self.name} {version}"
    
    def __repr__(self) -> str:
        _type = type(self).__name__
        return f"<{_type} name={self.name!r} version={self.version!r}>"
    
    @classmethod
    def parse(cls, string: str) -> 'Package':
        """
        Parses a requirements.txt line and returns a Package objects with
        version=None in case no version is found.
        """
        match = regex_version.search(string)

        if not match:
            raise ValueError("Invalid string.")
        
        _version = match.group('major', 'minor', 'patch')

        return Package(
            name=match.group('package'),
            version=Version(*_version) if _version[0] is not None else None,
        )

    @classmethod
    def from_file(cls, file: TextIO) -> Generator['Package', None, None]:
        """
        Parses a text buffer and yields Package objects ignoring comment lines.
        """
        for line in file:
            line: str = line.strip()
            
            if not line or line.startswith('#'):
                # ignore empty lines and comments
                continue
            
            yield cls.parse(line)
