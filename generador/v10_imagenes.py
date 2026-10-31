"""IA desde cero #7 · Así crea una IA una imagen de la nada (modelos de difusión)."""
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

from base import Reel, ease, ACCENT, C1, C3, MUTED, FG, SERIE_CERO

PANEL = "#161D2A"
N = 72                      # resolución de la imagen generada (píxeles por lado)
PASOS = 50


def paisaje(n=N, sol=(0.66, 0.62), montes=(0.42, 0.33), tono=0.0):
    """Montañas al atardecer, dibujadas con matemáticas (sin fotos de nadie)."""
    yy, xx = np.mgrid[0:1:n * 1j, 0:1:n * 1j]
    y = 1 - yy
    cielo_arr = np.array([0.36 + tono, 0.16, 0.45])     # violeta arriba
    cielo_abj = np.array([1.0, 0.55 + tono * 0.3, 0.25])  # naranja en el horizonte
    img = cielo_abj * (1 - y[..., None]) + cielo_arr * y[..., None]
    d = np.hypot(xx - sol[0], (y - sol[1]) * 1.0)
    img = np.where((d < 0.11)[..., None], [1.0, 0.86, 0.35], img)
    img += (np.exp(-d * 6) * 0.25)[..., None] * np.array([1, 0.7, 0.3])
    lejos = montes[0] + 0.12 * np.sin(xx * 7 + 1) + 0.06 * np.sin(xx * 17)
    img = np.where((y < lejos)[..., None], [0.33, 0.18, 0.42], img)
    cerca = montes[1] + 0.1 * np.sin(xx * 5 + 3) + 0.04 * np.sin(xx * 23)
    img = np.where((y < cerca)[..., None], [0.15, 0.09, 0.25], img)
    lago = y < 0.14
    img = np.where(lago[..., None], img[::-1] * 0.55 + np.array([0.05, 0.05, 0.12]), img)
    return np.clip(img, 0, 1)


IMAGEN = paisaje()
RUIDO = np.random.default_rng(10).normal(0, 1, IMAGEN.shape)
EJEMPLOS = [paisaje(24, (0.3 + 0.2 * k % 0.5, 0.5 + 0.05 * k), (0.35 + 0.04 * (k % 3), 0.25),
                    tono=0.1 * (k % 2)) for k in range(9)]

T_P0, T_P1, T_P2, T_FIN = 4.6, 9.0, 15.0, 17.2   # progreso del "limpiado"

ESCENAS = [  # "!" = habla el robot (subtítulo amarillo); el resto, la narradora
    (0.0, 4.2, "Le pides: «montañas al atardecer». Y empieza… con puro ruido"),
    (4.2, 9.0, "Una red neuronal mira el ruido… y quita un poquito"),
    (9.0, 15.0, "Y otra vez. Y otra. En cada paso, la imagen se ve más clara"),
    (15.0, 19.4, "!¡Como ver formas en las nubes… pero a lo bestia!", "explica"),
    (19.4, 24.0, "Aprendió viendo millones de imágenes con su descripción"),
    (24.0, 28.0, "Así funcionan los generadores de imágenes con IA"),
    (28.0, 32.5, "!¡Sígueme! En el próximo, me verás aprender a andar"),
]
VOZ = {
    "gancho": "¿Cómo pinto una imagen de la nada? ¡Mira!",
    0: "Le pides: montañas al atardecer. Y empieza… con puro ruido.",
    2: "Y otra vez. Y otra. En cada paso, la imagen se ve más clara.",
    6: "¡Sígueme! En el próximo, me verás aprender a andar.",
}
EFECTOS = ([(0.4, "pop"), (1.6, "whoosh"), (T_P0, "whoosh")]
           + [(T_P1 + k * 1.2, "whoosh") for k in range(5)]
           + [(T_FIN, "pop"), (19.8, "pop"), (24.2, "pop")])
PORTADA = dict(titulo=["Así crea una IA", "una imagen", "de la nada"], amarilla=1, t=13.0,
               gesto="explica")

reel = Reel(7, "Así crea una IA\nuna imagen de la nada", ESCENAS, 32.5, voz=VOZ,
            efectos=EFECTOS, serie=SERIE_CERO, musica={"bpm": 90}, portada=PORTADA)
ax = reel.ax
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.8)
ax.set_aspect("equal")

lienzo = ax.imshow(np.zeros_like(IMAGEN), extent=(0.4, 5.4, 1.3, 6.3), origin="upper",
                   interpolation="nearest", zorder=3)
artistas = []


def add(a):
    artistas.append(a)
    return a


def limpiar():
    while artistas:
        artistas.pop().remove()


def progreso(t):
    """0 = solo ruido, 1 = imagen terminada."""
    if t < T_P0:
        return 0.0
    if t < T_P1:
        return 0.12 * ease((t - T_P0) / (T_P1 - T_P0))
    if t < T_P2:
        # avanza a saltos (un "paso" cada poco), como el algoritmo
        k = (t - T_P1) / (T_P2 - T_P1)
        escalon = np.floor(k * 12) / 12 + ease((k * 12) % 1) / 12
        return 0.12 + 0.73 * escalon
    return 0.85 + 0.15 * ease((t - T_P2) / (T_FIN - T_P2))


def draw(t):
    limpiar()
    p = progreso(t)
    # mezcla imagen + ruido (como un modelo de difusión, de mucho a nada de ruido)
    a = p ** 1.6
    img = 0.5 + np.sqrt(a) * (IMAGEN - 0.5) + np.sqrt(1 - a) * RUIDO * 0.32
    lienzo.set_data(np.clip(img, 0, 1))
    lienzo.set_alpha(ease(t / 0.4))
    add(ax.add_patch(Rectangle((0.4, 1.3), 5, 5, fc="none", ec=FG, lw=2, zorder=4)))
    paso = int(round(PASOS * (1 - p)))
    add(ax.text(2.9, 0.75, "¡imagen terminada!" if p >= 0.999 else f"paso {paso} de {PASOS}",
                ha="center", va="center", size=15, weight="black",
                color=C3 if p >= 0.999 else ACCENT, zorder=6))

    if t < 19.4:
        # ---------------------------------------- texto pedido + la red que limpia
        b = ease((t - 0.4) / 0.4)
        add(ax.add_patch(FancyBboxPatch((5.85, 5.0), 3.85, 1.6,
                                        boxstyle="round,pad=0,rounding_size=0.25",
                                        fc=PANEL, ec=C1, lw=2, alpha=b, zorder=3)))
        add(ax.text(6.05, 6.4, "lo que pides:", size=11, weight="bold", color=MUTED, va="top",
                    alpha=b, zorder=6))
        add(ax.text(7.77, 5.6, "«montañas al\natardecer»", size=15, weight="black",
                    color=FG, ha="center", va="center", alpha=b, zorder=6, linespacing=1.1))
        if t >= T_P0 - 0.2:
            c = ease((t - T_P0 + 0.2) / 0.4)
            add(ax.add_patch(FancyBboxPatch((6.3, 2.2), 2.95, 1.5,
                                            boxstyle="round,pad=0,rounding_size=0.3",
                                            fc=PANEL, ec=ACCENT, lw=2.5, alpha=c, zorder=3)))
            add(ax.text(7.77, 2.95, "red\nneuronal", size=15, weight="black", color=ACCENT,
                        ha="center", va="center", alpha=c, zorder=6, linespacing=1.0))
            # flechas: imagen → red → imagen (bucle de "quita un poco de ruido")
            pulso = 0.5 + 0.5 * np.sin(2 * np.pi * 1.6 * t)
            add(ax.annotate("", xy=(6.25, 3.25), xytext=(5.5, 4.2),
                            arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=2.5,
                                            mutation_scale=18, alpha=c), zorder=5))
            add(ax.annotate("", xy=(5.5, 2.2), xytext=(6.25, 2.6),
                            arrowprops=dict(arrowstyle="-|>", color=C3, lw=2.5,
                                            mutation_scale=18, alpha=c), zorder=5))
            add(ax.text(7.77, 1.75, "− un poco de ruido", size=12, weight="bold", color=C3,
                        ha="center", va="center", alpha=c * (0.6 + 0.4 * pulso), zorder=6))
    else:
        # ---------------------------------------- de dónde lo aprendió
        b = ease((t - 19.6) / 0.4)
        add(ax.text(7.75, 6.55, "aprendió de…", size=12, weight="bold", color=MUTED,
                    ha="center", va="center", alpha=b, zorder=6))
        for k, mini in enumerate(EJEMPLOS):
            fila, col = divmod(k, 3)
            c = ease((t - 19.8 - 0.12 * k) / 0.3)
            x0, y0 = 6.0 + col * 1.25, 4.9 - fila * 1.45
            add(ax.imshow(mini, extent=(x0, x0 + 1.05, y0, y0 + 1.05), origin="upper",
                          alpha=c, zorder=4))
            add(ax.text(x0 + 0.52, y0 - 0.17, "«paisaje»", size=7, color=MUTED, ha="center",
                        va="center", alpha=c, zorder=6))
        add(ax.text(7.75, 0.75, "…millones de imágenes", size=13, weight="black", color=FG,
                    ha="center", va="center", alpha=ease((t - 21.2) / 0.4), zorder=6))


if __name__ == "__main__":
    reel.render(draw, "10_imagenes")
