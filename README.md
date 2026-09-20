# adm-sorteio-amostra

Sorteia ids de participantes de um grupo a partir do `membros_ic.json` gerado pelo [whatsapp-scrap](https://github.com/ynxdeiv/whatsapp-scrap). Um arquivo só, sem dependências.

## Uso

```bash
python3 sortear.py                        # 32 ids: id, papel e contato salvo
python3 sortear.py -n 10 --seed 123       # tamanho e sorteio repetível
python3 sortear.py --formato json         # imprime o JSON
python3 sortear.py --salvar sorteio.json  # grava o JSON num arquivo
```

O JSON é procurado em `--json`, `./membros_ic.json`, `~/Documents/whatsapp-scrap/saida/membros_ic.json` e `~/Desktop/membros_ic.json`.

```
#  ID             Papel    Contato salvo
1  557182066144   membro   Sim
```

Amostra uniforme e sem repetição (`random.sample`). Com `--seed` o mesmo sorteio sai igual de novo.

## Formato do JSON

Objeto com a lista `participantes` (ou uma lista solta), cada um com `numero`, `papel` e `contatoSalvo` — o formato que o `whatsapp-scrap` gera.

## Aviso

O JSON tem telefone de terceiros: **não comite** (o `.gitignore` bloqueia `membros_*.json`). Sem garantia de qualquer tipo; licença MIT.
