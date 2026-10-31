"""IA desde cero #6 · ¿Por qué la IA se inventa cosas? (alucinaciones)."""
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

from base import Reel, ease, ACCENT, C1, C2, C3, MUTED, FG, SERIE_CERO

PANEL = "#161D2A"
PREGUNTA = "¿Qué premio ganó @hacerlointeligente en 2019?".split()
INICIO = ["Ganó", "el"]
CANDIDATOS = [("Premio", 46), ("concurso", 22), ("trofeo", 9), ("no lo sé", 4)]
RESTO = ["Nacional", "de", "Robótica", "de", "2019."]
T_PREGUNTA = (0.4, 0.33)
T_BARRAS, T_ELIGE = 4.8, 8.6
T_RESTO0, T_RESTO_PASO = 9.8, 0.55
T_SELLO = 16.6

ESCENAS = [  # "!" = habla el robot (subtítulo amarillo); el resto, la narradora
    (0.0, 4.4, "Le preguntas algo que no sabe… (esta cuenta no existía en 2019)"),
    (4.4, 9.4, "La IA no busca la verdad: elige la palabra que SUENA más probable"),
    (9.4, 14.0, "Palabra a palabra, la frase suena perfecta…"),
    (14.0, 18.4, "!¡Ganó el Premio Nacional de Robótica! …Ups, me lo he inventado.", "piensa"),
    (18.4, 23.2, "Eso es una ALUCINACIÓN: suena muy seguro, pero es falso"),
    (23.2, 27.6, "Truco: pide fuentes y comprueba los datos importantes"),
    (27.6, 32.0, "!¡Sígueme! Yo también me equivoco… pero aprendo"),
]
VOZ = {
    "gancho": "¿Por qué la IA se inventa cosas? ¡Te lo confieso!",
    0: "Le preguntas algo que la IA no puede saber.",
    1: "La IA no busca la verdad: elige la palabra que suena más probable.",
    3: "¡Ganó el Premio Nacional de Robótica! … Ups. Me lo he inventado.",
    4: "Eso es una alucinación: suena muy seguro, pero es falso.",
    5: "Un truco: pide fuentes, y comprueba los datos importantes.",
    6: "¡Sígueme! Yo también me equivoco… pero aprendo.",
}
EFECTOS = ([(T_PREGUNTA[0] + k * T_PREGUNTA[1], "pop") for k in range(0, len(PREGUNTA), 2)]
           + [(T_BARRAS, "whoosh"), (T_ELIGE, "pop")]
           + [(T_RESTO0 + k * T_RESTO_PASO, "pop") for k in range(len(RESTO))]
           + [(T_SELLO, "error"), (18.6, "whoosh")]
           + [(23.6 + 0.8 * k, "pop") for k in range(3)])
PORTADA = dict(titulo=["¿Por qué la IA", "se inventa", "cosas?"], amarilla=1, t=17.5,
               gesto="piensa")

reel = Reel(6, "¿Por qué la IA\nse inventa cosas?", ESCENAS, 32.0, voz=VOZ, efectos=EFECTOS,
            serie=SERIE_CERO, musica={"bpm": 92}, portada=PORTADA)
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


def escribir(palabras, x0, y0, x_max, colores, size=16, alto_linea=0.58):
    """Coloca palabras con salto de línea automático; devuelve (x, y) final."""
    r = reel.fig.canvas.get_renderer()
    inv = ax.transData.inverted()
    x, y = x0, y0
    for p, color in zip(palabras, colores):
        txt = add(ax.text(x, y, p, size=size, weight="bold", color=color, va="top", zorder=6))
        bb = txt.get_window_extent(renderer=r)
        (a0, _), (a1, _) = inv.transform([[bb.x0, bb.y0], [bb.x1, bb.y1]])
        if x + (a1 - a0) > x_max and x > x0:
            x, y = x0, y - alto_linea
            txt.set_position((x, y))
        x += (a1 - a0) + 0.16
    return x, y


def respuesta_en(t):
    if t < T_BARRAS:
        return []
    pal = list(INICIO)
    if t >= T_ELIGE + 0.35:
        pal.append(CANDIDATOS[0][0])
    if t >= T_RESTO0:
        n = min(int((t - T_RESTO0) / T_RESTO_PASO) + 1, len(RESTO))
        pal += RESTO[:n]
    return pal


def draw(t):
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    if not hasattr(reel.fig.canvas, "get_renderer"):
        FigureCanvasAgg(reel.fig)
    limpiar()

    # ------------------------------------------------ pregunta (burbuja de la persona)
    n = int(np.clip((t - T_PREGUNTA[0]) / T_PREGUNTA[1] + 1, 0, len(PREGUNTA)))
    add(ax.add_patch(FancyBboxPatch((1.6, 6.15), 8.1, 1.35,
                                    boxstyle="round,pad=0,rounding_size=0.3",
                                    fc="#2A3344", ec="none", zorder=3)))
    add(ax.text(1.85, 7.38, "tú", size=11, weight="bold", color=MUTED, va="top", zorder=6))
    escribir(PREGUNTA[:n], 2.3, 7.35, 9.4, [FG] * n, size=15, alto_linea=0.52)

    # ------------------------------------------------ respuesta de la IA
    if t >= T_BARRAS - 0.3:
        add(ax.add_patch(FancyBboxPatch((0.3, 4.05), 8.6, 1.8,
                                        boxstyle="round,pad=0,rounding_size=0.3",
                                        fc=PANEL, ec=C1, lw=2.2, zorder=3)))
        add(ax.text(0.55, 5.72, "IA", size=11, weight="black", color=C1, va="top", zorder=6))
        pal = respuesta_en(t)
        cols = [C1] * len(pal)
        if pal:
            cols[-1] = ACCENT
        x, y = escribir(pal, 1.2, 5.65, 8.6, cols, size=17)
        if (t * 2) % 1 < 0.6 and t < 13.0:
            add(ax.add_patch(Rectangle((x - 0.05, y - 0.45), 0.12, 0.42, fc=ACCENT, ec="none",
                                       zorder=6)))
        if t >= T_SELLO:  # sello de "INVENTADO"
            a = ease((t - T_SELLO) / 0.25)
            add(ax.text(4.6, 4.95, "INVENTADO", ha="center", va="center", size=26 + 12 * (1 - a),
                        weight="black", color=C2, rotation=-8, alpha=a, zorder=9,
                        bbox=dict(boxstyle="round,pad=0.2", fc="none", ec=C2, lw=4, alpha=a)))

    # ------------------------------------------------ barras: la palabra que "suena" mejor
    if T_BARRAS <= t < T_RESTO0 + 0.3:
        crece = ease((t - T_BARRAS - 0.3) / 0.9)
        elegida = t >= T_ELIGE
        add(ax.text(0.4, 3.55, "¿siguiente palabra?", size=13, weight="bold", color=MUTED,
                    va="center", zorder=6))
        for i, (pal, prob) in enumerate(CANDIDATOS):
            y = 2.8 - i * 0.78
            sincera = pal == "no lo sé"
            col = ACCENT if (i == 0 and elegida) else (C3 if sincera else C1)
            add(ax.text(2.6, y, pal, size=15, weight="black", ha="right", va="center",
                        color=col, zorder=6))
            largo = 5.5 * prob / 50 * crece
            add(ax.add_patch(FancyBboxPatch((2.85, y - 0.26), max(largo, 0.05), 0.52,
                                            boxstyle="round,pad=0,rounding_size=0.12",
                                            fc=col, ec="none", alpha=0.85, zorder=5)))
            add(ax.text(3.0 + largo, y, f"{prob * crece:.0f} %", size=13, weight="bold",
                        va="center", color=col, zorder=6))
            if sincera and t >= 6.6:
                add(ax.text(4.5, y, "← la respuesta sincera casi nunca gana",
                            size=11, weight="bold", va="center", color=C3, zorder=6,
                            alpha=ease((t - 6.6) / 0.4)))

    # ------------------------------------------------ alucinación + consejos
    if t >= 18.6:
        a = ease((t - 18.6) / 0.4)
        add(ax.text(5, 2.95, "ALUCINACIÓN", ha="center", va="center", size=30, weight="black",
                    color=C2, alpha=a, zorder=6))
        add(ax.text(5, 2.25, "suena seguro  ·  es falso", ha="center", va="center", size=15,
                    weight="bold", color=FG, alpha=a, zorder=6))
    if t >= 23.4:
        consejos = ["✓  Pide fuentes", "✓  Comprueba los datos importantes",
                    "✓  Pregunta «¿estás seguro?»"]
        for k, c in enumerate(consejos):
            b = ease((t - 23.6 - 0.8 * k) / 0.3)
            add(ax.text(1.0, 1.5 - k * 0.55, c, size=14, weight="black", color=C3, alpha=b,
                        va="center", zorder=6))


if __name__ == "__main__":
    reel.render(draw, "09_alucinaciones")
