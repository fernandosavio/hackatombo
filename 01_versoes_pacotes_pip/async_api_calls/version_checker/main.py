import argparse

from . import __version__
from .parser import Package


def get_options():
    """
    Faz o parsing dos argumentos recebidos pela linha de comando.

    Docs: https://docs.python.org/3.9/library/argparse.html
    Tutorial: https://docs.python.org/3.9/howto/argparse.html
    """
    parser = argparse.ArgumentParser(
        prog='version_checker',
        description='''
            Reads package version from a requirements-like text file and check on 
            PyPI if there is a newer version for each package.
            Prints the results as a JSON to stdout.
        ''',
        epilog='''
            This script uses "Version matching" especifier (`==`) to recognize
            the package version. So especifiers as `!=`, `~=`, `>=`, `>=`, `>` and `<`
            are treated as being up to date version.
        ''',
    )
    parser.add_argument(
        '-f', '--file',
        help="requirements file path (defaults to stdin).",
        default='-',
        type=argparse.FileType('r', encoding='utf8'),
    )
    parser.add_argument(
        '-V', '--version',
        action='version',
        version=f'%(prog)s {__version__}',
    )
    return parser.parse_args()


def main():
    opts = get_options()

    for package in Package.from_file(opts.file):
        print(package)

    opts.file.close()


if __name__ == '__main__':
    main()
