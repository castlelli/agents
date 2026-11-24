import sympy as sp

def check(nome, cond):
    ok = bool(cond)
    print(("OK   " if ok else "FALHA") + "  " + nome)
    assert ok, nome

# ===== Q1 Placa / chip =====
x, y = sp.symbols("x y", real=True)
Q = 5*x**2 - 4*x*y + 8*y**2
T = 80 - Q/4
P = {x: 2, y: 2}
check("T(P)=71", T.subs(P) == 71)
gT = sp.Matrix([T.diff(x), T.diff(y)]).subs(P)
check("grad T(P) = (-3,-6)", gT == sp.Matrix([-3, -6]))
u = -sp.Matrix([1, 1])/sp.sqrt(2)
DuT = sp.simplify((gT.T*u)[0])
check("D_u T = 9/sqrt2", sp.simplify(DuT - 9/sp.sqrt(2)) == 0)
G = Q - 36
phi_p = (-G.diff(x)/G.diff(y)).subs(P)
check("phi'(2) = -1/2", phi_p == sp.Rational(-1, 2))
sol = sp.solve([G, G.diff(y)], [x, y], dict=True)
print("   pontos com G_y=0:", sol)
check("pontos verticais", {(s[x], s[y]) for s in sol} == {(2*sp.sqrt(2), sp.sqrt(2)/2), (-2*sp.sqrt(2), -sp.sqrt(2)/2)})
A = sp.Matrix([[5, -2], [-2, 8]])
check("Q = p^T A p", sp.expand((sp.Matrix([x, y]).T*A*sp.Matrix([x, y]))[0] - Q) == 0)
check("autovalores 4, 9", set(A.eigenvals()) == {4, 9})
v1 = sp.Matrix([2, 1])/sp.sqrt(5); v2 = sp.Matrix([1, -2])/sp.sqrt(5)
check("A v1 = 4 v1", A*v1 == 4*v1); check("A v2 = 9 v2", A*v2 == 9*v2)
uu, vv = sp.symbols("u v")
Qr = sp.expand(Q.subs({x: (2*uu + vv)/sp.sqrt(5), y: (uu - 2*vv)/sp.sqrt(5)}))
check("Q = 4u^2+9v^2", sp.simplify(Qr - (4*uu**2 + 9*vv**2)) == 0)
# gradiente paralelo a p só nos eixos principais
gp = A*sp.Matrix([2, 2]); check("A P x P != 0", gp[0]*2 - gp[1]*2 != 0)
# ponto da isoterma no eixo maior: u=3, v=0
pmaj = 3*v1; check("ponto (6/sqrt5,3/sqrt5) na isoterma", sp.simplify(Q.subs({x: pmaj[0], y: pmaj[1]}) - 36) == 0)
# direção de maior queda
check("-grad T ∝ (1,2)", (-gT)[1] == 2*(-gT)[0])

# ===== Q2 MEMS =====
xg, q, V, eps, Ar, k, x0 = sp.symbols("x q V epsilon A k x0", positive=True)
C = eps*Ar/xg
E_xV = C*V**2/2
E_xq = q**2/(2*C)
V_of = q*xg/(eps*Ar)
roteiro = -(E_xV.diff(xg)).subs(V, V_of)
certo = -E_xq.diff(xg)
print("   roteiro:", sp.simplify(roteiro), " certo:", sp.simplify(certo))
check("roteiro = +q^2/(2eA)", sp.simplify(roteiro - q**2/(2*eps*Ar)) == 0)
check("certo = -q^2/(2eA)", sp.simplify(certo + q**2/(2*eps*Ar)) == 0)
check("energia igual nas duas formas", sp.simplify(E_xV.subs(V, V_of) - E_xq) == 0)
F_xV = sp.simplify(certo.subs(q, C*V))
check("F(x,V) = -eA V^2/(2x^2)", sp.simplify(F_xV + eps*Ar*V**2/(2*xg**2)) == 0)
Gm = 2*k*xg**2*(x0 - xg) - eps*Ar*V**2
eq = k*(x0 - xg) + F_xV
check("G = 2x^2 * (equilibrio)", sp.simplify(Gm - 2*xg**2*eq) == 0)
dxdV = sp.simplify(-Gm.diff(V)/Gm.diff(xg))
print("   dx/dV =", dxdV)
check("dx/dV = eA V /(k x (2x0-3x))", sp.simplify(dxdV - eps*Ar*V/(k*xg*(2*x0 - 3*xg))) == 0)
check("G_x = 0 em x=2x0/3", sp.simplify(Gm.diff(xg).subs(xg, 2*x0/3)) == 0)
Vpi = sp.solve(Gm.subs(xg, 2*x0/3), V)[0]
check("V_pi^2 = 8 k x0^3/(27 eA)", sp.simplify(Vpi**2 - 8*k*x0**3/(27*eps*Ar)) == 0)
h = xg**2*(x0 - xg)
check("max h = 4x0^3/27", sp.simplify(h.subs(xg, 2*x0/3) - 4*x0**3/27) == 0)

# ===== Q3 Baterias =====
t = sp.symbols("t", nonnegative=True)
M = sp.Matrix([[-2, 1], [1, -2]])
check("autovalores -1,-3", set(M.eigenvals()) == {-1, -3})
th = sp.Matrix([20*sp.exp(-t) + 20*sp.exp(-3*t), 20*sp.exp(-t) - 20*sp.exp(-3*t)])
check("theta' = M theta", sp.simplify(th.diff(t) - M*th) == sp.zeros(2, 1))
check("theta(0) = (40,0)", th.subs(t, 0) == sp.Matrix([40, 0]))
tm = sp.solve(th[1].diff(t), t)
print("   t_max:", tm)
check("t* = ln3/2", sp.simplify(tm[0] - sp.log(3)/2) == 0)
th2max = sp.simplify(th[1].subs(t, sp.log(3)/2))
check("theta2 max = 40 sqrt3/9", sp.simplify(th2max - 40*sp.sqrt(3)/9) == 0)
print("   theta2 max ≈", sp.N(th2max), "  t* (x10 min) ≈", sp.N(sp.log(3)/2))
check("segunda derivada < 0 em t*", sp.N(th[1].diff(t, 2).subs(t, sp.log(3)/2)) < 0)
# coordenadas na base de autovetores (nao normalizada): s = th1+th2, d = th1-th2
s = sp.simplify(th[0] + th[1]); d = sp.simplify(th[0] - th[1])
check("d = s^3/1600", sp.simplify(d - s**3/1600) == 0)
gp = th.diff(t)
lim_dir = sp.limit(gp[1]/gp[0], t, sp.oo)
check("tangente limite com inclinação 1 (reta th1=th2)", lim_dir == 1)
# coordenadas ortonormais: g1 = (th1+th2)/sqrt2, g2 = (th1-th2)/sqrt2
g1 = s/sp.sqrt(2); g2 = d/sp.sqrt(2)
check("g2 = g1^3/800", sp.simplify(g2 - g1**3/800) == 0)
print("tudo OK")
