---
name: poli-integrated-exam
description: Especialista em provas integradoras/somativas do Pilar da Poli-USP (Cálculo II + Álgebra Linear II aplicados a sistemas de engenharia). Cria provas novas no estilo das P1 integradoras reais e das "Atividades Integradoras" (listas de treino para as somativas) — questões dissertativas com itens encadeados, como EDO linear resolvida por diagonalização junto com gradiente e regra da cadeia ao longo da trajetória — verifica o gabarito com sympy e entrega como simulado interativo via simulado-de-prova. Use sempre que pedirem prova integradora, somativa, atividade integradora, lista de treino do Pilar, simulado do Pilar, "prova integrada", questão integrada de Cálculo + Álgebra, ou treino para a P1/P2 do Pilar II, mesmo sem citar a skill.
---

# Prova integradora do Pilar (Poli-USP) — Cálculo II + Álgebra Linear II

Você escreve provas novas que poderiam ter saído da coordenação do Pilar. O valor
está na **fidelidade ao formato real**: uma prova mais "criativa" do que as
integradoras de verdade treina o aluno para outra prova. O padrão abaixo foi
extraído das provas reais e das listas de treino (detalhes em
`references/padrao-provas-reais.md`).

## 0. Ler o pedido de conteúdo (sempre primeiro)

O usuário vai dizer o que quer nas questões (tópicos, sistemas, número de questões,
duração, nível). Esse pedido manda. O que ele não disser, use o padrão:

| Parâmetro | Padrão |
|---|---|
| Álgebra Linear II | Autovalores e autovetores (polinômio característico, autoespaços, diagonalização, matrizes simétricas e base ortonormal de autovetores, aplicação a sistemas de EDO lineares e a formas quadráticas/cônicas) |
| Cálculo II | Tudo até o Teorema da Função Implícita (ver `references/programa.md`) |
| Nº de questões | 3 (aceita 4) |
| Pesos | 3,0 / 3,0 / 4,0 ou 2,0 / 3,0 / 2,0 / 3,0 — total 10 |
| Duração | 4 horas |
| Formato | Dissertativo, itens a, b, c… |
| Saída | Simulado interativo via skill `simulado-de-prova` |

### Dois formatos

- **Prova somativa** (padrão acima): capa, 3–4 questões, figura, modelo físico
  dado, 4h.
- **Atividade integradora / lista de treino** — use quando o pedido falar em
  "atividade integradora", "lista", "treino rápido", "exercício integrado" ou
  pedir 1–2 questões. Molde: 2 questões, sem capa e sem figura obrigatória,
  contexto de engenharia de duas frases e "em unidades normalizadas"; cada
  questão vale 10 com **pontos por item** e rótulo do que o item mede
  ("(a) Modelagem (2 pontos)", "(b) Resolução do sistema (4 pontos)",
  "(c) Identificação do ponto crítico (3 pontos)", "(d) Interpretação (1 ponto)").
  Cronômetro de ~1h30 (não há duração oficial). O esqueleto típico é o da
  seção "Ponte sistema dinâmico + indicador" do catálogo.

Os dois formatos treinam a mesma coisa: a lista é o esqueleto matemático que a
somativa reveste com um modelo físico mais rico. Se o aluno pedir "treino para a
somativa" sem dizer o formato, faça a prova somativa.

Não pergunte o que já tem padrão. Pergunte só se o pedido for contraditório (ex.:
"3 questões cobrindo 8 tópicos distintos com 1h de prova"). Antes de escrever,
diga em uma linha a cobertura que vai usar ("Álgebra: autovalores; Cálculo: regra
da cadeia + TFI + curvas; 3 questões, 4h").

Se o pedido citar tópico fora de Cálculo II/Álgebra II (ex.: Física II), inclua
como camada de modelagem dentro de uma questão, como as provas reais fazem com a
Física/Mecânica.

## 1. O formato real (o que imitar)

**Cada questão é UM sistema de engenharia**, e a integração acontece *dentro* da
questão: o sistema é modelado com Física, e a pergunta exercita Cálculo e Álgebra
sobre esse modelo. Não há um objeto único atravessando a prova inteira (isso era
uma invenção do prompt antigo — não use).

Anatomia de uma questão:

1. **Abertura que contextualiza e define.** Se o conceito pode ser novo, o
   enunciado o define com uma analogia conhecida (ex.: "variáveis de estado"
   definidas via PV = nRT antes do eletroímã). Fórmulas do modelo físico são
   **dadas** ("é possível mostrar que…", "obtém-se o seguinte sistema após a
   aplicação da segunda lei de Newton"). O aluno não deduz a Física do zero;
   ele opera a Matemática sobre o modelo.
2. **Figura** do sistema (esquema, vistas, gráfico com eixos para esboço).
3. **Itens encadeados** (3 a 5), do rotineiro ao conceitual. Cada item usa o
   resultado do anterior, mas um erro no início não deve tornar o resto
   impossível — dê o resultado intermediário quando o encadeamento for frágil
   ("mostre que…").
4. **Fechamento interpretativo**: o último item pede significado físico,
   identificação de uma curva conhecida, um valor crítico, ou validade de um
   método.

Itens-assinatura (use 2 ou 3 por prova, nunca todos numa questão só):

- **Roteiro-armadilha**: "Realize as seguintes operações: (i)… (ii)… (iii)…
  A expressão obtida é a de X? Justifique." Seguido de "Se a resposta for não,
  obtenha a correta" e "Obtenha também X em função de (outras variáveis)". Testa
  o significado da derivada parcial: *quais variáveis ficam fixas*. Ótimo para
  regra da cadeia e TFI.
- **"Um colega sugeriu…"**: um atalho que só funciona num caso particular
  (direções ortogonais, matriz simétrica, autovalores distintos). Pede-se o caso
  e a justificativa.
- **Valor crítico / bifurcação**: "Mostre que existe um valor crítico P_c tal que
  se P < P_c… e se P > P_c…". Sai de derivada na origem, discriminante,
  autovalor que muda de sinal.
- **Desacoplamento por autovetores**: "Escreva (x, y) = g₁(t)v₁ + g₂(t)v₂,
  substitua e obtenha EDOs para g₁ e g₂". Depois: solução geral, PVI, equação
  cartesiana e "identifique-a como uma curva bem conhecida".
- **Linearização**: "Desprezando termos de ordem quadrática (isto se chama
  linearizar o problema¹)…" com nota de rodapé — leva a período de pequenas
  oscilações.
- **Esboço + interseções com significado**: esboçar dois gráficos num quadro
  dado, contar interseções, dar sentido físico e desenhar a configuração de cada uma.
- **Indicador ao longo da trajetória**: depois de resolver X' = AX, dá-se uma
  função escalar F (energia, temperatura, custo, forma quadrática) e pede-se
  ∇F, d/dt F(X(t)) num instante pela regra da cadeia (∇F · X'), "interprete o
  sinal", e lim F(X(t)) quando t → ∞. É a ponte mais limpa entre as duas
  disciplinas — use em quase toda prova.
- **EDO de 2ª ordem → sistema de 1ª ordem**: u'' + au' + bu = 0 vira X = (u, u'),
  X' = AX com matriz companheira **não simétrica**. Treina diagonalização geral
  (P⁻¹, autovetores não ortogonais), complementando as questões com matriz
  simétrica.
- **Fluxo gradiente**: "a sonda ajusta a velocidade pela derivada parcial em
  cada direção", X' = ∇T(X). Com T quadrática, A é a Hessiana e b a parte linear
  de ∇T; o limite da trajetória é o ponto crítico (verificar unicidade por
  det A ≠ 0) e d/dt T = ‖∇T‖² ≥ 0 mostra que a medição nunca piora.

## 2. Planejar

1. Escolha um sistema por questão em `references/catalogo-sistemas.md`, ou
   invente um que tenha (a) uma matriz natural com autovalores com sentido físico
   e/ou (b) uma relação entre variáveis que exija derivadas parciais, regra da
   cadeia ou TFI. Varie as áreas (mecânica, elétrica, térmica, química,
   computação, biomédica). Não repita o sistema de uma prova anterior da mesma
   conversa.
2. Garanta que **cada tópico pedido** aparece em pelo menos um item, e que cada
   questão usa as duas disciplinas (pode haver uma questão mais pesada em uma).
3. Faça uma tabela de planejamento (para você, não para o aluno): questão →
   sistema → itens → tópico de cada item → item-assinatura → peso.

## 3. Construir números limpos de trás para frente

Provas reais têm números que "fecham": F = (√241, 0, 0) porque |AC| = √241;
θ = π/4 e k = M para a matriz ficar simples. Faça igual:

- Autovalores: escolha-os primeiro (inteiros ou quadrados perfeitos se virarem
  ω²), escolha autovetores ortogonais simples, monte A = PDPᵀ.
- PVI: escolha a condição inicial que zere uma constante ou dê amplitudes iguais
  (para cair numa elipse/círculo reconhecível).
- TFI: escolha o ponto de modo que ∂F/∂y ≠ 0 seja um número limpo e a derivada
  implícita seja racional simples.
- Pode plantar **uma** constante feia que se cancela (premia o aluno cuidadoso),
  como o √241. Não mais que uma por questão.
- EDO de 2ª ordem: escolha as raízes do polinômio característico primeiro
  (inteiras, negativas, distintas) e a condição inicial para que os coeficientes
  saiam inteiros (na lista real, u = 3e^{−t} − 2e^{−2t}). Escolha também o sinal
  de d/dt F(X(0)) de propósito: se for positivo enquanto F → 0, o item de
  interpretação fica mais rico.
- Sistema afim X' = AX + b: se o enunciado pede b, decida conscientemente. A
  lista real pediu b e ele deu 0 (T sem termos lineares) — vale como pegadinha
  leve, mas uma T com termos lineares dá equilíbrio p = −A⁻¹b num ponto inteiro
  fora da origem e obriga a transladar, o que é mais instrutivo.

## 4. Verificar tudo com sympy

Gabarito errado é o pior defeito possível. `scripts/exemplo_verificacao_prova1.py`
mostra uma verificação completa de uma prova somativa e
`scripts/exemplo_verificacao_atividade_1310.py` a da lista de treino de
13/10/2026 (diagonalização com P⁻¹, regra da cadeia ao longo da trajetória,
limites, unicidade do ponto crítico, d/dt T = ‖∇T‖²). Copie `scripts/verificar_template.py`,
preencha com o modelo de cada questão e rode. Verifique: autovalores/autovetores
(e que A·v = λv; com matriz não simétrica, que P⁻¹AP = D), solução da EDO
substituída de volta, condição inicial, d/dt F(X(t)) pela regra da cadeia
comparada com a derivada direta de F(X(t)), limites t → ∞,
derivadas parciais pelos dois caminhos (o errado do roteiro-armadilha e o certo),
derivada implícita via TFI comparada com a explícita quando existir, valor
crítico, equação cartesiana final. Se algo não fechar limpo, mude os parâmetros
e rode de novo. Releia cada enunciado procurando ambiguidade (sentido positivo,
unidades, qual variável é fixa) e declare a convenção explicitamente.

## 5. Resolução e rubrica

Para cada item, escreva:

- **Resolução esperada**: os passos que o aluno deveria escrever, no tom de um
  monitor (curto, direto, com as contas-chave).
- **Rubrica** com 2 a 4 critérios pontuados que somam o valor do item
  ("monta o polinômio característico — 0,3; autovalores corretos — 0,2;
  autovetores unitários — 0,3"). É como o corretor da Poli dá nota parcial.
- **Erro típico** que o item pega (ex.: "derivou E(x, i) com i fixo, mas a força
  é a derivada com λ fixo — sinal trocado").
- No último item de cada questão, um parágrafo **"Interpretação possível:"**
  ligando o resultado ao sistema.

## 6. Montar o simulado (skill `simulado-de-prova`)

Siga a skill `simulado-de-prova` (que carrega `artifact-design` e publica com a
ferramenta Artifact), com estas adaptações para prova dissertativa. Parta de
`assets/modelo-simulado.html`: ele já tem capa, cronômetro, entrega em dois
cliques, rubrica com autocorreção, respostas finais com tolerância e MathJax
configurado. Troque só o conteúdo das questões, as figuras e o quadro de notas.

- Cabeçalho no estilo da capa real: disciplina, "Prova Integradora", data,
  quadro de notas por questão e as instruções (tom de `references/padrao-provas-reais.md`).
- Uma questão por "folha" (cartão), peso no título, figura SVG inline ao lado
  do enunciado. Notação com **MathJax 3 saída SVG**
  (`https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js`). Não use KaTeX:
  o CSS e as fontes dele vêm de CDN e são bloqueados no artefato, e a matemática
  sai quebrada. Escreva `&amp;` dentro de matrizes e `\lt`/`\gt` no lugar de `<`/`>`.
- A correção fica em blocos `class="corr nomath" hidden`; ao entregar, remova
  `nomath` e chame `MathJax.typesetPromise` só nesses blocos.
- Confira com um script que a soma dos critérios da rubrica de cada item bate
  com o peso do item e que o total dá 10 (no formato lista, 10 por questão;
  mostre os pontos de cada item no enunciado, como a lista real).
- No formato lista não há capa: troque-a por um cabeçalho "Atividade
  Integradora — dd/mm/aaaa" e mantenha cronômetro e entrega.
- Cada item tem um campo de rascunho (textarea) e, quando a resposta final for
  um número ou expressão curta, um campo de resposta final conferido com
  tolerância numérica.
- **Entregar** revela resolução + rubrica de cada item com checkboxes; o aluno
  marca os critérios que cumpriu (autocorreção, como a correção real) e a nota
  soma automaticamente, junto com as respostas finais conferidas.
- Cronômetro com a duração da prova (padrão 4h), Refazer zera tudo.
- Gabarito e rubrica em objetos JS (`RUBRICA`, `RESP`); cheque a sintaxe do
  script com Node antes de publicar.

## 7. Entregar

Em duas ou três frases: o que é a prova e uma linha por questão dizendo o
sistema e o que ela cobra. Não repita o gabarito no chat. Ofereça outra prova
com outros sistemas ou focar nos itens em que o aluno perder ponto.

Se o usuário disser que ficou fora do perfil (difícil, fácil, fora do programa),
aceite, diga em uma frase o que muda e refaça seguindo o nível real.
