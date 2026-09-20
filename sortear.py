#!/usr/bin/env python3
"""Sorteia ids de participantes do membros_ic.json (whatsapp-scrap)."""

import argparse
import json
import random
import secrets
from pathlib import Path

PADROES = (
    Path.cwd() / "membros_ic.json",
    Path.home() / "Documents" / "whatsapp-scrap" / "saida" / "membros_ic.json",
    Path.home() / "Desktop" / "membros_ic.json",
)


def acharJson(explicito):
    if explicito:
        return Path(explicito).expanduser()
    for caminho in PADROES:
        if caminho.is_file():
            return caminho
    raise SystemExit("ERRO: não achei o JSON; passe o caminho com --json")


def universo(caminho):
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    lista = dados if isinstance(dados, list) else dados.get("participantes", [])
    vistos = set()
    participantes = []
    for bruto in lista:
        numero = str(bruto.get("numero") or "")
        if numero and numero not in vistos:
            vistos.add(numero)
            participantes.append(
                {
                    "id": numero,
                    "papel": str(bruto.get("papel") or ""),
                    "contatoSalvo": bool(bruto.get("contatoSalvo")),
                }
            )
    if not participantes:
        raise SystemExit(f"ERRO: nenhum participante com numero em {caminho}")
    return participantes


def main():
    parser = argparse.ArgumentParser(description="Sorteia ids de um grupo a partir do JSON do whatsapp-scrap.")
    parser.add_argument("--json", help="caminho do membros_ic.json")
    parser.add_argument("-n", "--n", type=int, default=32, help="quantos ids sortear (padrão: 32)")
    parser.add_argument("--seed", type=int, help="semente, para repetir um sorteio (padrão: aleatória)")
    parser.add_argument("--formato", choices=("tabela", "json"), default="tabela", help="saída")
    parser.add_argument("--salvar", help="grava o resultado nesse arquivo JSON")
    args = parser.parse_args()

    participantes = universo(acharJson(args.json))
    if args.n > len(participantes):
        raise SystemExit(f"ERRO: pedi {args.n} ids, mas o JSON só tem {len(participantes)} participantes")

    seed = args.seed if args.seed is not None else secrets.randbits(64)
    sorteados = random.Random(seed).sample(participantes, args.n)

    if args.formato == "json":
        print(json.dumps(sorteados, ensure_ascii=False, indent=2))
    else:
        print(f"{len(participantes)} participantes · seed {seed}\n")
        print(f"{'#':>3}  {'ID':<13}  {'Papel':<7}  Contato salvo")
        for posicao, item in enumerate(sorteados, 1):
            print(
                f"{posicao:>3}  {item['id']:<13}  {item['papel']:<7}  "
                f"{'Sim' if item['contatoSalvo'] else 'Não'}"
            )

    if args.salvar:
        destino = Path(args.salvar).expanduser()
        destino.write_text(json.dumps(sorteados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nsalvo em {destino}")


if __name__ == "__main__":
    main()
