from os import X_OK, openpty
import sys
from pathlib import Path
from typing import Optional, Tuple


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


def main(filepath: Path):
    with filepath.open(mode='r', encoding='utf8') as file:
        for line in file:
            result = extract_line_info(line)

            if result is None:
                continue
            
            package, version = result
            
            print("{package} ({a}.{b}.{c})".format(
                package=package,
                a='*' if version[0] == -1 else version[0],
                b='*' if version[1] == -1 else version[1],
                c='*' if version[2] == -1 else version[2],
            ))


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
