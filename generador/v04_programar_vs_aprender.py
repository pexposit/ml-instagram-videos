"""IA desde cero #1 · Programar vs. aprender: la IA saca la regla de los ejemplos."""
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, Ellipse

from base import Reel, ease, ACCENT, C1, C2, C3, MUTED, FG, GRID, BG, SERIE_CERO

ROJO, VERDE, NARANJA = "#E63946", "#7BC950", "#FF9F1C"

# ----------------------------------------------------------------- datos de ejemplo
rng = np.random.default_rng(4)
N = 14
manzanas = np.c_[rng.normal(3.0, 0.7, N), rng.normal(2.3, 0.6, N)]
naranjas = np.c_[rng.normal(6.6, 0.7, N), rng.normal(5.3, 0.6, N)]
X = np.vstack([manzanas, naranjas])
y = np.r_[-np.ones(N), np.ones(N)]           # -1 manzana, +1 naranja
colores = [ROJO if rng.random() < 0.6 else VERDE for _ in range(N)] + [NARANJA] * N
orden_aparicion = rng.permutation(len(X))

# Intentos de frontera: empieza mal y se va corrigiendo a saltos, como hace el algoritmo
# (cada intento = ángulo de la recta y un punto por el que pasa).
INTENTOS = [(15, 5.0, 1.4), (6, 5.0, 2.1), (-10, 4.9, 2.7), (-24, 4.9, 3.2), (-38, 4.8, 3.6),
            (-50, 4.8, 3.8)]


def recta(theta, px, py):
    n = np.array([-np.sin(np.radians(theta)), np.cos(np.radians(theta))])
    return n, -n @ np.array([px, py])


fronteras = [recta(*k) for k in INTENTOS]
NUEVA = np.array([2.0, 4.0])                 # fruta nueva: una manzana

T_APRENDE0, T_APRENDE1 = 11.4, 18.0
T_PASO = (T_APRENDE1 - T_APRENDE0 - 0.6) / (len(fronteras) - 1)

ESCENAS = [
    (0.0, 3.9, "Programar es escribir reglas: «si es roja, es manzana»"),
    (3.9, 7.6, "Pero llega una manzana VERDE… y la regla falla"),
    (7.6, 11.4, "La IA hace otra cosa: aprende de MUCHOS ejemplos"),
    (T_APRENDE0, T_APRENDE1, "Prueba una frontera, mira en qué falla y la corrige"),
    (18.0, 22.2, "!Llega una fruta nueva… y la clasifica ella sola"),
    (22.2, 26.4, "Eso es aprender: sacar la regla a partir de ejemplos"),
    (26.4, 31.0, "!Sigue a @hacerlointeligente para entender la IA desde cero"),
]
VOZ = {
    "gancho": "La inteligencia artificial no se programa. Se enseña.",
    0: "Programar es escribir reglas. Por ejemplo: si es roja, es manzana.",
    1: "Pero llega una manzana verde, y la regla falla.",
    2: "La IA hace otra cosa: aprende de muchos ejemplos.",
    3: "Prueba una frontera, mira en qué se equivoca, y la corrige. Una y otra vez.",
    4: "Llega una fruta nueva, y la clasifica ella sola.",
    5: "Eso es aprender: sacar la regla a partir de ejemplos.",
    6: "Sigue a hacerlo inteligente para entender la IA desde cero.",
}
EFECTOS = ([(0.6, "pop"), (4.4, "pop"), (5.4, "error")]
           + [(7.9 + 0.11 * k, "pop") for k in range(0, len(X), 4)]
           + [(T_APRENDE0 + 0.3 + k * T_PASO, "whoosh") for k in range(len(fronteras) - 1)]
           + [(18.4, "pop"), (19.6, "pop")])

PORTADA = dict(titulo=["La IA no", "se programa.", "Se ENSEÑA."], amarilla=2, t=20.5, gesto="senala")

reel = Reel(1, "La IA no se programa.\nSe ENSEÑA.", ESCENAS, 31.0, voz=VOZ, efectos=EFECTOS,
            serie=SERIE_CERO, musica={"bpm": 98},
            portada=PORTADA)
ax = reel.ax
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.8)
ax.set_aspect("equal")


# ----------------------------------------------------------------- dibujo
def fruta(x, y, r, color, tipo, alpha=1.0):
    arts = [ax.add_patch(Circle((x, y), r, fc=color, ec=FG, lw=2, alpha=alpha, zorder=6))]
    if tipo == "manzana":
        arts.append(ax.add_patch(Ellipse((x + r * 0.35, y + r * 1.05), r * 0.7, r * 0.35,
                                         angle=25, fc="#2D6A4F", ec="none", alpha=alpha, zorder=7)))
        arts.append(ax.plot([x, x + r * 0.05], [y + r * 0.8, y + r * 1.25], color="#6B4226",
                            lw=3, alpha=alpha, zorder=7)[0])
    arts.append(ax.add_patch(Circle((x - r * 0.35, y + r * 0.35), r * 0.22, fc="#FFFFFF",
                                    ec="none", alpha=0.35 * alpha, zorder=7)))
    return arts


artistas = []


def limpiar():
    while artistas:
        artistas.pop().remove()


tarjeta_txt = ax.text(5, 5.2, "", ha="center", va="center", size=17, weight="bold", color=FG,
                      family="DejaVu Sans Mono", zorder=5)
resultado = ax.text(5, 1.0, "", ha="center", va="center", size=19, weight="black", zorder=8)
puntos = ax.scatter(X[:, 0], X[:, 1], s=0, c=colores, edgecolors=FG, linewidths=1.2, zorder=4)
eje_x = ax.text(9.8, 0.15, "tamaño →", ha="right", va="bottom", color=MUTED, size=12, alpha=0)
eje_y = ax.text(0.15, 7.6, "↑ piel rugosa", ha="left", va="top", color=MUTED, size=12, alpha=0)
gx, gy = np.meshgrid(np.linspace(0, 10, 120), np.linspace(0, 7.8, 94))
fondo = ax.imshow(np.zeros((94, 120, 4)), extent=(0, 10, 0, 7.8), origin="lower", zorder=1,
                  interpolation="bilinear")
frontera, = ax.plot([], [], color=ACCENT, lw=4, zorder=3)
leyenda = ax.text(5, 7.55, "", ha="center", va="top", size=13, weight="bold", color=FG, zorder=8)


def linea(wv, bv):
    xs = np.array([0, 10])
    if abs(wv[1]) < 1e-6:
        return [-bv / wv[0]] * 2, [0, 7.8]
    return xs, -(wv[0] * xs + bv) / wv[1]


def pintar_fondo(wv, bv, alpha):
    lado = (np.c_[gx.ravel(), gy.ravel()] @ wv + bv).reshape(gx.shape) > 0
    img = np.zeros(gx.shape + (4,))
    img[lado] = [1.0, 0.62, 0.11, 0.09 * alpha]
    img[~lado] = [0.9, 0.22, 0.27, 0.09 * alpha]
    fondo.set_data(img)


def draw(t):
    limpiar()
    tarjeta_txt.set_text("")
    resultado.set_text("")
    frontera.set_data([], [])
    fondo.set_data(np.zeros((94, 120, 4)))
    leyenda.set_text("")

    if t < 7.6:  # --------------------------------------------- programación clásica
        a = ease(t / 0.5)
        caja = FancyBboxPatch((1.4, 4.1), 7.2, 2.2, boxstyle="round,pad=0,rounding_size=0.3",
                              fc="#161D2A", ec=C1, lw=2.5, alpha=a, zorder=4)
        artistas.append(ax.add_patch(caja))
        tarjeta_txt.set_text("SI la fruta es ROJA\n   → es MANZANA")
        tarjeta_txt.set_alpha(a)
        if t < 3.9:
            b = ease((t - 0.6) / 0.4)
            artistas.extend(fruta(5, 2.2, 0.9 * b + 0.01, ROJO, "manzana"))
            if t > 1.6:
                resultado.set_text("✓ manzana")
                resultado.set_color(C3)
        else:
            b = ease((t - 4.4) / 0.4)
            artistas.extend(fruta(5, 2.2, 0.9 * b + 0.01, VERDE, "manzana"))
            if t > 5.4:
                resultado.set_text("✗ «no es manzana»")
                resultado.set_color(C2)
        puntos.set_sizes(np.zeros(len(X)))
        eje_x.set_alpha(0)
        eje_y.set_alpha(0)
        return

    # ------------------------------------------------------------- aprendizaje
    eje_x.set_alpha(1)
    eje_y.set_alpha(1)
    tamanos = np.zeros(len(X))
    for k, i in enumerate(orden_aparicion):
        tamanos[i] = 190 * ease((t - 7.9 - 0.11 * k) / 0.25)
    puntos.set_sizes(tamanos)
    leyenda.set_text("●  manzanas      ●  naranjas")
    if t < 9.0:
        return

    if t < T_APRENDE0:
        return
    if t < T_APRENDE1:
        tt = t - T_APRENDE0 - 0.3
        k = int(np.clip(tt // T_PASO, 0, len(fronteras) - 2))
        a = ease((tt - k * T_PASO) / (T_PASO * 0.7)) if tt > 0 else 0
        (w0, b0), (w1, b1) = fronteras[k], fronteras[k + 1]
        wv, bv = w0 + (w1 - w0) * a, b0 + (b1 - b0) * a
        # resalta los ejemplos mal clasificados en este momento
        mal = y * (X @ wv + bv) <= 0
        tam = tamanos.copy()
        tam[mal] = 190 + 120 * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * t))
        puntos.set_sizes(tam)
        leyenda.set_text(f"intento {k + 1}   ·   fallos: {int(mal.sum())}")
    else:
        wv, bv = fronteras[-1]
        leyenda.set_text("fallos: 0")
    frontera.set_data(*linea(wv, bv))
    pintar_fondo(wv, bv, 1.0)

    if t >= 18.0:  # ------------------------------------------- fruta nueva
        b = ease((t - 18.4) / 0.4)
        artistas.extend(fruta(*NUEVA, 0.42 * b + 0.01, VERDE, "manzana"))
        if t < 19.6:
            artistas.append(ax.text(NUEVA[0] + 0.7, NUEVA[1] + 0.5, "?", size=26,
                                    weight="black", color=ACCENT, zorder=9))
        else:
            artistas.append(ax.text(NUEVA[0] + 0.6, NUEVA[1], "¡manzana!", size=16, va="center",
                                    weight="black", color=ACCENT, zorder=9))


if __name__ == "__main__":
    reel.render(draw, "04_programar_vs_aprender")
