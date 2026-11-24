# Catálogo de sistemas (gire, combine, invente)

Cada entrada: sistema → objeto matemático → itens possíveis → onde mora o
item-assinatura. Escolha sistemas de áreas diferentes numa mesma prova. Os
sistemas já usados nas provas reais (molas a 45°, eletroímã, esfera na parábola,
estrutura com cabo, flambagem, toboágua) podem inspirar, mas não repita os
mesmos números nem a mesma geometria.

## Álgebra (autovalores) em primeiro plano

1. **Osciladores acoplados** (duas massas e três molas; pêndulos ligados por
   mola; prédio de dois andares em sismo; circuitos LC acoplados).
   Mx'' = −Kx, K simétrica. Itens: autovalores = ω², modos normais, base
   ortonormal, desacoplamento g₁, g₂, PVI que excita um só modo, batimento,
   trajetória no plano (x₁, x₂). Assinatura: "um colega disse que basta resolver
   cada massa separadamente" — só vale se a mola de acoplamento for nula
   (K diagonal).

2. **Tanques/compartimentos em cascata** (mistura de salmoura; farmacocinética
   sangue–tecido; reator químico; resfriamento de dois blocos em contato).
   x' = Ax, autovalores reais negativos. Itens: montar A pelo balanço,
   diagonalizar, solução geral, PVI, lim t→∞, instante em que a concentração do
   2º tanque é máxima (derivada = 0). Assinatura: valor crítico da vazão em que
   A deixa de ser diagonalizável (autovalor duplo).

3. **Tensões/inércia em placa — eixos principais.** Tensor simétrico 2×2
   σ = [[σx, τ], [τ, σy]]. Itens: autovalores = tensões principais, autovetores =
   direções principais, forma quadrática σ(n) = nᵀσn, identificar a cônica
   nᵀσn = 1 (elipse/hipérbole) por rotação de eixos. Cálculo: gradiente da forma
   quadrática é 2σn (ortogonal à cônica), derivada direcional. Assinatura:
   "um colega rotacionou 45° sempre" — só funciona se σx = σy.

4. **Processo iterativo / Markov** (bicicletas entre estações; usuários entre
   servidores; população de Leslie). xₙ₊₁ = Axₙ. Itens: autovalor 1 e estado
   estacionário, Aⁿ via diagonalização, limite n→∞, taxa de convergência pelo
   2º autovalor. Cálculo: versão contínua x' = (A − I)x.

5. **Rotação rígida / mudança de referencial.** Matriz de rotação em ℝ³, eixo
   = autovetor de autovalor 1, ângulo pelo traço. Curvas: trajetória de um ponto
   do corpo, velocidade = ω⃗ ∧ r⃗.

## Ponte: sistema dinâmico + indicador escalar (padrão das listas de treino)

Esqueleto: X' = AX (+ b) resolvido por diagonalização, e uma função escalar
F(x, y) acompanhada ao longo da trajetória. Gera naturalmente ∇F, regra da
cadeia d/dt F(X(t)) = ∇F·X', sinal com interpretação, limite t → ∞, ponto de
equilíbrio. Varie o revestimento:

11. **EDO de 2ª ordem monitorada** (peça com amortecimento, suspensão, circuito
    RLC, sensor de posição). u'' + a u' + b u = 0 → X = (u, u'), matriz
    companheira [[0, 1], [−b, −a]] — **não simétrica**, autovetores não
    ortogonais (treina P⁻¹ em vez de Pᵀ). Escolha a, b com raízes inteiras
    distintas (−1, −2; −1, −3; −2, −3). Indicador: forma quadrática
    (energia x² + y², ou com termo cruzado). Itens: d/dt F em t = 0 (sinal
    pode ser negativo ou positivo — escolha a condição inicial para que o
    sinal ensine algo: "o indicador cresce no início mesmo indo a zero"),
    limites. Assinatura possível: "um colega afirmou que, como F(X(t)) → 0,
    F decresce sempre" — falso se d/dt F(X(0)) > 0; peça contraexemplo.

12. **Fluxo gradiente** (sonda que busca máximo de temperatura/concentração/
    sinal; algoritmo de otimização contínuo; robô que segue luz). X' = ∇T(X)
    (ou −∇ para mínimo). Com T quadrática, A = Hessiana (simétrica → autovalores
    reais, autovetores ortogonais) e b = parte linear de ∇T. Itens: montar A e b,
    diagonalizar, limite = ponto crítico, verificar unicidade (det A ≠ 0),
    d/dt T = ‖∇T‖² ≥ 0 e interpretar. Variante mais rica: T com termos lineares
    → b ≠ 0, equilíbrio p = −A⁻¹b fora da origem; o aluno translada Y = X − p.
    Variante com ponto de sela (autovalores de sinais opostos): a sonda só
    converge se X(0) estiver no autoespaço estável — ótimo item conceitual.

13. **Compartimentos com indicador** (dois tanques e custo/impureza total;
    duas populações e um índice). x' = Ax (+ entrada constante b) e um índice
    linear ou quadrático das concentrações; d/dt do índice e limite.

## Cálculo II em primeiro plano

6. **Variáveis de estado e regra da cadeia** (gás de van der Waals; capacitor
   de placas com distância variável; mola não linear; solenoide). Relação
   F(a, b, c) = 0 entre três grandezas, energia E(·,·). Itens: roteiro-armadilha
   de "quais variáveis ficam fixas", TFI para expressar uma variável pelas
   outras, identidade (∂a/∂b)(∂b/∂c)(∂c/∂a) = −1, função homogênea e Euler.

7. **Placa aquecida** T(x, y) (dissipador de CPU, chapa de solda). Itens:
   domínio e conjunto aberto, continuidade, gradiente = direção de maior
   aumento, derivada direcional, plano tangente/aproximação linear, isoterma
   T = c como curva implícita (TFI: y'(x) no ponto), e — se T for quadrática —
   identificar a isoterma via autovalores da matriz da forma (ponte com Álgebra).

8. **Braço robótico de dois elos** (x, y) = f(θ₁, θ₂). Itens: Jacobiana,
   regra da cadeia para velocidade da garra, singularidade det J = 0
   (configurações esticada/dobrada), TFI para inverter localmente, autovalores
   de JJᵀ = elipse de manipulabilidade.

9. **Partícula/conta em trilho** (curva dada γ(t) ou implícita G(x, y) = 0:
   trilho de montanha-russa, came, pista de teste). Itens: parametrização,
   reta tangente, comprimento de arco, linearização, período de pequenas
   oscilações, ponto onde a TFI falha (tangente vertical).

10. **Equilíbrio com não linearidade** (flambagem, pêndulo com mola, válvula de
    alívio). Equação f(θ) = g(θ) com parâmetro; contagem de soluções; valor
    crítico pela derivada na origem; esboço com interseções e significado físico.
    Versão com Álgebra: linearizar em torno do equilíbrio → matriz 2×2 →
    autovalores decidem estabilidade.

## Como inventar um sistema novo

Bom sistema = alguém da Poli acredita que ele existe + tem uma matriz simétrica
ou diagonalizável natural OU uma relação implícita natural + rende uma pergunta
final com significado (curva conhecida, valor crítico, estabilidade, direção
principal). Se só rende contas, descarte.
