# Gerador de Perfis Sintéticos em Python

Este é um script Python para gerar **perfis sintéticos determinísticos** usando a biblioteca `Faker`. Ele é útil para testes e desenvolvimento, pois gera dados de pessoas, incluindo informações de parentesco (pai, mãe, avós), de forma consistente a partir de um identificador de entrada.

## Funcionalidades

- **Geração Determinística:** Perfis gerados são sempre os mesmos para o mesmo identificador de entrada.
- **Dados de Parentesco:** Inclui dados sintéticos para pai, mãe, avó paterna e avó materna.
- **CPF Sintético:** Gera um CPF sintético e determinístico.
- **Modos de Uso:** Suporta geração de perfil único, processamento em lote a partir de um arquivo ou leitura a partir da entrada padrão (stdin).
- **Formatos de Saída:** Suporta saída em JSON e CSV.

## Requisitos

O projeto requer apenas a biblioteca `Faker`.

```bash
pip install -r requirements.txt
```

## Uso

O script principal é `gerador_perfis.py`.

### Geração de Perfil Único

Gera um perfil para um identificador específico (ex: número de telefone ou ID).

```bash
python gerador_perfis.py gerar "+5511999999999"
```

Para salvar em um arquivo JSON:

```bash
python gerador_perfis.py gerar "+5511999999999" --out perfil.json --format json
```

### Processamento em Lote

Gera perfis para uma lista de identificadores contidos em um arquivo (um identificador por linha).

```bash
python gerador_perfis.py batch ids.txt --out perfis.csv --format csv
```

## Estrutura do Projeto

- `gerador_perfis.py`: O script principal com toda a lógica de geração.
- `requirements.txt`: Lista de dependências do Python.
- `.gitignore`: Arquivo para ignorar arquivos e diretórios desnecessários no Git.
