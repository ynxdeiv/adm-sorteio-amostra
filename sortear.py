#!/usr/bin/env python3
"""Sorteia participantes do membros_ic.json (whatsapp-scrap).

O id de cada sorteado e a posicao dele no arquivo (1..N), nao o telefone: a saida
pode ser anexada sem expor ninguem. O telefone sai separado, no mapa privado.
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
    for posicao, bruto in enumerate(lista, 1):
        telefone = str(bruto.get("numero") or "")
        if not telefone or telefone in vistos:
            continue
        vistos.add(telefone)
        participantes.append(
            {
                "id": posicao,
                "papel": str(bruto.get("papel") or ""),
                "contatoSalvo": bool(bruto.get("contatoSalvo")),
                "telefone": telefone,
            }
        )
    if not participantes:
        raise SystemExit(f"ERRO: nenhum participante com numero em {caminho}")
    return conteudo, participantes


def publico(sorteado):
    return {"id": sorteado["id"], "papel": sorteado["papel"], "contatoSalvo": sorteado["contatoSalvo"]}


def imprimirTabela(sorteados, seed, total):
    largura = max(len(str(item["id"])) for item in sorteados)
    print(f"{total} participantes · seed {seed}\n")
    print(f"{'#':>3}  {'ID':>{largura}}  {'Papel':<7}  Contato salvo")
    for ordem, item in enumerate(sorteados, 1):
        print(
            f"{ordem:>3}  {item['id']:>{largura}}  {item['papel']:<7}  "
            f"{'Sim' if item['contatoSalvo'] else 'Não'}"
        )


def gravar(caminho, dados):
    Path(caminho).expanduser().write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return caminho


def main():
    parser = argparse.ArgumentParser(description="Sorteia participantes de um grupo a partir do JSON do whatsapp-scrap.")
    parser.add_argument("--json", help="caminho do membros_ic.json")
    parser.add_argument("-n", "--n", type=int, default=32, help="quantos sortear (padrão: 32)")
    parser.add_argument("--seed", type=int, help="semente, para repetir um sorteio (padrão: aleatória)")
    parser.add_argument("--formato", choices=("tabela", "json"), default="tabela", help="saída")
    parser.add_argument("--relatorio", help="grava a trilha de auditoria (seguro anexar: sem telefone)")
    parser.add_argument("--mapa", help="grava id -> telefone (PRIVADO, não anexar)")
    args = parser.parse_args()

    caminho = acharJson(args.json)
    conteudo, participantes = carregar(caminho)
    if args.n > len(participantes):
        raise SystemExit(f"ERRO: pedi {args.n}, mas o JSON só tem {len(participantes)} participantes")

    seed = args.seed if args.seed is not None else secrets.randbits(64)
    sorteados = random.Random(seed).sample(participantes, args.n)

    if args.formato == "json":
        print(json.dumps([publico(item) for item in sorteados], ensure_ascii=False, indent=2))
    else:
        imprimirTabela(sorteados, seed, len(participantes))

    if args.relatorio:
        registro = {
            "geradoEm": datetime.now(timezone.utc).isoformat(),
            "arquivoOrigem": Path(caminho).name,
            "participantesNoUniverso": len(participantes),
            "pedido": args.n,
            "metodo": "amostragem aleatória simples, sem reposição (random.sample)",
            "algoritmoDeResumo": "SHA-256",
            "seed": seed,
            "sha256Arquivo": sha256(conteudo),
            "sha256Universo": sha256("|".join(item["telefone"] for item in participantes).encode()),
            "sha256Script": sha256(Path(__file__).read_bytes()),
            "comandoParaReproduzir": f"python3 sortear.py --json <arquivo> --seed {seed}",
            "idsSorteados": sorted(item["id"] for item in sorteados),
            "sorteados": [publico(item) for item in sorteados],
            "confidencialidade": {
                "dadosPessoaisNesteArquivo": False,
                "identificadores": "posições (1..N) no arquivo de origem, na ordem em que os participantes aparecem",
                "arquivoDeOrigem": "mantido sob guarda do pesquisador; não anexado",
                "mapaIdTelefone": "arquivo separado e privado; não anexado",
                "observacao": "os hashes permitem verificar integridade e refazer o sorteio sem revelar os dados",
            },
        }
        print(f"\n>> relatorio (seguro anexar): {gravar(args.relatorio, registro)}")

    if args.mapa:
        print(
            f">> mapa id -> telefone (PRIVADO, não anexar): "
            f"{gravar(args.mapa, {'seed': seed, 'idParaTelefone': {str(item['id']): item['telefone'] for item in sorteados}})}"
        )


if __name__ == "__main__":
    main()
