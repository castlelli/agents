"""Molde de verificação de gabarito para provas integradoras.

Copie para o diretório de trabalho, preencha uma função por questão e rode:
    python3 verificar.py
Cada `check` falha alto (AssertionError) se algo não fechar.
Requer: pip install sympy numpy
"""
import sympy as sp


def check(nome, cond):
    ok = bool(sp.simplify(cond)) if not isinstance(cond, bool) else cond
    print(("OK   " if ok else "FALHA") + "  " + nome)
    assert ok, nome


# ---------- Exemplo 1: autovalores / desacoplamento ----------
def questao_autovalores():
    k, M, t = sp.symbols("k M t", positive=True)
    A = sp.Matrix([[3, 1], [1, 3]]) * k / M         # matriz do sistema x'' = -A x
    for lam, mult, vecs in A.eigenvects():
        for v in vecs:
            check(f"A v = {lam} v", sp.simplify(A * v - lam * v) == sp.zeros(2, 1))
    # solução candidata e PVI
    w1, w2 = sp.sqrt(2 * k / M), sp.sqrt(4 * k / M)
    c1, c2 = sp.symbols("c1 c2")
    X = c1 * sp.cos(w1 * t) * sp.Matrix([1, -1]) + c2 * sp.cos(w2 * t) * sp.Matrix([1, 1])
    check("x'' = -A x", sp.simplify(X.diff(t, 2) + A * X) == sp.zeros(2, 1))


# ---------- Exemplo 2: derivada implícita (TFI) ----------
def questao_tfi():
    x, y = sp.symbols("x y")
    F = x**3 + y**3 - 3 * x * y - 1          # curva implícita F = 0
    p = {x: 1, y: 0}                          # ponto (verifique F(p) = 0!)
    check("ponto na curva", F.subs(p) == 0)
    Fy = sp.diff(F, y).subs(p)
    check("TFI aplicável (Fy != 0)", Fy != 0)
    dydx = (-sp.diff(F, x) / sp.diff(F, y)).subs(p)
    print("   y'(x0) =", sp.nsimplify(dydx))


# ---------- Exemplo 3: roteiro-armadilha (qual variável fica fixa) ----------
def questao_variaveis_estado():
    x, lam, i, R = sp.symbols("x lambda i R", positive=True)
    L = R / x
    E_xi = L * i**2 / 2
    i_of = 2 * lam * x / R                    # de lambda*x = R i / 2
    errado = -sp.diff(E_xi, x).subs(i, i_of)  # roteiro do enunciado
    certo = -sp.diff(E_xi.subs(i, i_of), x)   # derivada com lambda fixo
    print("   roteiro:", sp.simplify(errado), "| correto:", sp.simplify(certo))
    check("roteiro dá resposta diferente (armadilha funciona)", sp.simplify(errado - certo) != 0)


if __name__ == "__main__":
    questao_autovalores()
    questao_tfi()
    questao_variaveis_estado()
