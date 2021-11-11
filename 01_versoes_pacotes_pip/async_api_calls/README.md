## Instruções de uso

### Usando como _package_

```
python -m version_checker --file requirements.txt

python -m version_checker -f ../requirements.txt

cat requirements.txt | python -m version_checker

echo "django==3.2.4" | python -m version_checker
```


### ~~Usando como modulo~~

Ainda não está funcionando usando o arquivo diretamente 
(tretas com o path de importação do `__version__`).

```
python version_checker/main.py --file requirements.txt

python version_checker/main.py -f ../requirements.txt

cat requirements.txt | python version_checker/main.py
```

