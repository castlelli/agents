---
name: mock-exam
description: "Cria um simulado interativo (artefato) a partir de uma prova de exemplo de qualquer matéria, com mesmo formato, cronômetro e correção comentada. Use quando pedirem simulado, prova treino, testinho ou mock exam."
---

# Simulado de prova a partir de uma prova de exemplo

O objetivo é entregar uma página que a pessoa usa como se fosse a prova de verdade: mesmo formato, mesmo nível, mesmo tempo. Ao entregar, ela recebe a nota e uma correção que ensina. O valor está em **imitar a prova real com fidelidade**. Um simulado mais difícil ou mais "criativo" que a prova real atrapalha o estudo, porque treina a pessoa para outra prova.

## 1. Ler a prova de exemplo (e o material de apoio)

Antes de escrever qualquer questão, extraia da prova de exemplo:

- **Formato:** quantas questões, peso de cada uma, duração, instruções do cabeçalho (copie o tom delas), tipo de resposta (alternativa única, "marque todas e somente todas", V/F, numérica, dissertativa curta).
- **Regra de pontuação:** "para pontuar você deve marcar exatamente o que se pede" significa tudo ou nada por questão. Respeite isso na correção.
- **Linguagem visual:** a prova tem figuras (circuitos, gráficos, estruturas, código, tabelas)? Os simulados devem ter figuras do mesmo tipo, desenhadas no mesmo estilo.
- **O que cada questão realmente cobra:** o mecanismo central (por exemplo, "ler o que chega em cada entrada e aplicar a fórmula"), e não só o tema.
- **Nível:** quantos passos de raciocínio cada questão exige e quantas "pegadinhas" ela tem. Normalmente é no máximo uma armadilha por questão, e ela vem do conteúdo, não de enunciado confuso.

Se houver lista, apostila ou PDF do conteúdo, leia também. As questões devem ficar dentro do que foi dado, usar a mesma notação (barra para complemento, nomes de sinais, convenções de bits etc.) e, quando fizer sentido, reaproveitar trechos do material (como um código Verilog ou uma figura da apostila).

Se houver memória ou contexto sobre a pessoa e a disciplina (provas anteriores, tópicos fracos), use para escolher a ênfase, sem sair do perfil da prova.

## 2. Planejar as questões

- Mantenha a **mesma quantidade de questões** e a mesma distribuição de tipos da prova de exemplo, com ajustes pequenos só se a pessoa pedir.
- Cada questão deve ser **análoga** a uma da prova ou do material, com números e situações novas. Não copie a questão original com outro valor; mude o caso para que o raciocínio tenha que ser refeito.
- **Calibre a dificuldade pela prova real.** Não empilhe duas armadilhas na mesma questão (por exemplo, ordem de bits cruzada **e** complemento escondido). Se uma convenção importa (qual variável é o bit mais significativo, unidade, sentido positivo), declare-a no enunciado ou na figura de forma explícita, como a prova faria.
- **Distratores com propósito:** cada alternativa errada corresponde a um erro plausível e específico (trocar XOR por XNOR, ler o bit pela esquerda, esquecer o enable, esquecer o sinal). Anote qual erro gera cada distrator, pois isso vai para a correção.
- Ao fazer um **segundo simulado**, varie os casos em relação ao primeiro (outras portas, outras funções, outro valor de entrada), mantendo o nível.

## 3. Verificar o gabarito com cálculo, não de cabeça

Gabarito errado é o pior defeito possível de um simulado. Para tudo que for calculável, verifique com um script (Python ou Node) antes de publicar:

- tabelas verdade, mintermos, saídas de circuitos e códigos (enumere todas as entradas);
- contas numéricas, derivadas e integrais (avalie numericamente ou com sympy);
- saída de trechos de código (execute).

Confira também que **nenhum distrator é acidentalmente correto** e que, nas questões de múltipla marcação, o conjunto correto é exatamente o esperado. Releia cada enunciado procurando ambiguidade: se duas leituras razoáveis levam a respostas diferentes, reescreva.

## 4. Escrever a correção comentada

Para cada questão, a explicação mostra a resposta com o raciocínio curto que leva a ela (os passos que a pessoa deveria escrever na prova), e diz de onde vêm as alternativas erradas principais ("Σm(1,4,5,6) é quem leu A como mais significativo"). Escreva como um monitor explicaria: frases diretas, sem enrolação.

## 5. Montar o artefato

Carregue a skill `artifact-design` antes de escrever o HTML e publique com a ferramenta Artifact. A página deve conter:

- **Folha de prova:** cabeçalho com disciplina e tema, instruções no tom da prova original, questões numeradas com o peso entre colchetes, figura ao lado do enunciado no desktop e acima dele no celular.
- **Figuras em SVG inline**, desenhadas com as cores do tema (claro e escuro), no estilo da prova (portas lógicas, eixos de gráfico, diagramas). Cada SVG recebe `role="img"` e um `aria-label` que descreve as ligações. Para notação matemática pesada, use KaTeX via cdnjs; para notação leve, HTML com Unicode e `text-decoration: overline` para barras.
- **Controles:** radio para alternativa única, checkbox para múltipla marcação, cada um com `id` estável.
- **Barra fixa no topo** com cronômetro da duração real da prova (botão para iniciar, aviso visual nos últimos 2 minutos, entrega automática ao zerar), botão Entregar e botão Refazer.
- **Correção ao entregar:** desabilita os controles, marca a alternativa correta e as marcações erradas, mostra a nota por questão e a nota total, e exibe a explicação de cada questão com o visual de "caneta vermelha". O Refazer limpa tudo e zera o cronômetro.
- O gabarito fica num objeto JS (`KEY = {q1:['c'], q2:['1','3']}`) e as explicações num objeto `WHY`. A pontuação compara conjuntos: só pontua se o marcado for exatamente igual ao gabarito, quando a prova for tudo ou nada.

Antes de publicar, faça uma checagem de sintaxe do script (por exemplo, `new Function(js)` no Node). Título da página: curto e específico, como "Testinho PCS3115 — Mux". Para um segundo simulado, use outro arquivo e um título com "II".

## 6. Entregar

Na resposta, diga em uma ou duas frases o que é o simulado e liste em uma linha o que cada questão cobre. Não repita o gabarito no chat. Ofereça montar outro simulado ou focar nos tipos de questão em que a pessoa errar.

Se a pessoa disser que o simulado ficou fora do perfil (difícil demais, pegadinha demais, conteúdo fora do programa), aceite o ajuste, explique em uma frase o que vai mudar e refaça seguindo o nível da prova real.