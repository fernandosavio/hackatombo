from os import name
import sys

from pathlib import Path
from typing import Optional, Tuple

import requests


Version = Tuple[int, int, int]

# https://www.python.org/dev/peps/pep-0440/#version-specifiers
_version_specifiers_3char = {'==='}
_version_specifiers_2char = {'~=', '!=', '<=', '>=', '=='}
_version_specifiers_1char = {'>', '<'}


def iter_specs(line):
    """
    Generator que gera nome do pacote + especificações de versão.

    Exemplo:
    >>> list(iter_specs('pytest >= 1.2.3, <2.0.0'))
    ['pytest', '>=1.2.3', '<2.0.0']
    """
    expecting_comma = False
    start_index = 0
    line = line.replace(' ', '')

    i = 0
    while i < (len(line) - 1):
        in_1char = line[i] in _version_specifiers_1char 
        in_2char = line[i:i+2] in _version_specifiers_2char 
        in_3char = line[i:i+3] in _version_specifiers_3char
        
        if in_3char:
            jump = 3
        elif in_2char:
            jump = 2
        else:
            jump = 1

        if (in_3char or in_2char or in_1char):
            # o primeiro yield é o nome do pacote
            if start_index == 0:
                # remove extras e normaliza o nome
                name, _, _ = line[:i].partition('[')
                yield name.lower()

            expecting_comma = True
            start_index = i
            i += jump
            continue
        
        if expecting_comma and line[i] == ',':
            yield line[start_index:i]
            expecting_comma = False
        
        i += 1
    
    # Se ainda não encontrou nada, retorno apenas o nome do pacote
    if start_index == 0:
        # remove extras e normaliza o nome
        name, _, _ = line.partition('[')
        yield name.strip().lower()
    else:
        # retorna o último spec
        yield line[start_index:]


def extract_line_info(line: str) -> Optional[Tuple[str, Version]]:
    """
    Lê uma linha do arquivo e extrai o nome do pacote removendo os [extras]
    e a versão (será usado -1 para os valores da tupla que forem incertos).
    """

    # remove espaços antes e depois
    line = line.strip()

    # ignora a linha se:
    if (
        not line                  # for linha em branco
        or line.startswith('#')   # for um comentário 
        or line.startswith('-r')  # for importação de outro requirements
    ):
        return None
    
    name, *specs = iter_specs(line)
    
    # filtra apenas os specs que sejam '=='
    specs = [
        s[2:] for s in specs
        if s.startswith('==') and not s.startswith('===')
    ]

    # Se tiver duas specs que usam '==' ignora a linha
    if len(specs) > 1:
        return None

    version = [-1, -1, -1]

    # se encontrou specs preenche as versões reconhecidas
    if specs:
        _v = specs[0].split('.', maxsplit=2)

        for i in range(3):
            try:
                version[i] = int(_v[i].rstrip(' ,'))
            except (IndexError, TypeError, ValueError):
                break
    
    return name.strip(), tuple(version)


def get_api_info(package_name):
    url = f'https://pypi.org/pypi/{package_name}/json'
    
    response = requests.get(url)

    if response.status_code >= 400:
        print(f'Erro ao acessar url "{url}"')
        return None
    
    data = response.json()
    
    return tuple(
        int(x) 
        for x in data['info']['version'].split('.', maxsplit=2)
    )

def is_updated(current, latest):
    if -1 in current:
        return False
    
    return current >= latest


def print_formatted_results(results, name_columns_size):
    name_columns_size = max(name_columns_size, 7)
    version_column_size = 11
    _n = "─" * name_columns_size
    _v = "─" * version_column_size

    print("┌" + _n + "┬" + _v + "┬" + _v + "┬" + _v + "┐")
    print(
        "│" 
        + "Package".center(name_columns_size) 
        + "│" 
        + "Current".center(version_column_size)
        + "│"
        + "Latest".center(version_column_size)
        + "│"
        + "Updated".center(version_column_size)
        + "│"
    )
    print(
        "├" + _n + "┼" + _v + "┼" + _v + "┼" + _v + "┤"
    )
    for package, version, api_version, updated in results:
        package: str
        print(
            "│" 
            + package.ljust(name_columns_size) 
            + "│"
            + "{a}.{b}.{c}".format(
                a='?' if version[0] == -1 else version[0],
                b='?' if version[1] == -1 else version[1],
                c='?' if version[2] == -1 else version[2],
            ).center(11)
            + "│"
            + "{a}.{b}.{c}".format(
                a='?' if api_version[0] == -1 else api_version[0],
                b='?' if api_version[1] == -1 else api_version[1],
                c='?' if api_version[2] == -1 else api_version[2],
            ).center(11)
            + "│"
            + ("✓" if updated else "✗").center(version_column_size)
            + "│"
        )
    print("└" + _n + "┴" + _v + "┴" + _v + "┴" + _v + "┘")


def main(filepath: Path):
    with filepath.open(mode='r', encoding='utf8') as file:
        results = []
        max_name_size = 0

        for line in file:
            result = extract_line_info(line)

            if result is None:
                continue
            
            package, version = result
            max_name_size = max(max_name_size, len(package))

            current_version = get_api_info(package)
            
            results.append(
                (
                    package, 
                    version, 
                    current_version, 
                    is_updated(version, current_version),
                )
            )
        print_formatted_results(results, max_name_size)


if __name__ == '__main__':
    try:
        filepath = sys.argv[1]
    except IndexError:
        print("O programa deve receber um arquivo 'requirements.txt'.")
        exit(1)
    
    filepath = Path(filepath)

    if not filepath.is_file():
        print("'requirements.txt' não existe ou não é um arquivo.")
        exit(1)
    
    if filepath.suffix != '.txt':
        print("Arquivo não é um .txt")
        exit(1)
    
    print(filepath.resolve())

    main(filepath)
