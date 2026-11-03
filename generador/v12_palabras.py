"""IA desde cero #9 · Para una IA, las palabras son coordenadas (embeddings)."""
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch

from base import Reel, ease, ACCENT, C1, C2, C3, MUTED, FG, SERIE_CERO

NARANJA = "#FF9F1C"
PALABRAS = {  # palabra: (x, y, grupo)
    "perro": (1.6, 5.6, "animal"), "gato": (2.5, 6.1, "animal"), "lobo": (1.0, 4.8, "animal"),
    "can": (2.1, 5.1, "animal"),
    "manzana": (7.6, 6.0, "fruta"), "pera": (8.6, 5.4, "fruta"), "plátano": (7.9, 4.8, "fruta"),
    "hombre": (2.0, 1.4, "persona"), "mujer": (4.6, 1.6, "persona"),
    "rey": (3.0, 3.8, "persona"), "reina": (5.6, 4.0, "persona"),
    "coche": (8.3, 1.8, "vehículo"), "moto": (8.9, 2.7, "vehículo"),
}
COLOR = {"animal": NARANJA, "fruta": C3, "persona": C1, "vehículo": C2}
P = {k: np.array(v[:2]) for k, v in PALABRAS.items()}

T_REALEZA, T_SUMA0, T_SUMA1 = 9.4, 14.6, 17.6

ESCENAS = [  # "!" robot · "P:" Paco · "V:" Voltio · resto, narradora
    (0.0, 4.4, "La IA convierte cada palabra en números: un punto en un mapa"),
    (4.4, 9.0, "Las palabras parecidas quedan cerca: perro y gato, manzana y pera"),
    (9.0, 14.0, "Y hasta las DIRECCIONES significan algo: de hombre a rey… «realeza»"),
    (14.0, 18.6, "!Mira: rey − hombre + mujer = …", "explica"),
    (18.6, 23.0, "V:¡REINA! Nadie se lo explicó: ¡lo sacó de leer textos!"),
    (23.0, 27.4, "P:O sea, que para la IA un can y un perro… ¡son vecinos!"),
    (27.4, 32.0, "!¡Sígueme y te enseño más trucos de palabras!"),
]
VOZ = {
    "gancho": "¡Sé hacer cuentas con palabras!",
    0: "La IA convierte cada palabra en números: un punto en un mapa.",
    1: "Las palabras parecidas quedan cerca. Perro y gato. Manzana y pera.",
    2: "Y hasta las direcciones significan algo. De hombre a rey: realeza.",
    3: "Mira: rey, menos hombre, más mujer, es igual a…",
}
EFECTOS = ([(0.4 + 0.12 * k, "pop") for k in range(0, len(PALABRAS), 3)]
           + [(4.8, "whoosh"), (T_REALEZA, "whoosh"), (11.4, "whoosh"),
              (T_SUMA0, "whoosh"), (T_SUMA1, "pop"), (18.8, "pop")])
PORTADA = dict(titulo=["Para una IA,", "las palabras", "son coordenadas"], amarilla=2, t=19.5,
               gesto="explica")

TEASER = {'t': 19.0, 'texto': 'Esta IA hace cuentas con palabras', 'pregunta': '◀◀  ¿Cómo lo hace?', 'y': 0.36}

reel = Reel(9, "Para una IA, las palabras\nson coordenadas", ESCENAS, 32.0, voz=VOZ,
            efectos=EFECTOS, serie=SERIE_CERO, musica={"bpm": 96}, portada=PORTADA,
            teaser=TEASER, retratos=True)
ax = reel.ax
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.8)
ax.set_aspect("equal")
# cuadrícula tenue: es un "mapa" de coordenadas
for v in np.arange(1, 10):
    ax.plot([v, v], [0.2, 7.6], color="#1A2230", lw=1, zorder=0)
for v in np.arange(1, 8):
    ax.plot([0.2, 9.8], [v, v], color="#1A2230", lw=1, zorder=0)

artistas = []


def add(a):
    artistas.append(a)
    return a


def limpiar():
    while artistas:
        artistas.pop().remove()


def flecha(p0, p1, color, lw=3, alpha=1.0, ls="-"):
    add(ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=22, color=color,
                                     lw=lw, alpha=alpha, ls=ls, zorder=5,
                                     shrinkA=12, shrinkB=12)))


def draw(t):
    limpiar()
    # ------------------------------------------------ palabras como puntos
    for k, (pal, (x, y, grupo)) in enumerate(PALABRAS.items()):
        a = ease((t - 0.4 - 0.12 * k) / 0.3)
        if a <= 0:
            continue
        color = COLOR[grupo]
        resalta = (4.8 <= t < 9.0 and pal in ("perro", "gato", "manzana", "pera")) or \
                  (23.2 <= t < 27.4 and pal in ("can", "perro")) or \
                  (t >= T_SUMA1 and pal == "reina")
        r = 0.16 * a * (1.5 if resalta else 1)
        add(ax.add_patch(Circle((x, y), r, fc=ACCENT if resalta else color, ec=FG, lw=1.5,
                                zorder=6)))
        add(ax.text(x, y - 0.38, pal, ha="center", va="top", size=13 if not resalta else 15,
                    weight="black", color=ACCENT if resalta else color, alpha=a, zorder=7))
        if t >= 2.0 and pal in ("perro", "rey"):  # sus "coordenadas"
            add(ax.text(x + 0.25, y + 0.18, f"({x:.1f}, {y:.1f})", size=10, weight="bold",
                        color=MUTED, alpha=ease((t - 2.0) / 0.4), zorder=7))

    # ------------------------------------------------ cercanía
    if 4.8 <= t < 9.0:
        a = ease((t - 4.8) / 0.4)
        for p, q in (("perro", "gato"), ("manzana", "pera")):
            add(ax.plot(*zip(P[p], P[q]), color=ACCENT, lw=2, ls=":", alpha=a, zorder=5)[0])
            m = (P[p] + P[q]) / 2
            add(ax.text(m[0] + 0.2, m[1] + 0.15, "cerca", size=11, weight="bold", color=ACCENT,
                        alpha=a, zorder=7))

    # ------------------------------------------------ dirección "realeza"
    if t >= T_REALEZA:
        a = ease((t - T_REALEZA) / 0.5)
        flecha(P["hombre"], P["hombre"] + (P["rey"] - P["hombre"]) * a, ACCENT, alpha=1)
        if t >= 11.4:
            b = ease((t - 11.4) / 0.5)
            flecha(P["mujer"], P["mujer"] + (P["reina"] - P["mujer"]) * b, ACCENT, alpha=0.9)
            add(ax.text(4.35, 2.9, "realeza", size=13, weight="black", color=ACCENT, rotation=63,
                        ha="center", va="center", alpha=b, zorder=7))

    # ------------------------------------------------ rey − hombre + mujer
    if t >= T_SUMA0 - 0.6:
        a = ease((t - T_SUMA0 + 0.6) / 0.4)
        flecha(P["hombre"], P["mujer"], C2, lw=2.5, alpha=a, ls="--")
        mov = ease((t - T_SUMA0) / (T_SUMA1 - T_SUMA0))
        q = P["rey"] + (P["mujer"] - P["hombre"]) * mov
        if t >= T_SUMA0:
            flecha(P["rey"], q, C2, lw=3)
        if t < T_SUMA1:
            add(ax.text(q[0] + 0.3, q[1] + 0.35, "?", size=24, weight="black", color=C2,
                        zorder=8))
        add(ax.text(5.0, 7.45, "rey − hombre + mujer =" + (" reina" if t >= T_SUMA1 else " …"),
                    ha="center", va="top", size=17, weight="black",
                    color=ACCENT if t >= T_SUMA1 else FG, zorder=8,
                    bbox=dict(boxstyle="round,pad=0.3", fc="#0E1117", ec=C2, lw=2)))


if __name__ == "__main__":
    reel.render(draw, "12_palabras")
