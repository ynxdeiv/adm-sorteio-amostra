# adm-sorteio-amostra

Sorteia ids de participantes de um grupo a partir do `membros_ic.json` gerado pelo [whatsapp-scrap](https://github.com/ynxdeiv/whatsapp-scrap). Um arquivo só, sem dependências.

## Uso

```bash
python3 sortear.py                                # 32 ids: id, papel e contato salvo
python3 sortear.py -n 10 --seed 123               # tamanho e sorteio repetível
python3 sortear.py --formato json                 # imprime o JSON
python3 sortear.py --anonimizar                   # mostra P01…P32 em vez de telefone
python3 sortear.py --relatorio relatorio.json     # grava a trilha de auditoria
python3 sortear.py --salvar sorteio.json          # grava só a lista sorteada
```

O JSON é procurado em `--json`, `./membros_ic.json`, `~/Documents/whatsapp-scrap/saida/membros_ic.json` e `~/Desktop/membros_ic.json`.

```
1023 participantes · seed 4694497217951215973 · 'Contato salvo' do JSON

  #  Codigo  Papel    Contato salvo
  1  P01     membro   Não
```

Amostra uniforme e sem repetição (`random.sample`): cada subconjunto de `n` tem a mesma probabilidade e a seleção não depende da ordem da lista. Com `--seed` o mesmo sorteio sai igual de novo.

## Auditoria

`--relatorio` grava seed, SHA-256 do arquivo, SHA-256 da lista de ids, tamanho do universo, posições dos sorteados e SHA-256 do próprio script. Com isso dá para refazer o sorteio e conferir a integridade do arquivo — `METODOLOGIA.md` traz o passo a passo.

`--anonimizar` mostra códigos `P01`…`P32` e guarda o mapa código → telefone em `sorteio_mapa_<seed>.json`.

## Formato do JSON

Objeto com a lista `participantes` (ou uma lista solta), cada um com `numero`, `papel` e `contatoSalvo` — o formato que o `whatsapp-scrap` gera.

## Aviso

O JSON tem telefone de terceiros: **não comite** e não anexe (`membros_*.json`, `sorteio*.json` e `relatorio*.json` estão no `.gitignore`). No relatório, use a saída `--anonimizar`. Sem garantia de qualquer tipo; licença MIT.
