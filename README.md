# adm-sorteio-amostra

Sorteia ids de participantes de um grupo do WhatsApp a partir do JSON gerado pelo [whatsapp-scrap](https://github.com/ynxdeiv/whatsapp-scrap) — ou de qualquer JSON no mesmo formato.

Feito para sorteio e amostragem interna: mostra o resultado na tela, deixa **repetir** um sorteio exatamente pela seed e grava um registro com prova de auditoria.

## ⚠️ Antes de usar

- O JSON de entrada contém **dados pessoais** (telefones de terceiros). Este repositório é público e **não** traz nenhum dado real: o `.gitignore` bloqueia `membros_*.json` e o arquivo em `exemplos/` é sintético. Não comite dados de participantes.
- O sorteio é uniforme e sem repetição, mas usa o `random` do Python (Mersenne Twister) com seed vinda de `secrets`. Serve para sorteio/amostra interna; se houver alguém com interesse em fraudar o resultado, use uma ferramenta com prova pública de aleatoriedade.

## Requisitos

Python 3.9 ou mais novo. Nenhuma dependência externa.

## Uso

```bash
python3 sortear.py                          # 32 ids entre todos (tabela: id, papel, contato salvo)
python3 sortear.py --formato json           # imprime só o JSON do sorteio
python3 sortear.py --formato ids            # só os ids, um por linha
python3 sortear.py --n 5 --campo lid        # sorteia LIDs em vez de telefones
python3 sortear.py --papel admin            # restringe o sorteio a um papel
python3 sortear.py --seed 20240911          # repete exatamente um sorteio anterior
python3 sortear.py --detalhado              # tabela com lid e nome também
python3 sortear.py --salvar sorteio.json    # grava o registro (seed + hash + sorteados)
```

Saída padrão:

```
Universo: 1023 ids elegíveis pelo campo 'numero' (papel: todos)
Arquivo.: /caminho/membros_ic.json
Seed....: 12345678901234567890
Hash....: 4f2a9c1b7e8d3a05  (universo, na ordem do arquivo)
Resumo..: 32 sorteados — 30 membros · 2 admins

  #  ID             Papel    Contato salvo
  1  5571900000001  admin    Sim
  2  5571900000002  membro   Não
```

Cada sorteado sai com **id, papel e se o contato está salvo** — os mesmos três campos no JSON (`--formato json`) e no registro (`--salvar`). Com `--detalhado`, a tabela também traz lid e nome.

O JSON de entrada é procurado nesta ordem: `--json`, `./membros_ic.json`, `~/Documents/whatsapp-scrap/saida/membros_ic.json`, `~/Desktop/membros_ic.json`.

### Opções

| Opção | Padrão | O que faz |
|---|---|---|
| `--json CAMINHO` | busca nos locais acima | JSON de entrada |
| `-n`, `--n N` | `32` | Quantos ids sortear |
| `--campo {numero,lid}` | `numero` | Campo usado como id do participante |
| `--papel PAPEL` | todos | Sorteia só entre quem tem esse `papel` (ex.: `admin`) |
| `--seed N` | aleatória | Semente para repetir um sorteio |
| `--formato {tabela,json,ids}` | `tabela` | Forma da saída: tabela com id/papel/contato salvo, JSON do sorteio, ou só os ids |
| `--detalhado` | desligado | Na tabela, mostra também lid e nome |
| `--salvar CAMINHO` | não grava | Grava o resultado em JSON, com seed e hash |

### Códigos de saída

| Código | Quando |
|---|---|
| `0` | Sorteio feito |
| `2` | Erro de uso ou de entrada: JSON ausente/inválido/sem participantes, `--n` maior que o universo, `--n` menor que 1 |

## Formato esperado do JSON

Aceita o objeto exportado pelo `whatsapp-scrap` (lista dentro de `participantes`) ou uma lista solta de participantes. Os campos usados:

| Campo | Uso |
|---|---|
| `numero` | Telefone (padrão do sorteio) — ex.: `5571900000001` |
| `lid` | Id interno do WhatsApp, quando `--campo lid` |
| `papel` | `membro`, `admin` ou `superadmin`; sai na saída e serve de filtro no `--papel` |
| `contatoSalvo` | `true`/`false`; sai na saída como `Sim`/`Não` |
| `nomeAgenda`, `nomeParticipante`, `pushname`, `notifyName`, `shortName`, `verifiedName` | Primeiro preenchido vira o nome exibido |

Participantes sem o campo escolhido (ou repetido) são ignorados: o universo é sempre de ids **distintos**.

## Como funciona

1. Lê o JSON e monta o universo de ids distintos, na ordem do arquivo.
2. Aplica o filtro de `--papel`, se houver.
3. Sorteia com `random.Random(seed).sample(...)` — amostra **uniforme e sem reposição** (ninguém sai duas vezes).
4. Imprime o `id`, o `papel` e o `contatoSalvo` de cada sorteado e, com `--salvar`, grava o registro.

## Saída em JSON

`--formato json` imprime exatamente isto (um objeto por sorteado):

```json
[
  { "id": "5571900000001", "papel": "admin", "contatoSalvo": true },
  { "id": "5571900000002", "papel": "membro", "contatoSalvo": false }
]
```

`--salvar arquivo.json` grava a mesma lista dentro de `sorteados`, junto com os dados de auditoria (seed, hash, campo, papel, data):

```json
{
  "geradoEm": "2026-09-20T22:00:00+00:00",
  "arquivoOrigem": "/caminho/membros_ic.json",
  "campo": "numero",
  "papel": null,
  "seed": 12535001914905072965,
  "pedido": 32,
  "universo": 1023,
  "hashUniverso": "2cf024f6bfd91673",
  "sorteados": [
    { "id": "5571900000001", "papel": "admin", "contatoSalvo": true }
  ]
}
```

## Auditoria

Cada sorteio imprime a **seed** usada e o **hash do universo** (SHA-256 dos ids elegíveis, na ordem do arquivo, truncado em 16 caracteres). Com isso:

- **Repetir o sorteio:** a mesma seed + o mesmo JSON devolvem exatamente o mesmo resultado.
- **Provar que o universo não mudou:** recalcule o hash depois; se bater, a lista de participantes não foi alterada.
- **Registro:** `--salvar` guarda seed, hash, campo, papel, quantidade e os sorteados (`id`, `numero`, `lid`, `nome`, `papel`) com data em UTC.

## Estrutura

```
adm-sorteio-amostra/
├── sortear.py              # entrada: linha de comando
├── src/
│   ├── dados.py            # acha e lê o JSON, monta o universo de elegíveis
│   └── sorteio.py          # sorteio e registro de auditoria
├── testes/
│   └── test_sorteio.py     # 22 testes (unittest, sem dependências)
├── exemplos/
│   └── exemplo.json        # JSON sintético, para testar sem dado real
├── LICENSE
└── README.md
```

## Testes

```bash
python3 -m unittest discover -s testes -t .
```

Os testes cobrem leitura/deduplicação/filtro do universo, reprodutibilidade por seed, erro quando se pede mais ids do que existem, formato do registro e a linha de comando de ponta a ponta (usando `exemplos/exemplo.json`) — nenhum teste depende de dado real.

## Licença

MIT — veja [LICENSE](LICENSE).
