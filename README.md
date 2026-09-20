# adm-sorteio-amostra

Sorteia participantes de um grupo a partir do `membros_ic.json` gerado pelo [whatsapp-scrap](https://github.com/ynxdeiv/whatsapp-scrap). Um arquivo só, sem dependências.

O id de cada sorteado é a **posição dele no arquivo** (1..N), não o telefone — assim a tabela pode ser anexada sem expor ninguém. O telefone sai separado, no mapa privado.

## Uso

```bash
python3 sortear.py                             # 32 ids: id, papel e contato salvo
python3 sortear.py -n 10 --seed 123            # tamanho e sorteio repetível
python3 sortear.py --formato json              # imprime o JSON
python3 sortear.py --relatorio relatorio.json  # trilha de auditoria (seguro anexar)
python3 sortear.py --mapa mapa.json            # id -> telefone (PRIVADO, não anexar)
```

O JSON é procurado em `--json`, `./membros_ic.json`, `~/Documents/whatsapp-scrap/saida/membros_ic.json` e `~/Desktop/membros_ic.json`.

```
1023 participantes · seed 4694497217951215973

  #   ID  Papel    Contato salvo
  1    7  membro   Não
  2   24  membro   Sim
```

Amostra uniforme e sem repetição (`random.sample`): cada subconjunto de `n` tem a mesma probabilidade e a seleção não depende da ordem da lista. Com `--seed` o mesmo sorteio sai igual de novo.

## Auditoria

`--relatorio` grava seed, SHA-256 do arquivo, SHA-256 da lista de ids, tamanho do universo, os ids sorteados e o SHA-256 do próprio script — dá para refazer o sorteio e conferir a integridade do arquivo. O passo a passo está no `METODOLOGIA.md`.

## Formato do JSON

Objeto com a lista `participantes` (ou uma lista solta), cada um com `numero`, `papel` e `contatoSalvo` — o formato que o `whatsapp-scrap` gera. A posição na lista é o id do sorteio.

## Aviso

O JSON tem telefone de terceiros: **não comite** e não anexe (`membros_*.json`, `sorteio*.json` e `relatorio*.json` estão no `.gitignore`). No relatório, use a saída padrão — que já é anônima. Sem garantia de qualquer tipo; licença MIT.
