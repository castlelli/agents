# Padrão extraído das provas integradoras reais

Fontes analisadas: "Mecatrônica — Projeto Integrador, Primeira Prova, 22/05/2024"
(4 questões), "P1 Integradora" (3 questões, fotos; Cálculo II + Álgebra II) e
"Atividade Integradora 13/10/2026" (lista de treino para as somativas, 2 questões,
p. 21 da apostila).
Use este arquivo para calibrar formato, tom e nível. Não copie as questões: elas
servem de molde.

## Capa e instruções (tom a reproduzir)

- Identificação: Nome, NUSP, Turma; quadro "Questão | Nota" e Total.
- Instruções numeradas, tom seco e administrativo: celular proibido mesmo
  desligado (e "não custa repetir"); preencher à tinta; duração máxima de 4 horas
  e saída só após 1 hora; "Este caderno consiste de N questões dissertativas, uma
  em cada folha"; tinta azul/preta ou lápis; só vale o que estiver na folha da
  questão (frente e verso, devidamente indicado); "justificando todas as suas
  afirmações"; não destacar folhas. Fecha com "BOA PROVA!".
- Pesos entre 2,0 e 3,0 por questão, total 10.

## Anatomia das questões reais

### Mecatrônica 2024

**Q1 (3,0) Estrutura com cabo.** Duas barras articuladas e um cabo; vistas
isométrica, frontal e lateral; coordenadas dos pontos dadas; F escolhida com
módulo √241 para casar com |AC| = √241 (constante plantada).
Itens: projeção de F nas direções das barras → momento em relação a um polo →
forças nas barras no equilíbrio (sistema linear) → "um colega sugeriu projetar F
nas direções das barras e do cabo… em que caso particular funciona?" (resposta:
direções mutuamente ortogonais).

**Q2 (2,0) Cinemática por integração.** v(t) = 2 − cos 2t após t = 0; a(t),
x(t) com condição dada num instante não nulo (3π/4), deslocamento no intervalo.
Questão "de respiro", rotineira.

**Q3 (3,0) Flambagem com mola de torção.** Equação de equilíbrio PL sen θ = kθ.
Itens: justificar que a equação é necessária → esboçar f e g num quadro dado e
contar interseções, com significado físico → justificar analiticamente e desenhar
cada configuração → mostrar que existe P_c (aqui P_c = k/L, pela derivada na
origem) com uma solução abaixo e várias acima, das quais só três fazem sentido
físico.

**Q4 (2,0) Toboágua helicoidal.** Conservação de energia para a velocidade no
solo; depois R(t) dado ("é possível mostrar que…"), instante em que toca o solo e
vetor velocidade nesse instante.

### P1 Integradora (Cálculo II + Álgebra II) — o modelo mais próximo do pedido

**Q1 Eletroímã e variáveis de estado.** Abre definindo variáveis de estado via
PV = nRT. Dá λx = Ri/2, E = ½Li², L(x) = R/x e F = −∂E/∂x (x, λ).
Itens: (a) roteiro-armadilha — derive E(x, i) em x, substitua i(λ, x), multiplique
por −1; "é a força em função de x e λ? Justifique" (não: a derivada parcial foi
feita com i fixo, não λ fixo); (b) obtenha a fórmula correta em (x, λ); (c) obtenha
F em (x, i). Tópico: derivadas parciais, regra da cadeia, mudança de variáveis.

**Q2 Quatro molas e uma massa.** Sistema de EDOs de 2ª ordem dado em forma
matricial, matriz depende de θ; fixa θ = π/4.
Itens: (a) matriz explícita, diagonalizável, autovalores e base de autovetores
unitários (em função de k e M); (b) escrever (x, y) = g₁v₁ + g₂v₂, substituir e
obter EDOs para g₁, g₂; (c) solução geral de cada uma e do sistema; (d) k = M,
PVI com posição (−1, 0) e velocidade (0, 1); (e) equação cartesiana da trajetória
e identificar a curva (elipse).

**Q3 Esfera na parábola.** γ(t) = (t/L, (t/L)²)L; forças peso e normal.
Itens: (a) com s(t) = ∫‖γ'‖ dt, desprezando termos quadráticos ("isto chama-se
linearizar o problema", com nota de rodapé), mostrar d²s/dt² ≈ d²x/dt²;
(b) segunda lei de Newton → equação do movimento; (c) período de pequenas
oscilações, com dica de condição inicial.

### Atividade Integradora 13/10/2026 — lista de treino para as somativas

Formato diferente da P1: **sem capa, sem figura, 2 questões numa página**, cabeçalho
"Atividade Integradora dd/mm/aaaa". Contexto de engenharia em **duas frases**
("um sistema mecânico é monitorado por sensores…", "uma sonda móvel procura o
ponto de temperatura máxima numa placa"), "em unidades normalizadas", e depois é
Matemática pura. Na Q2 cada item tem **rótulo e pontuação**: "(a) Modelagem
(2 pontos)", "(b) Resolução do sistema (4 pontos)", "(c) Identificação do ponto
crítico (3 pontos)", "(d) Interpretação do movimento (1 ponto)" — 10 por questão.

O que une as duas questões é um esqueleto só: **sistema linear X' = AX (+ b)
resolvido por diagonalização + uma função escalar avaliada ao longo da
trajetória**. A ponte entre as disciplinas é a regra da cadeia
d/dt F(X(t)) = ∇F(X(t)) · X'(t).

**Q1 Peça monitorada por sensores.** u'' + 3u' + 2u = 0, u(0) = 1, u'(0) = 1;
X = (u, u'); indicador F(x, y) = x² + y² − xy.
Itens: (a) ∇F e ∇F(X(0)) → (b) reescrever como X' = AX (matriz companheira
[[0, 1], [−2, −3]], **não simétrica**) e X(0) → (c) autovalores −1, −2,
autovetores (1, −1), (1, −2), diagonalização e u(t) = 3e^{−t} − 2e^{−2t} →
(d) X'(0) = (1, −5) e d/dt F(X(t))|₀ = −4; "interprete o sinal" (indicador
decrescendo naquele instante) → (e) lim X(t) e lim F(X(t)) (ambos 0); "interprete"
(sistema volta ao equilíbrio, indicador some).

**Q2 Sonda que sobe o gradiente.** T(x, y) = 100 − x² + xy − y²; a sonda obedece
X' = ∇T(X) (fluxo gradiente), X(0) = (1, 0).
Itens: (a) Modelagem: T_x, T_y, escrever X' = AX + b, achar A, b, X(0) (aqui
A é a Hessiana [[−2, 1], [1, −2]] e **b = 0**, porque T não tem termos lineares;
o enunciado pede b mesmo assim) → (b) autovalores −1, −3, autovetores ortogonais
(1, 1), (1, −1), x(t) e y(t) explícitos → (c) p = lim (x, y) = (0, 0); "verifique
que p é o único ponto crítico de T" (∇T = 0, sem classificar pela Hessiana) e
T(p) = 100 → (d) regra da cadeia: d/dt T = T_x x' + T_y y' = ‖∇T‖² ≥ 0; explicar
que a temperatura medida nunca diminui.

Leituras de nível: contas de 2×2 com autovalores inteiros negativos, condições
iniciais que dão coeficientes inteiros ou ½. O esforço está em **montar o
sistema** e **interpretar**, não em álgebra pesada. Cada questão caberia em
~40–50 min.

## Regularidades

1. Um sistema por questão; integração dentro da questão.
2. Física entra como modelo dado; a nota está na Matemática.
3. Itens vão do procedimento ao conceito; o último pede interpretação,
   identificação ou validade.
4. Números escolhidos para fechar limpo (θ = π/4, k = M, √241).
5. O enunciado guia passo a passo quando o caminho não é óbvio ("realize as
   seguintes operações", "escreva … = g₁v₁ + g₂v₂", "se for útil, use…").
6. Pedidos de justificativa são frequentes ("justifique", "mostre que").
7. Notação: vetores com seta, (F⃗, C) para força aplicada em C, base
   {i⃗, j⃗, k⃗}, γ: ℝ → ℝ², ∂E/∂x (x, λ) indicando as variáveis da função.
8. Uma questão por prova pode ser mais leve (cinemática por integração) para
   equilibrar 4h.
9. Quase todo item final pede **"Interprete…"** em termos do sistema: sinal de
   uma derivada, limite quando t → ∞, desigualdade. A interpretação é cobrada
   como item com pontos, não como enfeite.
10. Nas listas de treino a física quase some: o contexto só dá nome às variáveis.
    Isso é deliberado — elas treinam o esqueleto matemático que a somativa
    reveste com um modelo físico mais rico.
