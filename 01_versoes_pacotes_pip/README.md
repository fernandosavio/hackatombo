# Comparação de versões de pacotes no arquivo `requirements.txt`

## O problema

A equipe de desenvolvimento sinalizou que muitos projetos estão com versões de libs desatualizadas,
e para verificar todos os projetos levaria bastante tempo. Os desenvolvedores tiveram uma ideia,
"que tal ler o arquivo requiments.txt e utilizar a [API pública do PyPI](https://warehouse.readthedocs.io/api-reference/json.html)"

## Solução

Você deve desenvolver um programa que leia o arquivo requirements.txt
listando todas as libs/versões validando pela api pública do PyPI.

A saída deverá estar no formato JSON seguinte:

```
[{
    "packageName": "Nome do pacote",
    "currentVersion": "Versão atual do pacote",
    "latestVersion": "Última versão do pacote",
    "outOfDate: true or false
}]
```
