"""IA desde cero #10 · Una IA es tan buena como sus datos (sesgo)."""
import numpy as np
from matplotlib.patches import Circle, Ellipse

from base import Reel, ease, ACCENT, C2, C3, MUTED, FG, SERIE_CERO

ROJO, VERDE, NARANJA = "#E63946", "#7BC950", "#FF9F1C"
rng = np.random.default_rng(13)
ROJAS = np.c_[rng.normal(1.6, 0.45, 9), rng.normal(2.4, 0.5, 9)]
NARANJAS = np.c_[rng.normal(4.6, 0.45, 9), rng.normal(5.5, 0.5, 9)]
VERDES = np.c_[rng.normal(8.0, 0.45, 8), rng.normal(2.5, 0.5, 8)]
PRUEBA = np.array([6.2, 3.0])   # la manzana verde que llega

T_REGLA, T_PRUEBA, T_NARANJA, T_ERROR = 4.8, 9.2, 10.6, 11.8
T_VERDES, T_GIRO0, T_GIRO1, T_BIEN = 17.9, 19.4, 20.9, 21.2

ESCENAS = [  # "!" robot · "P:" Paco · "V:" Voltio · resto, narradora
    (0.0, 4.4, "Entrenamos una IA con frutas… pero solo con manzanas ROJAS"),
    (4.4, 8.8, "P:Hombre, lo rojo es manzana. Eso lo sabe todo el mundo"),
    (8.8, 13.0, "!Llega una manzana verde… ¡es una naranja! Segurísimo.", "pulgar"),
    (13.0, 17.6, "No es tonta: nunca había visto una manzana verde"),
    (17.6, 22.6, "V:¡Solución científica: más ejemplos y más variados!"),
    (22.6, 27.2, "Esto es el SESGO: pasa con caras, voces o currículums"),
    (27.2, 31.8, "!¡Sígueme! Con buenos datos, aprendo mejor"),
]
VOZ = {
    "gancho": "¡Confundí una manzana con una naranja!",
    0: "Entrenamos una IA con frutas. Pero solo con manzanas rojas.",
    2: "Llega una manzana verde… ¡Es una naranja! Segurísimo.",
    5: "Esto se llama sesgo. Y pasa con caras, voces, o currículums.",
}
EFECTOS = ([(0.4 + 0.15 * k, "pop") for k in range(0, 18, 3)]
           + [(T_REGLA, "whoosh"), (T_PRUEBA, "pop"), (T_ERROR, "error"),
              (T_VERDES, "pop"), (T_GIRO0, "whoosh"), (T_BIEN, "pop")])
PORTADA = dict(titulo=["Una IA es", "tan buena", "como sus datos"], amarilla=2, t=12.5,
               gesto="piensa")

TEASER = {'t': 12.0, 'texto': 'Confundió una manzana con una naranja', 'pregunta': '◀◀  ¿Cómo pudo pasar?', 'y': 0.6}

reel = Reel(10, "Una IA es tan buena\ncomo sus datos", ESCENAS, 31.8, voz=VOZ,
            efectos=EFECTOS, serie=SERIE_CERO, musica={"bpm": 94}, portada=PORTADA,
            teaser=TEASER, retratos=True)
ax = reel.ax
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.8)
ax.set_aspect("equal")
ax.text(9.8, 7.6, "color: rojo → naranja → verde →", ha="right", va="top", color=MUTED,
        size=11)
ax.text(0.15, 7.6, "↑ tamaño", ha="left", va="top", color=MUTED, size=11)
gx, gy = np.meshgrid(np.linspace(0, 10, 120), np.linspace(0, 7.8, 94))
fondo = ax.imshow(np.zeros((94, 120, 4)), extent=(0, 10, 0, 7.8), origin="lower", zorder=1,
                  interpolation="bilinear")
frontera, = ax.plot([], [], color=ACCENT, lw=4, zorder=3)

artistas = []


def add(a):
    artistas.append(a)
    return a


def limpiar():
    while artistas:
        artistas.pop().remove()


def fruta(p, r, color, manzana=True, alpha=1.0):
    add(ax.add_patch(Circle(p, r, fc=color, ec=FG, lw=1.5, alpha=alpha, zorder=6)))
    if manzana and r > 0.05:
        add(ax.add_patch(Ellipse((p[0] + r * 0.35, p[1] + r * 1.05), r * 0.7, r * 0.35,
                                 angle=25, fc="#2D6A4F", ec="none", alpha=alpha, zorder=7)))


def regla(t):
    """Frontera: primero vertical (solo mira el color), luego horizontal (mira el tamaño)."""
    g = ease((t - T_GIRO0) / (T_GIRO1 - T_GIRO0))
    ang = 90 * (1 - g)                       # 90 = vertical, 0 = horizontal
    centro = np.array([3.1 + 1.9 * g, 4.0])
    d = np.array([np.cos(np.radians(ang)), np.sin(np.radians(ang))])
    n = np.array([-d[1], d[0]])              # normal: apunta hacia las "naranjas"
    if n @ (NARANJAS.mean(0) - centro) < 0:
        n = -n
    return centro, d, n


def draw(t):
    limpiar()
    frontera.set_data([], [])
    fondo.set_data(np.zeros((94, 120, 4)))
    # ------------------------------------------------ datos de entrenamiento
    for k, p in enumerate(ROJAS):
        fruta(p, 0.26 * ease((t - 0.4 - 0.15 * k) / 0.25) + 0.001, ROJO)
    for k, p in enumerate(NARANJAS):
        fruta(p, 0.36 * ease((t - 0.5 - 0.15 * k) / 0.25) + 0.001, NARANJA, manzana=False)
    if t >= T_VERDES:
        for k, p in enumerate(VERDES):
            fruta(p, 0.26 * ease((t - T_VERDES - 0.15 * k) / 0.25) + 0.001, VERDE)

    # ------------------------------------------------ la regla aprendida
    if t >= T_REGLA:
        a = ease((t - T_REGLA) / 0.6)
        c, d, n = regla(t)
        largo = 12 * a
        frontera.set_data([c[0] - d[0] * largo, c[0] + d[0] * largo],
                          [c[1] - d[1] * largo, c[1] + d[1] * largo])
        lado = ((np.c_[gx.ravel(), gy.ravel()] - c) @ n).reshape(gx.shape) > 0
        img = np.zeros(gx.shape + (4,))
        img[lado] = [1.0, 0.62, 0.11, 0.09 * a]
        img[~lado] = [0.9, 0.22, 0.27, 0.09 * a]
        fondo.set_data(img)
        if t < T_GIRO0:
            add(ax.text(1.6, 6.4, "MANZANA", ha="center", size=14, weight="black", color=ROJO,
                        alpha=a, zorder=8))
            add(ax.text(6.4, 6.4, "NARANJA", ha="center", size=14, weight="black",
                        color=NARANJA, alpha=a, zorder=8))
            add(ax.text(3.1, 0.55, "regla: el color", ha="center", size=12, weight="bold",
                        color=ACCENT, alpha=a, zorder=8))
        elif t >= T_GIRO1:
            add(ax.text(5.0, 6.6, "NARANJA", ha="center", size=14, weight="black",
                        color=NARANJA, zorder=8))
            add(ax.text(5.0, 0.55, "MANZANA (roja o verde)", ha="center", size=14,
                        weight="black", color=ROJO, zorder=8))

    # ------------------------------------------------ la manzana verde de prueba
    if t >= T_PRUEBA:
        b = ease((t - T_PRUEBA) / 0.4)
        fruta(PRUEBA, 0.42 * b + 0.001, VERDE)
        if T_NARANJA <= t < T_BIEN:
            add(ax.text(PRUEBA[0], PRUEBA[1] + 0.85, "«¡naranja!»", ha="center", size=16,
                        weight="black", color=NARANJA, zorder=9))
        if T_ERROR <= t < T_VERDES:
            c = ease((t - T_ERROR) / 0.25)
            add(ax.text(PRUEBA[0], PRUEBA[1] - 1.0, "✗ ERROR", ha="center", va="center",
                        size=22 + 8 * (1 - c), weight="black", color=C2, alpha=c, zorder=9))
            if t >= 13.2:
                add(ax.text(PRUEBA[0], PRUEBA[1] - 1.75, "nunca vio una manzana verde",
                            ha="center", va="center", size=12, weight="bold", color=MUTED,
                            alpha=ease((t - 13.2) / 0.4), zorder=9))
        if t >= T_BIEN:
            add(ax.text(PRUEBA[0], PRUEBA[1] - 1.0, "✓ manzana", ha="center", size=18,
                        va="center",
                        weight="black", color=C3, zorder=9))

    if t >= 22.8:
        a = ease((t - 22.8) / 0.4)
        add(ax.text(2.4, 4.3, "SESGO", ha="center", va="center", size=28, weight="black",
                    color=ACCENT, alpha=a, zorder=9,
                    bbox=dict(boxstyle="round,pad=0.25", fc="#0E1117", ec=ACCENT, lw=2,
                              alpha=a)))


if __name__ == "__main__":
    reel.render(draw, "13_sesgo")
