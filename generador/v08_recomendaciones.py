"""IA desde cero #5 · Así decide Instagram qué vídeo ves después (sistemas de recomendación)."""
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch

from base import Reel, ease, ACCENT, C1, C2, C3, MUTED, FG, SERIE_CERO

NARANJA = "#FF9F1C"
TEMAS = {  # nombre: (centro, color)
    "gatos": ((2.3, 5.7), NARANJA),
    "fútbol": ((7.7, 5.8), C3),
    "cocina": ((2.5, 1.9), C2),
    "ciencia": ((7.5, 1.9), C1),
}
rng = np.random.default_rng(8)
VIDEOS = []  # (x, y, tema)
for tema, ((cx, cy), _c) in TEMAS.items():
    for _ in range(8):
        VIDEOS.append((cx + rng.normal(0, 0.6), cy + rng.normal(0, 0.45), tema))
VIDEOS.append((3.4, 3.4, "cocina"))  # el vídeo de "cocina para gatos" que te descubren otros
DESCUBRE = len(VIDEOS) - 1
VIDEOS = np.array([(x, y) for x, y, _ in VIDEOS]), [t for *_r, t in VIDEOS]

TU_RUTA = [(5.0, 3.9), (4.3, 4.4), (3.7, 4.8), (3.2, 5.0)]   # te acercas a los gatos
T_LIKES = [9.2, 10.6, 12.0]
OTROS = [(2.8, 4.1), (3.9, 5.6), (2.6, 5.2)]                   # gente parecida a ti

ESCENAS = [  # "!" = habla el robot (subtítulo amarillo); el resto, la narradora
    (0.0, 4.4, "Instagram coloca cada vídeo en un mapa: los parecidos, juntos"),
    (4.4, 8.8, "Y a ti también te coloca, según lo que ves y lo que te gusta"),
    (8.8, 13.6, "Cada «me gusta» te acerca a ese tipo de vídeos"),
    (13.6, 18.2, "Te enseña lo que está cerca… y lo que vieron otros como tú"),
    (18.2, 22.4, "!¡Por eso no paras de ver vídeos de gatos!", "pulgar"),
    (22.4, 27.0, "Es un SISTEMA DE RECOMENDACIÓN: cuanto más miras, mejor te conoce"),
    (27.0, 31.5, "!¡Dale a «me gusta» y verás más vídeos como este!"),
]
VOZ = {
    "gancho": "¿Te has preguntado por qué ves lo que ves?",
    0: "Instagram coloca cada vídeo en un mapa. Los parecidos, juntos.",
    3: "Te enseña lo que está cerca de ti… y lo que vieron otros como tú.",
    5: "Es un sistema de recomendación: cuanto más miras, mejor te conoce.",
}
EFECTOS = ([(0.4, "whoosh"), (4.8, "pop")] + [(tl, "pop") for tl in T_LIKES]
           + [(13.9, "whoosh"), (15.2, "pop"), (16.4, "pop"), (18.4, "pop")])
PORTADA = dict(titulo=["Así decide", "Instagram", "qué ves después"], amarilla=1, t=17.0,
               gesto="senala")

reel = Reel(5, "Así decide Instagram\nqué ves después", ESCENAS, 31.5, voz=VOZ,
            efectos=EFECTOS, serie=SERIE_CERO, musica={"bpm": 100}, portada=PORTADA)
ax = reel.ax
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.8)
ax.set_aspect("equal")

artistas = []


def add(a):
    artistas.append(a)
    return a


def limpiar():
    while artistas:
        artistas.pop().remove()


def posicion_tu(t):
    if t < 8.8:
        return np.array(TU_RUTA[0])
    k = sum(t >= tl for tl in T_LIKES)
    if k == 0:
        return np.array(TU_RUTA[0])
    a = ease((t - T_LIKES[k - 1]) / 0.6)
    p0, p1 = np.array(TU_RUTA[k - 1]), np.array(TU_RUTA[k])
    return p0 + (p1 - p0) * a


def persona(p, color, r, texto=None, alpha=1.0):
    add(ax.add_patch(Circle(p, r, fc=color, ec=FG, lw=2, alpha=alpha, zorder=7)))
    if texto:
        add(ax.text(*p, texto, ha="center", va="center", size=12, weight="black",
                    color="#0E1117", zorder=8, alpha=alpha))


def draw(t):
    limpiar()
    pos, temas = VIDEOS
    tu = posicion_tu(t)
    radio = 1.7

    # -------------------------------------------- vídeos (miniaturas de colores)
    for i, ((x, y), tema) in enumerate(zip(pos, temas)):
        a = ease((t - 0.3 - 0.03 * i) / 0.3)
        if i == DESCUBRE:
            a = ease((t - 16.4) / 0.3)
        if a <= 0:
            continue
        color = TEMAS[tema][1]
        cerca = t >= 13.9 and np.hypot(x - tu[0], y - tu[1]) < radio
        lado = 0.5 * a * (1.25 if cerca else 1.0)
        if tema == "gatos" and 18.2 <= t < 22.4:
            lado *= 1 + 0.12 * np.sin(2 * np.pi * 2 * t)
        add(ax.add_patch(FancyBboxPatch((x - lado / 2, y - lado / 2), lado, lado,
                                        boxstyle="round,pad=0,rounding_size=0.07",
                                        fc=color, ec=ACCENT if cerca else "#0E1117",
                                        lw=2.5 if cerca else 1, zorder=4)))
        add(ax.text(x, y, "▶", ha="center", va="center", size=8 * a, color="#0E1117",
                    zorder=5))
    for tema, ((cx, cy), color) in TEMAS.items():
        a = ease((t - 1.6) / 0.4)
        dy = 1.25 if cy > 4 else -1.25
        add(ax.text(cx, cy + dy, tema, ha="center", va="center", size=15, weight="black",
                    color=color, alpha=a, zorder=6))

    if t < 4.8:
        return

    # -------------------------------------------- "me gusta"
    for k, tl in enumerate(T_LIKES):
        f = (t - tl) / 1.0
        if 0 <= f < 1:
            obj = pos[[i for i, tm in enumerate(temas) if tm == "gatos"][k * 2]]
            add(ax.text(obj[0], obj[1] + 0.3 + 0.6 * f, "♥", ha="center", va="center",
                        size=26 + 10 * np.sin(np.pi * f), color=C2, alpha=1 - f ** 2,
                        zorder=9))

    # -------------------------------------------- tu radio de recomendaciones
    if t >= 13.9:
        a = ease((t - 13.9) / 0.5)
        add(ax.add_patch(Circle(tu, radio * a, fc=ACCENT, ec=ACCENT, lw=2, ls="--",
                                alpha=0.10, zorder=2)))
        add(ax.add_patch(Circle(tu, radio * a, fc="none", ec=ACCENT, lw=2, ls="--",
                                zorder=3)))

    # -------------------------------------------- otros como tú
    if t >= 15.2:
        for k, p in enumerate(OTROS):
            a = ease((t - 15.2 - 0.2 * k) / 0.3)
            persona(p, MUTED, 0.27 * a + 0.01, alpha=a)
        if t >= 16.4:
            d = pos[DESCUBRE]
            add(ax.plot([OTROS[0][0], d[0]], [OTROS[0][1], d[1]], color=MUTED, lw=2, ls=":",
                        zorder=3)[0])
            add(ax.text(d[0] + 0.35, d[1] - 0.05, "¡nuevo para ti!", ha="left", va="center",
                        size=12, weight="black", color=ACCENT, zorder=9,
                        alpha=ease((t - 16.6) / 0.3)))

    # -------------------------------------------- tú
    a = ease((t - 4.8) / 0.4)
    persona(tu, ACCENT, 0.42 * a + 0.01, "TÚ")


if __name__ == "__main__":
    reel.render(draw, "08_recomendaciones")
