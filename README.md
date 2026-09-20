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
python3 sortear.py                          # 32 ids pelo campo `numero`
python3 sortear.py --n 5 --campo lid        # sorteia LIDs em vez de telefones
python3 sortear.py --papel admin            # sorteia só entre os administradores
python3 sortear.py --seed 20240911          # repete exatamente um sorteio anterior
python3 sortear.py --apenas-ids > sorteados.txt
python3 sortear.py --salvar sorteio.json    # grava o registro (seed + hash + sorteados)
```

Saída padrão:

```
Universo: 1023 ids elegíveis pelo campo 'numero' (papel: todos)
Arquivo.: /caminho/membros_ic.json
Seed....: 12345678901234567890
Hash....: 4f2a9c1b7e8d3a05  (universo, na ordem do arquivo)

   1. 5571900000001 · 100000000000001 · Ana Exemplo · admin
   2. 5571900000002 · 100000000000002 · Bia Exemplo · membro
```

O JSON de entrada é procurado nesta ordem: `--json`, `./membros_ic.json`, `~/Documents/whatsapp-scrap/saida/membros_ic.json`, `~/Desktop/membros_ic.json`.

### Opções

| Opção | Padrão | O que faz |
|---|---|---|
| `--json CAMINHO` | busca nos locais acima | JSON de entrada |
| `-n`, `--n N` | `32` | Quantos ids sortear |
| `--campo {numero,lid}` | `numero` | Campo usado como id do participante |
| `--papel PAPEL` | todos | Sorteia só entre quem tem esse `papel` (ex.: `admin`) |
| `--seed N` | aleatória | Semente para repetir um sorteio |
| `--apenas-ids` | desligado | Imprime só os ids, um por linha (bom para copiar/colar) |
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
| `papel` | `membro`, `admin` ou `superadmin`; filtro do `--papel` |
| `nomeAgenda`, `nomeParticipante`, `pushname`, `notifyName`, `shortName`, `verifiedName` | Primeiro preenchido vira o nome exibido |

Participantes sem o campo escolhido (ou repetido) são ignorados: o universo é sempre de ids **distintos**.

## Como funciona

1. Lê o JSON e monta o universo de ids distintos, na ordem do arquivo.
2. Aplica o filtro de `--papel`, se houver.
3. Sorteia com `random.Random(seed).sample(...)` — amostra **uniforme e sem reposição** (ninguém sai duas vezes).
4. Imprime o resultado e, com `--salvar`, grava o registro.

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
│   └── test_sorteio.py     # 17 testes (unittest, sem dependências)
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
