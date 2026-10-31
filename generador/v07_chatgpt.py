"""IA desde cero #4 · Cómo escribe ChatGPT: adivina la siguiente palabra, una y otra vez."""
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

from base import Reel, ease, ACCENT, C1, MUTED, FG, SERIE_CERO

PANEL = "#161D2A"
PROMPT = "El gato se sentó en el".split()
PASOS = [  # candidatos para la siguiente palabra y su probabilidad; se elige el primero
    [("sofá", 41), ("suelo", 27), ("tejado", 12), ("coche", 3)],
    [("y", 38), (".", 30), ("a", 9), ("para", 6)],
    [("se", 44), ("empezó", 18), ("miró", 11), ("no", 7)],
    [("durmió.", 52), ("quedó", 21), ("lavó", 9), ("fue", 5)],
]
EXTRA = "Al despertar tenía hambre, así que fue a buscar a su dueño y le maulló".split()

T_TECLEO = (0.3, 3.4)
T_PASO = [4.6, 10.6, 12.6, 14.4, 16.2]    # inicio de cada paso (+ fin del último)
T_RAPIDO0, T_RAPIDO_PASO = 18.8, 0.22

ESCENAS = [
    (0.0, 4.4, "Le das un texto: «El gato se sentó en el…»"),
    (4.4, 9.2, "Calcula qué palabra es más probable que venga después"),
    (9.2, 12.6, "Elige una… y la añade al texto"),
    (12.6, 18.6, "Y repite. Palabra tras palabra."),
    (18.6, 22.8, "!Así escribe respuestas enteras: de una palabra en una"),
    (22.8, 27.0, "Lo aprendió leyendo muchísimos textos"),
    (27.0, 31.5, "!Sigue a @hacerlointeligente para entender la IA desde cero"),
]
VOZ = {
    "gancho": "ChatGPT no escribe la respuesta de golpe. La adivina, palabra a palabra.",
    0: "Le das un texto. El gato se sentó en el…",
    1: "Calcula qué palabra es más probable que venga después.",
    2: "Elige una, y la añade al texto.",
    3: "Y repite. Palabra tras palabra.",
    4: "Así escribe respuestas enteras: de una palabra en una.",
    5: "Lo aprendió leyendo muchísimos textos.",
    6: "Sigue a hacerlo inteligente para entender la IA desde cero.",
}
EFECTOS = ([(T_TECLEO[0] + k * 0.5, "pop") for k in range(len(PROMPT))]
           + [(T_PASO[0], "whoosh"), (9.8, "pop")]
           + [(tp + 0.9, "pop") for tp in T_PASO[1:4]]
           + [(T_RAPIDO0 + k * T_RAPIDO_PASO * 2, "pop") for k in range(len(EXTRA) // 2)]
           + [(22.9, "whoosh")])

PORTADA = dict(titulo=["Así escribe", "ChatGPT"], amarilla=1, t=13.4, gesto="explica")

reel = Reel(4, "ChatGPT escribe\nadivinando palabra\na palabra", ESCENAS, 31.5, voz=VOZ,
            efectos=EFECTOS, serie=SERIE_CERO, musica={"bpm": 94},
            portada=PORTADA)
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


def palabras_en(t):
    """Palabras visibles en la frase y cuántas son 'nuevas' (para resaltarlas)."""
    if t < T_TECLEO[1] + 0.3:
        n = int(np.clip((t - T_TECLEO[0]) / 0.5 + 1, 0, len(PROMPT)))
        return PROMPT[:n], None
    texto = list(PROMPT)
    nueva = None
    for k, paso in enumerate(PASOS):
        t_elige = (9.8 if k == 0 else T_PASO[k] + 0.9)
        if t >= t_elige:
            texto.append(paso[0][0])
            nueva = len(texto) - 1
    if t >= T_RAPIDO0:
        n = min(int((t - T_RAPIDO0) / T_RAPIDO_PASO) + 1, len(EXTRA))
        texto += EXTRA[:n]
        nueva = len(texto) - 1
    return texto, nueva


def frase(t):
    """Dibuja la frase palabra a palabra (para poder colorear la última)."""
    palabras, nueva = palabras_en(t)
    r = reel.fig.canvas.get_renderer()
    inv = ax.transData.inverted()
    x0, x, y = 0.75, 0.75, 6.95
    size = 17 if len(palabras) < 16 else 14
    alto_linea = 0.62 if size == 17 else 0.5
    for i, p in enumerate(palabras):
        color = ACCENT if i == nueva else (FG if i < len(PROMPT) else C1)
        txt = add(ax.text(x, y, p, size=size, weight="bold", color=color, va="top", zorder=6))
        bb = txt.get_window_extent(renderer=r)
        (ax0, _), (ax1, _) = inv.transform([[bb.x0, bb.y0], [bb.x1, bb.y1]])
        ancho = ax1 - ax0
        if x + ancho > 9.3 and x > x0:  # salto de línea
            x, y = x0, y - alto_linea
            txt.set_position((x, y))
        x += ancho + 0.17
    if (t * 2) % 1 < 0.6:  # cursor parpadeante
        add(ax.add_patch(Rectangle((x - 0.05, y - 0.45), 0.12, 0.42, fc=ACCENT, ec="none",
                                   zorder=6)))


def barras(t, k, a_elige):
    paso = PASOS[k]
    crece = ease((t - T_PASO[k] - (0.3 if k == 0 else 0.05)) / (0.9 if k == 0 else 0.4))
    add(ax.text(0.4, 4.15, "¿siguiente palabra?", size=13, weight="bold", color=MUTED,
                va="center", zorder=6))
    for i, (pal, prob) in enumerate(paso):
        y = 3.35 - i * 0.85
        elegida = i == 0 and a_elige
        add(ax.text(2.3, y, pal, size=16, weight="black", ha="right", va="center",
                    color=ACCENT if elegida else FG, zorder=6))
        largo = 6.0 * prob / 60 * crece
        add(ax.add_patch(FancyBboxPatch((2.55, y - 0.28), max(largo, 0.05), 0.56,
                                        boxstyle="round,pad=0,rounding_size=0.12",
                                        fc=ACCENT if elegida else C1, ec="none",
                                        alpha=1 if elegida else 0.75, zorder=5)))
        add(ax.text(2.7 + largo, y, f"{prob * crece:.0f} %", size=14, weight="bold",
                    va="center", color=ACCENT if elegida else FG, zorder=6))


def draw(t):
    limpiar()
    # burbuja de texto
    add(ax.add_patch(FancyBboxPatch((0.3, 4.75), 9.4, 2.75,
                                    boxstyle="round,pad=0,rounding_size=0.35",
                                    fc=PANEL, ec=C1, lw=2.2, zorder=3)))
    frase(t)

    if T_PASO[0] <= t < T_PASO[4] + 0.9:
        k = max(i for i in range(4) if t >= T_PASO[i])
        t_elige = 9.8 if k == 0 else T_PASO[k] + 0.9
        barras(t, k, t >= t_elige - 0.35)
    elif T_PASO[4] + 0.9 <= t < 22.8:
        add(ax.text(5, 2.4, "palabra a palabra…", size=20, weight="black", ha="center",
                    va="center", color=MUTED, alpha=0.8, zorder=6))
    elif t >= 22.8:
        # "lo que ha leído": muchas líneas de texto que pasan por debajo
        a = ease((t - 22.8) / 0.6)
        rng = np.random.default_rng(3)
        for i in range(9):
            desplaza = ((t - 22.8) * (0.9 + 0.25 * (i % 3))) % 12
            for j in range(4):
                x = -2 + j * 3.2 + desplaza - 12 * (j * 3.2 + desplaza > 11)
                largo = rng.uniform(1.2, 2.7)
                add(ax.add_patch(Rectangle((x, 0.35 + i * 0.45), largo, 0.16,
                                           fc=C1 if (i + j) % 4 else ACCENT, ec="none",
                                           alpha=0.25 * a, zorder=2)))
        add(ax.text(5, 2.35, "libros · webs · artículos · foros…", size=15, weight="black",
                    ha="center", va="center", color=FG, alpha=a, zorder=6))


if __name__ == "__main__":
    reel.render(draw, "07_chatgpt")
