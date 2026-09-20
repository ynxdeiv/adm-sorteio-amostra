# Metodologia — sorteio da amostra

> **Modelo para preencher e entregar.** Os valores reais estão no `sorteio_relatorio.json`
> (arquivo privado, gerado por `--relatorio`). **Não anexe** ao relatório o JSON de dados nem
> o mapa de códigos: o anexo correto é a tabela anonimizada (códigos `P01`…`P32`).

## 1. Objeto

Sorteio de **<n>** participantes de **<população>** para **<finalidade do estudo>**, realizado em
**<data/hora>**, com o script `sortear.py` (código e hash no item 6).

## 2. Origem dos dados

| Item | Valor |
|---|---|
| Instrumento de coleta | extração local da lista de participantes de um grupo de WhatsApp, lendo a store da própria sessão do WhatsApp Web (`whatsapp-scrap`) |
| Data e hora da captura | `<geradoEm>` (UTC) |
| Versão do WhatsApp Web | `<whatsappWeb>` |
| Grupo | `<nome e id do grupo>` — mantido no arquivo privado |
| Participantes capturados | `<N>` — todos com número resolvido, sem duplicidade |
| SHA-256 do arquivo de dados | `<sha256Arquivo>` |
| Campos utilizados | `numero` (id), `papel`, `contatoSalvo` |

## 3. População e amostra

- **Moldura amostral:** os `<N>` participantes do grupo na data da captura, listados em arquivo local.
- **Tipo:** amostragem **aleatória simples, sem reposição**, sobre a lista completa.
- Cada participante teve probabilidade `32/N` de ser sorteado; todo subconjunto de 32 tinha a mesma
  probabilidade; a seleção **não depende da ordem da lista** — não é amostragem sequencial, sistemática
  nem por conveniência (a seleção foi feita com `random.sample`, que devolve posições espalhadas).
- **Limitações declaradas:** quem entrou ou saiu do grupo depois da captura não tinha chance de ser
  sorteado; as conclusões valem para essa moldura, não automaticamente para toda a comunidade do curso.

## 4. Procedimento

```bash
python3 sortear.py --seed <seed> --relatorio sorteio_relatorio.json --anonimizar
```

Saída: a tabela anonimizada (`P01`…`P32` com papel e contato salvo) e dois arquivos privados
(`sorteio_relatorio.json` e `sorteio_mapa_<seed>.json`).

## 5. Trilha de auditoria

| Campo | Significado |
|---|---|
| `seed` | semente do sorteio; com ela o resultado é reproduzível |
| `sha256Arquivo` | impressão digital do arquivo de dados usado |
| `sha256Universo` | hash da lista de ids elegíveis, na ordem do arquivo |
| `participantesNoUniverso` | tamanho da moldura amostral |
| `pedido` | quantos ids foram sorteados |
| `posicoesNoUniverso` | onde os sorteados estão na lista — evidência de que não são consecutivos |
| `sha256Script` | versão exata do código usado |
| `geradoEm` | data e hora do sorteio (UTC) |

## 6. Protocolo de verificação

Se `sha256Arquivo` = `<sha256Arquivo>`, `sha256Universo` = `<sha256Universo>` e
`sha256Script` = `<sha256Script>`, o item é satisfeito.

1. **Integridade do arquivo:** `shasum -a 256 <arquivo>` → deve dar `<sha256Arquivo>`.
   Em seguida contar os participantes: o arquivo deve ter `<N>` registros com número, sem repetição.
2. **Reprodutibilidade do sorteio:** `python3 sortear.py --json <arquivo> --seed <seed> --anonimizar`
   → deve devolver **os mesmos `P01`…`P32`** (mesmo papel e mesmo contato salvo).
3. **Conferência contra o relatório:** a tabela anonimizada anexada deve ser idêntica à saída do passo 2.
4. **Dados brutos:** a verificação é feita **na máquina do pesquisador**, com o arquivo privado, sem
   transferência de cópia. Registrar em ata, assinada por quem verificou.

## 7. O que este arranjo prova — e o que não prova

**Prova:** que o sorteio foi feito sobre exatamente aquele arquivo (hash), que o procedimento é
reprodutível (seed + código), que a amostra é uniforme sem reposição e que os sorteados não são
consecutivos.

**Não prova:** que o conteúdo do arquivo corresponde a dados reais do grupo — hash garante
**integridade**, não **autenticidade**. Também não impede, por si só, que a semente tenha sido
escolhida depois de conhecido o resultado. Mitigações, em ordem de força:

1. verificação local do arquivo pelo professor/orientador + ata assinada (indício forte de origem);
2. semente derivada de **beacon público** imprevisível (hash de um bloco do Bitcoin ou resultado de
   loteria oficial **posterior** ao fechamento da lista), o que retira de qualquer pessoa o controle
   sobre a semente;
3. registro prévio (por e-mail ou protocolo) do `sha256Arquivo` **antes** do sorteio.

## 8. Proteção de dados (LGPD — confirmar com o orientador / instância de ética)

- **Finalidade e adequação:** a coleta existe para <finalidade>; não é reutilizada para outra coisa.
- **Minimização:** só `numero`, `papel` e `contatoSalvo` são usados; os demais campos do arquivo
  (pushname, verifiedName, flags de business/bloqueio) são ignorados.
- **Base legal:** estudos por órgão de pesquisa (art. 7º, IV) ou legítimo interesse (art. 7º, IX),
  documentado — a ser confirmado com o orientador. Não se trata de dado sensível (art. 5º, II),
  salvo se houver cruzamento que revele dado sensível.
- **Anonimização na divulgação:** no relatório, os participantes aparecem como `P01`…`P32`; o mapa
  código → telefone fica em arquivo local, sob guarda do pesquisador.
- **Segurança e não compartilhamento:** arquivos em máquina local, sem envio para nuvem; o repositório
  público do script **não contém dados** (verificável — só código e documentação).
- **Atenção específica:** o campo `descricao` do arquivo de dados contém o **link de convite** do grupo;
  se o arquivo circular, qualquer pessoa pode ingressar no grupo. Por isso o arquivo bruto não é anexado.
- **Retenção:** `<prazo ou evento>` — apagar o arquivo de dados e o mapa de códigos ao final
  (<ex.: conclusão do estudo / publicação>), mantendo apenas a tabela anonimizada e os hashes.

## 9. Anexos

1. Tabela anonimizada dos sorteados (`P01`…`P32`, papel, contato salvo).
2. `sortear.py` e seu `sha256` (`<sha256Script>`).
3. Hashes e seed (item 5) — o suficiente para auditoria, **sem** os dados pessoais.
