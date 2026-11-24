"""Verificação da Atividade Integradora de 13/10/2026 (lista de treino para a somativa).

Modelo do padrão "sistema dinâmico + indicador escalar ao longo da trajetória":
EDO linear resolvida por diagonalização (Álgebra) + gradiente, regra da cadeia
d/dt F(X(t)) e limite t→∞ (Cálculo). Use como molde para questões desse tipo.
Requer: pip install sympy
"""
import sympy as sp


def check(nome, cond):
    ok = bool(cond)
    print(("OK   " if ok else "FALHA") + "  " + nome)
    assert ok, nome


t = sp.symbols("t", real=True)
x, y = sp.symbols("x y", real=True)

# ===== Q1: EDO de 2ª ordem -> sistema de 1ª ordem (matriz companheira, NÃO simétrica) =====
A = sp.Matrix([[0, 1], [-2, -3]])            # u'' + 3u' + 2u = 0
X0 = sp.Matrix([1, 1])
check("autovalores -1, -2", set(A.eigenvals()) == {-1, -2})
v1, v2 = sp.Matrix([1, -1]), sp.Matrix([1, -2])
check("A v1 = -v1", A * v1 == -v1)
check("A v2 = -2 v2", A * v2 == -2 * v2)
P = sp.Matrix.hstack(v1, v2)
check("P^-1 A P = diag(-1,-2)", P.inv() * A * P == sp.diag(-1, -2))
c = P.inv() * X0                               # coordenadas de X(0) na base de autovetores
X = c[0] * sp.exp(-t) * v1 + c[1] * sp.exp(-2 * t) * v2
check("X' = A X", sp.simplify(X.diff(t) - A * X) == sp.zeros(2, 1))
check("X(0) = (1,1)", X.subs(t, 0) == X0)
check("u(t) = 3e^-t - 2e^-2t", sp.simplify(X[0] - (3 * sp.exp(-t) - 2 * sp.exp(-2 * t))) == 0)

F = x**2 + y**2 - x * y
gF = sp.Matrix([F.diff(x), F.diff(y)])
check("grad F(X(0)) = (1,1)", gF.subs({x: 1, y: 1}) == sp.Matrix([1, 1]))
Xp0 = A * X0
check("X'(0) = (1,-5)", Xp0 == sp.Matrix([1, -5]))
dF0 = (gF.subs({x: 1, y: 1}).T * Xp0)[0]
check("d/dt F(X(t)) em t=0 = -4 (regra da cadeia)", dF0 == -4)
FX = F.subs({x: X[0], y: X[1]})
check("confere derivando F(X(t)) direto", sp.simplify(FX.diff(t).subs(t, 0)) == -4)
check("lim X = 0", sp.limit(X[0], t, sp.oo) == 0 and sp.limit(X[1], t, sp.oo) == 0)
check("lim F(X) = 0", sp.limit(FX, t, sp.oo) == 0)

# ===== Q2: fluxo gradiente X' = grad T (A = Hessiana, simétrica) =====
T = 100 - x**2 + x * y - y**2
gT = sp.Matrix([T.diff(x), T.diff(y)])
A2 = gT.jacobian([x, y])
b = gT.subs({x: 0, y: 0})
check("A = [[-2,1],[1,-2]] (Hessiana de T)", A2 == sp.Matrix([[-2, 1], [1, -2]]))
check("b = 0 (T sem termos lineares)", b == sp.zeros(2, 1))
check("autovalores -1, -3", set(A2.eigenvals()) == {-1, -3})
w1, w2 = sp.Matrix([1, 1]), sp.Matrix([1, -1])
check("autovetores ortogonais (A simétrica)", (w1.T * w2)[0] == 0)
Y0 = sp.Matrix([1, 0])
Y = sp.Rational(1, 2) * sp.exp(-t) * w1 + sp.Rational(1, 2) * sp.exp(-3 * t) * w2
check("Y' = A Y + b", sp.simplify(Y.diff(t) - (A2 * Y + b)) == sp.zeros(2, 1))
check("Y(0) = (1,0)", Y.subs(t, 0) == Y0)
p = sp.Matrix([sp.limit(Y[0], t, sp.oo), sp.limit(Y[1], t, sp.oo)])
check("p = (0,0)", p == sp.zeros(2, 1))
crit = sp.solve(list(gT), [x, y], dict=True)
check("p é o único ponto crítico", crit == [{x: 0, y: 0}])
check("T(p) = 100", T.subs({x: 0, y: 0}) == 100)
TY = T.subs({x: Y[0], y: Y[1]})
dT = sp.simplify(TY.diff(t))
normgrad2 = sp.simplify((gT.T * gT)[0].subs({x: Y[0], y: Y[1]}))
check("d/dt T(X(t)) = |grad T|^2 >= 0", sp.simplify(dT - normgrad2) == 0)
