#!/usr/bin/env python3
"""Sorteia ids de participantes a partir do JSON exportado pelo whatsapp-scrap.

Cada sorteado sai com id, papel e se o contato está salvo.

Exemplos:
    python3 sortear.py
    python3 sortear.py --formato json > sorteados.json
    python3 sortear.py --n 5 --formato ids
    python3 sortear.py --seed 20240911 --salvar sorteio.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from src import dados, sorteio


def simNao(valor):
    return "Sim" if valor else "Não"


def resumoPorPapel(itens):
    contagem = Counter(item["papel"] or "sem papel" for item in itens)
    return " · ".join(
        f"{quantidade} {papel}{'s' if quantidade > 1 else ''}"
        for papel, quantidade in sorted(contagem.items())
    )


def imprimirCabecalho(caminho, campo, papel, seed, universo, itens):
    print(f"Universo: {len(universo)} ids elegíveis pelo campo '{campo}' (papel: {papel or 'todos'})")
    print(f"Arquivo.: {caminho}")
    print(f"Seed....: {seed}")
    print(f"Hash....: {sorteio.hashUniverso(universo)}  (universo, na ordem do arquivo)")
    print(f"Resumo..: {len(itens)} sorteados — {resumoPorPapel(itens)}")
    print()


def imprimirTabela(campo, escolhidos, itens):
    tituloId = "ID" if campo == "numero" else "LID"
    largura = max([len(str(item["id"])) for item in itens] + [len(tituloId)])
    print(f"{'#':>3}  {tituloId:<{largura}}  {'Papel':<7}  Contato salvo")
    for posicao, item in enumerate(itens, 1):
        print(f"{posicao:>3}  {item['id']:<{largura}}  {item['papel']:<7}  {simNao(item['contatoSalvo'])}")


def imprimirDetalhado(escolhidos, itens):
    for posicao, (_, participante) in enumerate(escolhidos, 1):
        item = itens[posicao - 1]
        detalhes = " · ".join(
            parte
            for parte in (
                str(participante.get("numero") or ""),
                str(participante.get("lid") or ""),
                dados.nomeDe(participante),
                item["papel"],
                f"contato salvo: {simNao(item['contatoSalvo'])}",
            )
            if parte
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
    parser.add_argument(
        "--formato",
        choices=("tabela", "json", "ids"),
        default="tabela",
        help="saída: tabela com id/papel/contato salvo, json ou só os ids (padrão: tabela)",
    )
    parser.add_argument("--detalhado", action="store_true", help="na tabela, mostra também lid e nome")
    parser.add_argument("--salvar", help="grava o resultado (com seed e hash) nesse arquivo JSON")
    args = parser.parse_args(argv)

    try:
        caminho = dados.acharJson(args.json)
        universo = dados.elegiveis(dados.carregarParticipantes(caminho), args.campo, args.papel)
        seed, escolhidos = sorteio.sortear(universo, args.n, args.seed)
    except (dados.ErroDeDados, ValueError) as erro:
        parser.error(str(erro))

    itens = [dados.descrever(valor, participante) for valor, participante in escolhidos]

    if args.formato == "ids":
        for item in itens:
            print(item["id"])
    elif args.formato == "json":
        print(json.dumps(itens, ensure_ascii=False, indent=2))
    else:
        imprimirCabecalho(caminho, args.campo, args.papel, seed, universo, itens)
        if args.detalhado:
            imprimirDetalhado(escolhidos, itens)
        else:
            imprimirTabela(args.campo, escolhidos, itens)

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
