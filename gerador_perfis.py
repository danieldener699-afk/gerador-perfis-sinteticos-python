#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_perfis.py - Gera perfis sintéticos, determinísticos, incluindo dados de pai, mãe, avós materna e paterna.
Uso:
    python gerar_perfis.py gerar "+5511999999999"
    python gerar_perfis.py batch ids.txt --out perfis.csv --format csv
Requisitos: pip install faker
"""
import argparse
import csv
import hashlib
import json
import os
import sys
import uuid
from typing import Dict, List, Optional
from faker import Faker

def seed_from_identifier(identifier: str) -> int:
    h = hashlib.sha256(identifier.encode('utf-8')).digest()
    return int.from_bytes(h[:8], 'big')

def cpf_sintetico(identifier: str) -> str:
    def _digits_from_hash(identifier: str, n: int) -> List[int]:
        h = hashlib.sha256(identifier.encode('utf-8')).digest()
        out = [(h[i % len(h)] % 10) for i in range(n)]
        if all(d == out[0] for d in out):
            out[0] = (out[0] + 1) % 10
        return out
    def _cpf_check_digit(digs: List[int]) -> int:
        weight = len(digs) + 1
        s = sum(d * (weight - i) for i, d in enumerate(digs))
        r = s % 11
        return 0 if r < 2 else 11 - r
    base = _digits_from_hash(identifier + "_cpf", 9)
    d1 = _cpf_check_digit(base)
    d2 = _cpf_check_digit(base + [d1])
    digits = base + [d1, d2]
    s = ''.join(str(d) for d in digits)
    return f"{s[0:3]}.{s[3:6]}.{s[6:9]}-{s[9:11]}"

def get_fakers(seed: int, locale='pt_BR'):
    roles = ['principal', 'pai', 'mae', 'avo_paterna', 'avo_materna']
    fakers = {}
    for i, role in enumerate(roles):
        fake = Faker(locale)
        fake.seed_instance(seed + i)
        fakers[role] = fake
    return fakers

def gerar_perfil(identifier: str, locale='pt_BR') -> Dict:
    seed = seed_from_identifier(identifier)
    fakers = get_fakers(seed, locale)
    perfil = {
        "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, identifier)),
        "input": identifier,
        "cpf_sintetico": cpf_sintetico(identifier),
        "nome": fakers['principal'].name(),
        "email": fakers['principal'].email(),
        "telefone": fakers['principal'].phone_number(),
        "data_nascimento": fakers['principal'].date_of_birth(18, 75).isoformat(),
        "endereco": {
            "rua": fakers['principal'].street_address(),
            "cidade": fakers['principal'].city(),
            "estado": fakers['principal'].state(),
            "cep": fakers['principal'].postcode()
        },
        "empresa": fakers['principal'].company(),
        "cargo": fakers['principal'].job(),
        "pai": {
            "nome": fakers['pai'].name(),
            "telefone": fakers['pai'].phone_number(),
            "data_nascimento": fakers['pai'].date_of_birth(40, 80).isoformat()
        },
        "mae": {
            "nome": fakers['mae'].name(),
            "telefone": fakers['mae'].phone_number(),
            "data_nascimento": fakers['mae'].date_of_birth(40, 80).isoformat()
        },
        "avo_paterna": {
            "nome": fakers['avo_paterna'].name(),
            "telefone": fakers['avo_paterna'].phone_number(),
            "data_nascimento": fakers['avo_paterna'].date_of_birth(65, 100).isoformat()
        },
        "avo_materna": {
            "nome": fakers['avo_materna'].name(),
            "telefone": fakers['avo_materna'].phone_number(),
            "data_nascimento": fakers['avo_materna'].date_of_birth(65, 100).isoformat()
        }
    }
    return perfil

def flatten_for_csv(profile: Dict) -> Dict:
    flat = {}
    for k, v in profile.items():
        if isinstance(v, dict):
            for subk, subv in v.items():
                flat[f"{k}_{subk}"] = subv
        else:
            flat[k] = v
    return flat

def escrever_json(perfiles: List[Dict], path: str, compact: bool = False) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        if compact:
            json.dump(perfiles, f, ensure_ascii=False, separators=(',', ':'))
        else:
            json.dump(perfiles, f, ensure_ascii=False, indent=2)

def escrever_csv(perfiles: List[Dict], path: str) -> None:
    if not perfiles:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            pass
        return
    rows = [flatten_for_csv(p) for p in perfiles]
    fieldnames = []
    for r in rows:
        for k in r.keys():
            if k not in fieldnames:
                fieldnames.append(k)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

def ler_identificadores_de_arquivo(path: str) -> List[str]:
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def parse_args():
    parser = argparse.ArgumentParser(description="Gerar perfis sintéticos a partir de identificadores.")
    sub = parser.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('gerar', help='Gerar perfil único')
    g.add_argument('identificador', help='Número de telefone ou @')
    g.add_argument('--locale', default='pt_BR', help='Locale do Faker (padrão: pt_BR)')
    g.add_argument('--out', default=None, help='Salvar resultado em arquivo (json ou csv)')
    g.add_argument('--format', choices=['json', 'csv'], default='json', help='Formato de saída')
    b = sub.add_parser('batch', help='Gerar vários perfis de arquivo')
    b.add_argument('arquivo', help='Arquivo com identificadores (um por linha)')
    b.add_argument('--locale', default='pt_BR')
    b.add_argument('--out', default=None)
    b.add_argument('--format', choices=['json', 'csv'], default='json')
    b.add_argument('--dedupe', action='store_true', help='Remove duplicados do arquivo')
    s = sub.add_parser('stdin', help='Leer identificadores da stdin')
    s.add_argument('--locale', default='pt_BR')
    s.add_argument('--out', default=None)
    s.add_argument('--format', choices=['json', 'csv'], default='json')
    s.add_argument('--dedupe', action='store_true')
    return parser.parse_args()

def main():
    args = parse_args()
    if args.cmd == 'gerar':
        perfil = gerar_perfil(args.identificador, args.locale)
        if args.out:
            if args.format == 'json':
                escrever_json([perfil], args.out)
            else:
                escrever_csv([perfil], args.out)
            print(f"Arquivo gravado: {args.out}")
        else:
            print(json.dumps(perfil, ensure_ascii=False, indent=2))
    elif args.cmd == 'batch':
        if not os.path.exists(args.arquivo):
            print(f"Arquivo não encontrado: {args.arquivo}", file=sys.stderr)
            sys.exit(1)
        ids = ler_identificadores_de_arquivo(args.arquivo)
        if args.dedupe:
            ids = list(dict.fromkeys(ids))
        perfis = [gerar_perfil(i, args.locale) for i in ids]
        if args.out:
            if args.format == 'json':
                escrever_json(perfis, args.out)
            else:
                escrever_csv(perfis, args.out)
            print(f"Arquivo gravado: {args.out}")
        else:
            print(json.dumps(perfis, ensure_ascii=False, indent=2))
    elif args.cmd == 'stdin':
        ids = [line.strip() for line in sys.stdin if line.strip()]
        if args.dedupe:
            ids = list(dict.fromkeys(ids))
        perfis = [gerar_perfil(i, args.locale) for i in ids]
        if args.out:
            if args.format == 'json':
                escrever_json(perfis, args.out)
            else:
                escrever_csv(perfis, args.out)
            print(f"Arquivo gravado: {args.out}")
        else:
            print(json.dumps(perfis, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()