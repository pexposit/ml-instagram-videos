"""IA desde cero #3 · Una red neuronal reconoce un número escrito a mano."""
import numpy as np
from matplotlib.patches import Circle, Rectangle
from matplotlib.collections import LineCollection

from base import Reel, ease, ACCENT, C1, C3, MUTED, FG, SERIE_CERO

PANEL = "#161D2A"
# Números "escritos a mano" de 7×9 píxeles: '#' = tinta, '+' = medio, '.' = vacío
DIGITOS = {
    7: ["#######", "######+", ".....##", "....##.", "...##..", "...#+..", "..##...", "..##...",
        "..#+..."],
    3: [".#####.", "#+...##", ".....##", "..####.", "....+##", ".....##", "#....##", "##+.##+",
        ".####.."],
    1: ["...##..", "..###..", ".+.##..", "...##..", "...##..", "...##..", "...##..", "...##..",
        "..####."],
    4: ["....##.", "...###.", "..#+##.", ".#+.##.", "#+..##.", "#######", "....##.", "....##.",
        "....##."],
    0: ["..###..", ".##.##.", "##...##", "#+...+#", "#.....#", "#+...+#", "##...##", ".##.##.",
        "..###.."],
    9: [".####..", "##..##.", "#....##", "##..###", ".####+#", ".....##", "....##.", "...##..",
        "..##..."],
}
VALOR = {"#": 9, "+": 5, ".": 0}
CELDA = 0.34
GRID_X0, GRID_Y0 = 0.25, 2.35            # esquina inferior izquierda de la cuadrícula

CAPAS_X = [3.25, 4.45, 5.65, 6.85, 8.05]
CAPAS_N = [8, 6, 6, 5, 10]
NOMBRES = [None, "trazos", "esquinas", "formas", None]
SALIDA = len(CAPAS_N) - 1


def ys(n):
    alto = 6.9 if n == 10 else 5.6
    return np.linspace(3.9 + alto / 2, 3.9 - alto / 2, n)


NODOS = [np.c_[np.full(n, x), ys(n)] for x, n in zip(CAPAS_X, CAPAS_N)]
rng = np.random.default_rng(5)
ACTIVACION = [rng.uniform(0.25, 1.0, n) for n in CAPAS_N[:-1]]
PESOS = [rng.normal(0, 1, (a, b)) for a, b in zip(CAPAS_N[:-1], CAPAS_N[1:])]


def probabilidades(ganador, seed):
    r = np.random.default_rng(seed)
    p = r.uniform(0.0, 0.03, 10)
    p[ganador] = 0
    p = p / p.sum() * 0.06
    p[ganador] = 0.94
    return p


T_CAPA = [8.4, 9.7, 11.0, 12.3, 14.2]    # cuándo se enciende cada capa
CICLO = [3, 1, 4, 0, 9, 7]               # números que "ha visto" al aprender
T_CICLO0, T_CICLO_PASO = 22.4, 0.65

ESCENAS = [  # "!" = habla el robot (subtítulo amarillo); el resto, la narradora
    (0.0, 4.2, "Para una IA, una imagen son números: uno por cada píxel"),
    (4.2, 8.0, "Esos números entran en una red de neuronas"),
    (8.0, 14.0, "Cada capa detecta algo: trazos, esquinas… formas"),
    (14.0, 18.0, "Al final, cada neurona vota por un número"),
    (18.0, 22.0, "!¡Gana el 7, con un 94 %! Lo sabía.", "pulgar"),
    (22.0, 26.6, "Lo aprendió viendo miles de números escritos a mano"),
    (26.6, 32.0, "!¡Sígueme! En el próximo: cómo escribe ChatGPT"),
]
VOZ = {
    "gancho": "¿Cómo leo un número escrito a mano? ¡Mira!",
    2: "Cada capa detecta algo. Trazos. Esquinas. Formas.",
    4: "¡Gana el siete, con un noventa y cuatro por ciento! Lo sabía.",
    6: "¡Sígueme! En el próximo: cómo escribe ChatGPT.",
}
EFECTOS = ([(2.0, "pop"), (4.6, "whoosh")] + [(tc, "pop") for tc in T_CAPA]
           + [(18.2, "pop")] + [(T_CICLO0 + k * T_CICLO_PASO, "pop") for k in range(len(CICLO))])

PORTADA = dict(titulo=["Cómo lee una IA", "un número", "escrito a mano"], amarilla=1, t=19.5, gesto="senala",
               robot_x=0.17)

reel = Reel(3, "Cómo reconoce una IA\nun número escrito\na mano", ESCENAS, 32.0, voz=VOZ,
            efectos=EFECTOS, serie=SERIE_CERO, musica={"bpm": 100},
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


def digito_en(t):
    if t < T_CICLO0:
        return 7
    k = min(int((t - T_CICLO0) / T_CICLO_PASO), len(CICLO) - 1)
    return CICLO[k]


def dibujar_cuadricula(t, digito):
    a = ease(t / 0.6)
    numeros = t >= 2.0
    filas = DIGITOS[digito]
    for i, fila in enumerate(filas):
        for j, c in enumerate(fila):
            v = VALOR[c]
            x = GRID_X0 + j * CELDA
            y = GRID_Y0 + (len(filas) - 1 - i) * CELDA
            gris = 0.12 + 0.88 * v / 9
            add(ax.add_patch(Rectangle((x, y), CELDA * 0.94, CELDA * 0.94,
                                       fc=(gris, gris, gris), ec="none", alpha=a, zorder=3)))
            if numeros:
                add(ax.text(x + CELDA * 0.47, y + CELDA * 0.47, str(v), ha="center",
                            va="center", size=7, weight="bold",
                            color="#0E1117" if v > 4 else "#7A8494", zorder=4,
                            alpha=ease((t - 2.0) / 0.5)))


def draw(t):
    limpiar()
    digito = digito_en(t)
    dibujar_cuadricula(t, digito)
    if t < 4.4:
        return

    # flecha de la imagen a la red
    a = ease((t - 4.4) / 0.5)
    add(ax.annotate("", xy=(CAPAS_X[0] - 0.35, 3.9), xytext=(2.75, 3.9),
                    arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=2.5, mutation_scale=20,
                                    alpha=a), zorder=2))

    # ------------------------------------------------ conexiones
    for c in range(SALIDA):
        aparece = ease((t - 4.9 - 0.3 * c) / 0.6)
        if aparece <= 0:
            continue
        segs, cols = [], []
        encendida = t >= T_CAPA[c] + 0.3
        for i, p in enumerate(NODOS[c]):
            for j, q in enumerate(NODOS[c + 1]):
                segs.append([p, q])
                if encendida:
                    w = PESOS[c][i, j]
                    fuerza = np.clip(abs(w) * ACTIVACION[c][i], 0, 1.4)
                    cols.append((0.3, 0.79, 0.94, 0.08 + 0.35 * fuerza / 1.4))
                else:
                    cols.append((0.55, 0.58, 0.65, 0.12 * aparece))
        add(ax.add_collection(LineCollection(segs, colors=cols, linewidths=1.2, zorder=1)))
        # impulso viajando por la capa
        f = (t - T_CAPA[c] - 0.3) / (T_CAPA[c + 1] - T_CAPA[c] - 0.3)
        if 0 < f < 1:
            x = CAPAS_X[c] + (CAPAS_X[c + 1] - CAPAS_X[c]) * f
            add(ax.plot([x, x], [0.3, 7.5], color=ACCENT, lw=3, alpha=0.35 * np.sin(np.pi * f),
                        zorder=2)[0])

    # ------------------------------------------------ neuronas
    probs = probabilidades(digito, digito)
    for c, nodos in enumerate(NODOS):
        aparece = ease((t - 4.6 - 0.3 * c) / 0.4)
        if aparece <= 0:
            continue
        r = 0.27 if c == SALIDA else 0.3
        encendida = ease((t - T_CAPA[c]) / 0.4)
        for i, p in enumerate(nodos):
            nivel = (probs[i] / 0.94 if c == SALIDA else ACTIVACION[c][i]) * encendida
            ganador = c == SALIDA and i == digito and t >= 18.0
            relleno = tuple(np.clip([0.09 + 0.21 * nivel, 0.11 + 0.68 * nivel,
                                     0.16 + 0.78 * nivel], 0, 1))
            if ganador:
                relleno = ACCENT
                pulso = 0.5 + 0.5 * np.sin(2 * np.pi * 1.6 * t)
                add(ax.add_patch(Circle(p, r + 0.18, fc=ACCENT, ec="none", alpha=0.25 * pulso,
                                        zorder=4)))
            add(ax.add_patch(Circle(p, r * aparece, fc=relleno, ec=FG, lw=1.4, zorder=5)))
            if c == SALIDA:
                add(ax.text(*p, str(i), ha="center", va="center", size=10, weight="black",
                            color="#0E1117" if (nivel > 0.5 or ganador) else FG, zorder=6))
        if NOMBRES[c] and t >= T_CAPA[c]:
            add(ax.text(CAPAS_X[c], 7.7 if c % 2 else 7.25, NOMBRES[c], ha="center", va="top",
                        size=11,
                        weight="bold", color=ACCENT, alpha=ease((t - T_CAPA[c]) / 0.4),
                        zorder=6))

    # ------------------------------------------------ votos (barras de probabilidad)
    if t >= T_CAPA[SALIDA]:
        crece = ease((t - T_CAPA[SALIDA]) / 0.8)
        for i, p in enumerate(NODOS[SALIDA]):
            largo = 1.0 * probs[i] * crece
            ganador = i == digito and t >= 18.0
            add(ax.add_patch(Rectangle((p[0] + 0.42, p[1] - 0.13), max(largo, 0.03), 0.26,
                                       fc=ACCENT if ganador else C1, ec="none",
                                       alpha=1 if ganador else 0.7, zorder=5)))
            if ganador or probs[i] > 0.5:
                add(ax.text(p[0] + 0.5 + largo, p[1], f"{probs[i] * 100:.0f} %", ha="left",
                            va="center", size=12, weight="black",
                            color=ACCENT if ganador else FG, zorder=6))


if __name__ == "__main__":
    reel.render(draw, "06_red_neuronal")
