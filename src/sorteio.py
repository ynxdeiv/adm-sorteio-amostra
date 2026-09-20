"""Regra do sorteio: amostra uniforme sem repetição, com registro auditável."""

from __future__ import annotations

import hashlib
import random
import secrets
from datetime import datetime, timezone

from . import dados


def hashUniverso(universo):
    texto = "|".join(valor for valor, _ in universo)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


def sortear(universo, quantidade, seed=None):
    if quantidade < 1:
        raise ValueError("a quantidade precisa ser pelo menos 1")
    if quantidade > len(universo):
        raise ValueError(f"pedi {quantidade} ids, mas só existem {len(universo)} elegíveis")
    if seed is None:
        seed = secrets.randbits(64)
    escolhidos = random.Random(seed).sample(universo, quantidade)
    return seed, escolhidos


def montarRegistro(caminho, campo, papel, seed, pedido, universo, escolhidos, quando=None):
    momento = quando or datetime.now(timezone.utc)
    return {
        "geradoEm": momento.isoformat(),
        "arquivoOrigem": str(caminho),
        "campo": campo,
        "papel": papel,
        "seed": seed,
        "pedido": pedido,
        "universo": len(universo),
        "hashUniverso": hashUniverso(universo),
        "sorteados": [dados.descrever(valor, participante) for valor, participante in escolhidos],
    }
