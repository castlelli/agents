# Claude Code hand-off prompt

Fill `[LISTA DE ARQUIVOS]` with the real filenames (project page first) and translate to the conversation's language if it isn't Portuguese. Keep the bracketed paths for the user to replace.

```
Você vai integrar um conjunto de notas novas ao meu vault do Obsidian (second brain organizado em PARA).

## Contexto
- Vault: [CAMINHO DO VAULT]
- Notas novas: [CAMINHO DA PASTA DESCOMPACTADA]
[LISTA DE ARQUIVOS — uma linha por arquivo, marcando qual é a nota de projeto (template de projeto) e quais são notas atômicas (template de nota completa)]
- Os campos `tags`, `area`, `parent project`, `status` e `deadline` estão vazios de propósito; preenchê-los faz parte da tarefa.

## Tarefa
1. Antes de mover qualquer arquivo, leia a estrutura do vault: pastas PARA, templates, tags existentes, áreas, projetos ativos e convenções de metadados e nomes. Use notas existentes como referência de padrão.
2. Coloque cada nota nova no lugar certo segundo essa estrutura.
3. Preencha os metadados vazios com valores e convenções que já existem no vault.
4. Conecte as notas novas entre si e ao restante do vault da forma que julgar mais adequada.

## Restrições
- NUNCA altere o conteúdo factual do corpo das notas nem a estrutura dos templates.
- NUNCA apague, renomeie ou mova notas que já existem no vault.
- Pare e me pergunte antes de: criar tag, área ou projeto que ainda não existe; editar o corpo de uma nota existente além de adicionar uma conexão; ou escolher entre duas localizações igualmente plausíveis.
- Não crie notas além das fornecidas.

## Pronto quando
- Todas as notas estão no vault com metadados preenchidos só com valores existentes ou aprovados por mim.
- A pasta de origem pode ser descartada sem perda.

Ao terminar, entregue um relatório curto: para cada nota, o caminho final, os metadados atribuídos e as conexões criadas; depois, liste as decisões em que ficou em dúvida.
```
