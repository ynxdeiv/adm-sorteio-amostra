#!/usr/bin/env python3
"""Sorteia ids de participantes do membros_ic.json (whatsapp-scrap).

--relatorio grava a trilha de auditoria (seed, hashes, posicoes) e --anonimizar
troca os telefones por codigos P01..P32 — o relatorio e o mapa de codigos sao
privados; a tabela anonimizada e o que pode ser anexado.
"""

import argparse
import hashlib
import json
import random
import secrets
from datetime import datetime, timezone
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


def sha256(conteudo):
    return hashlib.sha256(conteudo).hexdigest()


def carregar(caminho):
    conteudo = Path(caminho).read_bytes()
    dados = json.loads(conteudo)
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
    return conteudo, participantes


def posicoesNoUniverso(participantes, sorteados):
    indice = {item["id"]: posicao for posicao, item in enumerate(participantes, 1)}
    return sorted(indice[item["id"]] for item in sorteados)


def anonimizar(itens, codigos):
    return [
        {"codigo": codigos[item["id"]], "papel": item["papel"], "contatoSalvo": item["contatoSalvo"]}
        for item in itens
    ]


def imprimirTabela(itens, codigos, esconderId, seed, total):
    primeira = "Codigo" if esconderId else "ID"
    valores = [codigos[item["id"]] if esconderId else item["id"] for item in itens]
    largura = max([len(valor) for valor in valores] + [len(primeira)])
    print(f"{total} participantes · seed {seed} · 'Contato salvo' do JSON\n")
    print(f"{'#':>3}  {primeira:<{largura}}  {'Papel':<7}  Contato salvo")
    for posicao, (item, valor) in enumerate(zip(itens, valores), 1):
        print(f"{posicao:>3}  {valor:<{largura}}  {item['papel']:<7}  {'Sim' if item['contatoSalvo'] else 'Não'}")


def gravar(caminho, dados):
    Path(caminho).expanduser().write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return caminho


def main():
    parser = argparse.ArgumentParser(description="Sorteia ids de um grupo a partir do JSON do whatsapp-scrap.")
    parser.add_argument("--json", help="caminho do membros_ic.json")
    parser.add_argument("-n", "--n", type=int, default=32, help="quantos ids sortear (padrão: 32)")
    parser.add_argument("--seed", type=int, help="semente, para repetir um sorteio (padrão: aleatória)")
    parser.add_argument("--formato", choices=("tabela", "json"), default="tabela", help="saída")
    parser.add_argument("--salvar", help="grava só a lista sorteada nesse arquivo JSON")
    parser.add_argument("--relatorio", help="grava a trilha de auditoria (seed, hashes, posicoes) nesse arquivo")
    parser.add_argument(
        "--anonimizar",
        action="store_true",
        help="mostra codigos P01..P32 em vez de telefone e grava o mapa num arquivo privado",
    )
    args = parser.parse_args()

    caminho = acharJson(args.json)
    conteudo, participantes = carregar(caminho)
    if args.n > len(participantes):
        raise SystemExit(f"ERRO: pedi {args.n} ids, mas o JSON só tem {len(participantes)} participantes")

    seed = args.seed if args.seed is not None else secrets.randbits(64)
    sorteados = random.Random(seed).sample(participantes, args.n)
    codigos = {item["id"]: f"P{posicao:02d}" for posicao, item in enumerate(sorteados, 1)}

    if args.formato == "json":
        print(json.dumps(anonimizar(sorteados, codigos) if args.anonimizar else sorteados,
                         ensure_ascii=False, indent=2))
    else:
        imprimirTabela(sorteados, codigos, args.anonimizar, seed, len(participantes))

    if args.anonimizar:
        destino = gravar(
            f"sorteio_mapa_{seed}.json",
            {"seed": seed, "codigoParaId": {codigos[item["id"]]: item["id"] for item in sorteados}},
        )
        print(f"\n>> mapa codigo -> telefone (PRIVADO, não anexar): {destino}")

    if args.salvar:
        print(f"\n>> lista sorteada: {gravar(args.salvar, sorteados)}")

    if args.relatorio:
        registro = {
            "geradoEm": datetime.now(timezone.utc).isoformat(),
            "arquivo": str(caminho),
            "sha256Arquivo": sha256(conteudo),
            "sha256Universo": sha256("|".join(item["id"] for item in participantes).encode()),
            "participantesNoUniverso": len(participantes),
            "pedido": args.n,
            "seed": seed,
            "sha256Script": sha256(Path(__file__).read_bytes()),
            "posicoesNoUniverso": posicoesNoUniverso(participantes, sorteados),
            "sorteados": sorteados,
        }
        print(f"\n>> relatorio (PRIVADO, não anexar): {gravar(args.relatorio, registro)}")


if __name__ == "__main__":
    main()
