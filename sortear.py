#!/usr/bin/env python3
"""Sorteia ids de participantes a partir do JSON exportado pelo whatsapp-scrap.

Exemplos:
    python3 sortear.py
    python3 sortear.py --n 5 --campo lid
    python3 sortear.py --seed 20240911 --apenas-ids > sorteados.txt
    python3 sortear.py --papel admin --salvar sorteio_admins.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src import dados, sorteio


def imprimir(caminho, campo, papel, seed, universo, escolhidos):
    print(f"Universo: {len(universo)} ids elegíveis pelo campo '{campo}' (papel: {papel or 'todos'})")
    print(f"Arquivo.: {caminho}")
    print(f"Seed....: {seed}")
    print(f"Hash....: {sorteio.hashUniverso(universo)}  (universo, na ordem do arquivo)")
    print()
    for posicao, (valor, participante) in enumerate(escolhidos, 1):
        item = dados.descrever(valor, participante)
        detalhes = " · ".join(
            parte for parte in (item["numero"], item["lid"], item["nome"], item["papel"]) if parte
        )
        print(f"{posicao:>4}. {detalhes}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Sorteia ids distintos de participantes de um JSON do whatsapp-scrap.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json", help="caminho do JSON (padrão: procura membros_ic.json em locais conhecidos)")
    parser.add_argument("-n", "--n", type=int, default=32, help="quantos ids sortear (padrão: 32)")
    parser.add_argument(
        "--campo", choices=dados.CAMPOS, default="numero", help="campo usado como id (padrão: numero)"
    )
    parser.add_argument("--papel", help="sorteia só quem tem esse papel (ex.: admin, membro)")
    parser.add_argument("--seed", type=int, help="semente para repetir um sorteio (padrão: aleatória)")
    parser.add_argument("--apenas-ids", action="store_true", help="imprime só os ids, um por linha")
    parser.add_argument("--salvar", help="grava o resultado (com seed e hash) nesse arquivo JSON")
    args = parser.parse_args(argv)

    try:
        caminho = dados.acharJson(args.json)
        universo = dados.elegiveis(dados.carregarParticipantes(caminho), args.campo, args.papel)
        seed, escolhidos = sorteio.sortear(universo, args.n, args.seed)
    except (dados.ErroDeDados, ValueError) as erro:
        parser.error(str(erro))

    if args.apenas_ids:
        for valor, _ in escolhidos:
            print(valor)
    else:
        imprimir(caminho, args.campo, args.papel, seed, universo, escolhidos)

    if args.salvar:
        registro = sorteio.montarRegistro(
            caminho, args.campo, args.papel, seed, args.n, universo, escolhidos
        )
        destino = Path(args.salvar).expanduser()
        destino.write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nRegistro salvo em {destino}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
