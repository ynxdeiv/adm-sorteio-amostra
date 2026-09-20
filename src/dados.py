"""Leitura do JSON de participantes e montagem do universo do sorteio."""

from __future__ import annotations

import json
from pathlib import Path

CAMPOS = ("numero", "lid")

CAMPOS_NOME = (
    "nomeAgenda",
    "nomeParticipante",
    "pushname",
    "notifyName",
    "shortName",
    "verifiedName",
)

LOCAIS_PADRAO = (
    Path.cwd() / "membros_ic.json",
    Path.home() / "Documents" / "whatsapp-scrap" / "saida" / "membros_ic.json",
    Path.home() / "Desktop" / "membros_ic.json",
)


class ErroDeDados(Exception):
    """JSON ausente, ilegível ou em formato inesperado."""


def acharJson(explicito=None):
    if explicito:
        caminho = Path(explicito).expanduser()
        if not caminho.is_file():
            raise ErroDeDados(f"não achei o JSON em {caminho}")
        return caminho
    for caminho in LOCAIS_PADRAO:
        if caminho.is_file():
            return caminho
    raise ErroDeDados("não achei nenhum JSON; passe o caminho com --json")


def carregarParticipantes(caminho):
    caminho = Path(caminho)
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError as erro:
        raise ErroDeDados(f"não achei o arquivo {caminho}") from erro
    except json.JSONDecodeError as erro:
        raise ErroDeDados(f"{caminho} não é um JSON válido ({erro})") from erro

    if isinstance(dados, list):
        participantes = dados
    elif isinstance(dados, dict):
        participantes = dados.get("participantes") or dados.get("membros") or []
    else:
        raise ErroDeDados(f"formato inesperado em {caminho}: esperava lista ou objeto")

    if not participantes:
        raise ErroDeDados(f"nenhum participante encontrado em {caminho}")
    return participantes


def nomeDe(participante):
    for campo in CAMPOS_NOME:
        if participante.get(campo):
            return str(participante[campo])
    return "(sem nome)"


def elegiveis(participantes, campo, papel=None):
    vistos = set()
    universo = []
    for participante in participantes:
        if papel and participante.get("papel") != papel:
            continue
        valor = str(participante.get(campo) or "").strip()
        if not valor or valor in vistos:
            continue
        vistos.add(valor)
        universo.append((valor, participante))
    return universo


def descrever(valor, participante):
    return {
        "id": valor,
        "numero": str(participante.get("numero") or ""),
        "lid": str(participante.get("lid") or ""),
        "nome": nomeDe(participante),
        "papel": str(participante.get("papel") or ""),
    }
