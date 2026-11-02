"""IA desde cero #11 · Así ve una foto una IA (filtros / red convolucional)."""
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

from base import Reel, ease, ACCENT, C1, C3, MUTED, FG, SERIE_CERO

PANEL = "#161D2A"
N = 16


def casa():
    img = np.full((N, N), 0.08)
    img[8:15, 4:12] = 0.9                       # paredes
    for f in range(3, 8):                       # tejado
        medio = (f - 3) + 0.5
        img[f, int(7.5 - medio - 0.5):int(8.5 + medio)] = 0.65
    img[11:15, 7:9] = 0.3                       # puerta
    img[9:11, 5:7] = 0.3                        # ventana
    img[9:11, 9:11] = 0.3
    return img


IMG = casa()
KV = np.array([[-1, 0, 1]] * 3)                 # busca bordes verticales
KH = KV.T                                       # busca bordes horizontales


def convolucion(img, k):
    out = np.zeros((N - 2, N - 2))
    for i in range(N - 2):
        for j in range(N - 2):
            out[i, j] = (img[i:i + 3, j:j + 3] * k).sum()
    out = np.abs(out)
    return out / out.max()


MAPA_V, MAPA_H = convolucion(IMG, KV), convolucion(IMG, KH)
BORDES = np.clip(MAPA_V + MAPA_H, 0, 1)
TOTAL = (N - 2) ** 2

# zonas del panel (unidades de la animación)
IX0, IY0, LADO = 0.4, 1.6, 4.0                 # foto
OX0, OY0 = 5.6, 1.6                             # mapa de salida
T_FILTRO, T_V1, T_H0, T_H1 = 4.6, 13.0, 13.9, 16.2

ESCENAS = [  # "!" = habla el robot (subtítulo amarillo); el resto, la narradora
    (0.0, 4.2, "Para una IA, una foto es una cuadrícula de números"),
    (4.2, 8.6, "Pasa un pequeño FILTRO por encima, trocito a trocito"),
    (8.6, 13.6, "Este filtro busca bordes verticales… y los resalta"),
    (13.6, 18.0, "!¡Y este otro busca bordes horizontales! Ya veo el tejado", "senala"),
    (18.0, 22.8, "Capa tras capa: bordes → formas → ¡una casa!"),
    (22.8, 27.2, "Es una RED CONVOLUCIONAL: así ven las fotos los móviles"),
    (27.2, 31.8, "!¡Sígueme para ver cómo veo yo el mundo!"),
]
VOZ = {
    "gancho": "¿Quieres ver una foto como la veo yo?",
    0: "Para una IA, una foto es una cuadrícula de números.",
    3: "¡Y este otro busca bordes horizontales! Ya veo el tejado.",
    4: "Capa tras capa: bordes, formas… ¡y una casa!",
    5: "Es una red convolucional: así ven las fotos los móviles.",
}
EFECTOS = ([(0.4, "pop"), (2.0, "pop"), (T_FILTRO, "whoosh"), (T_V1, "pop"), (T_H0, "whoosh"),
            (T_H1, "pop"), (18.3, "whoosh"), (19.6, "whoosh"), (20.9, "pop")])
PORTADA = dict(titulo=["Así ve", "una foto", "una IA"], amarilla=1, t=11.0, gesto="senala")

reel = Reel(11, "Así ve una foto una IA", ESCENAS, 31.8, voz=VOZ, efectos=EFECTOS,
            serie=SERIE_CERO, musica={"bpm": 98}, portada=PORTADA)
ax = reel.ax
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.8)
ax.set_aspect("equal")
foto = ax.imshow(IMG, cmap="gray", vmin=0, vmax=1, extent=(IX0, IX0 + LADO, IY0, IY0 + LADO),
                 interpolation="nearest", zorder=2)
mapa = ax.imshow(np.zeros((N - 2, N - 2)), cmap="magma", vmin=0, vmax=1,
                 extent=(OX0, OX0 + LADO, OY0, OY0 + LADO), interpolation="nearest", zorder=2)

artistas = []


def add(a):
    artistas.append(a)
    return a


def limpiar():
    while artistas:
        artistas.pop().remove()


def kernel(k, x, y, titulo, alpha):
    add(ax.text(x, y + 0.95, titulo, ha="center", va="center", size=11, weight="bold",
                color=ACCENT, alpha=alpha, zorder=7))
    for i in range(3):
        for j in range(3):
            v = k[i, j]
            add(ax.add_patch(Rectangle((x - 0.6 + j * 0.4, y + 0.4 - i * 0.4), 0.38, 0.38,
                                       fc=PANEL, ec=ACCENT, lw=1, alpha=alpha, zorder=6)))
            add(ax.text(x - 0.41 + j * 0.4, y + 0.59 - i * 0.4, f"{v:+d}" if v else "0",
                        ha="center", va="center", size=8, weight="bold", alpha=alpha,
                        color=C3 if v > 0 else ("#F72585" if v < 0 else MUTED), zorder=7))


def escaneo(t, t0, t1, mapa_final):
    """Recorre la foto con el filtro y va revelando el mapa de salida."""
    f = np.clip((t - t0) / (t1 - t0), 0, 1)
    f = f ** 2 if t1 - t0 > 5 else f          # empieza despacio y luego acelera
    n = int(f * TOTAL)
    visible = np.zeros(TOTAL)
    visible[:n] = 1
    mapa.set_data(mapa_final * visible.reshape(N - 2, N - 2))
    if 0 < f < 1:
        i, j = divmod(min(n, TOTAL - 1), N - 2)
        c = LADO / N
        add(ax.add_patch(Rectangle((IX0 + j * c, IY0 + LADO - (i + 3) * c), 3 * c, 3 * c,
                                   fc="none", ec=ACCENT, lw=3, zorder=5)))
        co = LADO / (N - 2)
        add(ax.add_patch(Rectangle((OX0 + j * co, OY0 + LADO - (i + 1) * co), co, co,
                                   fc="none", ec=ACCENT, lw=2, zorder=5)))


def draw(t):
    limpiar()
    foto.set_alpha(ease(t / 0.4))
    add(ax.add_patch(Rectangle((IX0, IY0), LADO, LADO, fc="none", ec=FG, lw=1.5, zorder=3)))
    add(ax.text(IX0 + LADO / 2, IY0 - 0.35, "la foto", ha="center", va="center", size=13,
                weight="black", color=FG, zorder=6))

    # números de cada píxel
    if 2.0 <= t < 5.0:
        a = min(ease((t - 2.0) / 0.4), 1 - ease((t - 4.4) / 0.6))
        c = LADO / N
        for i in range(N):
            for j in range(N):
                v = int(round(IMG[i, j] * 9))
                add(ax.text(IX0 + (j + 0.5) * c, IY0 + LADO - (i + 0.5) * c, str(v), size=5,
                            ha="center", va="center", weight="bold", alpha=a, zorder=4,
                            color="#0E1117" if v > 4 else "#9AA5B4"))

    if t < T_FILTRO:
        mapa.set_alpha(0)
        return
    mapa.set_alpha(1)

    if t < 18.0:
        add(ax.add_patch(Rectangle((OX0, OY0), LADO, LADO, fc="none", ec=FG, lw=1.5, zorder=3)))
        if t < T_H0:
            kernel(KV, 5.0, 5.75, "filtro", ease((t - T_FILTRO) / 0.4))
            escaneo(t, T_FILTRO + 0.4, T_V1, MAPA_V)
            nombre = "bordes verticales"
        else:
            kernel(KH, 5.0, 5.75, "otro filtro", ease((t - T_H0) / 0.3))
            escaneo(t, T_H0 + 0.2, T_H1, MAPA_H)
            nombre = "bordes horizontales"
        add(ax.text(OX0 + LADO / 2, IY0 - 0.35, nombre, ha="center", va="center", size=13,
                    weight="black", color=ACCENT, zorder=6))
        return

    # ------------------------------------------------ capas: bordes → formas → casa
    mapa.set_alpha(0)
    etapas = [("bordes", BORDES, 18.3), ("formas", None, 19.6)]
    for k, (nombre, datos, t0) in enumerate(etapas):
        a = ease((t - t0) / 0.4)
        x0 = 5.2 + k * 2.3
        if datos is None:   # "formas": mapa más grueso (como una capa más profunda)
            datos = np.kron(BORDES.reshape(7, 2, 7, 2).max(axis=(1, 3)), np.ones((2, 2)))
        add(ax.imshow(datos, cmap="magma", vmin=0, vmax=1, alpha=a, zorder=3,
                      extent=(x0, x0 + 2.0, 3.6, 5.6), interpolation="nearest"))
        add(ax.text(x0 + 1.0, 3.3, nombre, ha="center", va="center", size=12, weight="black",
                    color=FG, alpha=a, zorder=6))
        if k == 0:
            add(ax.text(x0 + 2.15, 4.6, "→", ha="center", va="center", size=16, color=MUTED,
                        alpha=a, zorder=6))
    if t >= 20.9:
        a = ease((t - 20.9) / 0.4)
        add(ax.add_patch(FancyBboxPatch((5.4, 1.2), 4.2, 1.2,
                                        boxstyle="round,pad=0,rounding_size=0.25",
                                        fc=PANEL, ec=C3, lw=2.5, alpha=a, zorder=5)))
        add(ax.text(7.5, 1.8, "¡una casa!  97 %", ha="center", va="center", size=17,
                    weight="black", color=C3, alpha=a, zorder=6))
    add(ax.annotate("", xy=(5.15, 4.6), xytext=(4.5, 4.6),
                    arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=2.5, mutation_scale=18),
                    zorder=6))
    if t >= 23.0:
        add(ax.text(2.4, 7.2, "RED CONVOLUCIONAL", ha="center", va="center", size=16,
                    weight="black", color=ACCENT, alpha=ease((t - 23.0) / 0.4), zorder=7))


if __name__ == "__main__":
    reel.render(draw, "14_vision")
