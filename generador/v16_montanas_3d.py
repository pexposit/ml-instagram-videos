"""IA desde cero #13 · Una IA aprende bajando montañas (descenso del gradiente en 3D)."""
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from base import Reel, ease, ACCENT, C1, C2, C3, FG, SERIE_CERO


def f(x, y):
    """El "paisaje del error": un valle profundo (acierta) y otro pequeño (trampa)."""
    return (0.06 * (x ** 2 + y ** 2) + 1.6
            - 1.4 * np.exp(-((x - 1.0) ** 2 + (y - 0.8) ** 2) / 1.4)
            - 0.8 * np.exp(-((x + 1.5) ** 2 + (y + 1.3) ** 2) / 0.45)
            + 0.18 * np.sin(1.3 * x) * np.cos(1.1 * y))


def grad(x, y, h=1e-4):
    return np.array([(f(x + h, y) - f(x - h, y)) / (2 * h), (f(x, y + h) - f(x, y - h)) / (2 * h)])


def camino(x0, y0, pasos=45, lr=0.35):
    p = [np.array([x0, y0], float)]
    for _ in range(pasos):
        g = grad(*p[-1])
        paso = lr * g
        n = np.linalg.norm(paso)
        if n > 0.35:                      # pasos de tamaño razonable (se ve mejor)
            paso *= 0.35 / n
        p.append(p[-1] - paso)
    return np.array(p)


PRINCIPAL = camino(-2.6, 2.4)             # acaba en el valle profundo
ATASCADA = camino(-2.8, -2.7)             # se queda en el valle pequeño
VARIAS = [camino(*s) for s in ((2.6, -2.6), (2.7, 2.5), (-0.4, -2.8), (0.2, 2.8), (-1.2, -2.6))]

T_A0, T_A1 = 9.4, 14.6                     # bola principal
T_B0, T_B1 = 15.2, 18.6                    # bola atascada
T_C0, T_C1 = 19.6, 22.8                    # muchas bolas

ESCENAS = [  # "!" = habla el robot (subtítulo amarillo); el resto, la narradora
    (0.0, 4.4, "Imagina el error de una IA como un paisaje de montañas"),
    (4.4, 9.0, "Arriba se equivoca mucho. En el fondo del valle, acierta"),
    (9.0, 15.0, "La IA no ve el paisaje: solo nota hacia dónde baja… y da un paso"),
    (15.0, 19.4, "!¡Ups! Me he quedado en un valle pequeñito…", "piensa"),
    (19.4, 24.0, "Por eso se prueba desde muchos sitios y se queda con el mejor"),
    (24.0, 28.4, "Así se entrenan casi todas las IAs: bajando montañas de error"),
    (28.4, 33.0, "!¡Sígueme para más IA en 3D!"),
]
VOZ = {
    "gancho": "¡Aprender es bajar una montaña… a ciegas!",
    0: "Imagina el error de una IA como un paisaje de montañas.",
    1: "Arriba, se equivoca mucho. En el fondo del valle, acierta.",
    2: "La IA no ve el paisaje: solo nota hacia dónde baja… y da un paso. Y otro.",
    4: "Por eso se prueba desde muchos sitios, y se queda con el mejor.",
    5: "Así se entrenan casi todas las IAs: bajando montañas de error.",
}
EFECTOS = ([(0.4, "whoosh"), (T_A0, "pop"), (T_A1, "pop"), (T_B0, "pop"), (T_B1, "error"),
            (T_C0, "whoosh"), (T_C1, "pop")])
PORTADA = dict(titulo=["Una IA aprende", "bajando", "montañas"], amarilla=2, t=13.0,
               gesto="senala")

reel = Reel(13, "Una IA aprende\nbajando montañas", ESCENAS, 33.0, voz=VOZ, efectos=EFECTOS,
            serie=SERIE_CERO, musica={"bpm": 92}, portada=PORTADA, tres_d=True)
ax = reel.ax
ax.computed_zorder = False

G = np.linspace(-3, 3, 70)
GX, GY = np.meshgrid(G, G)
GZ = f(GX, GY)
paleta = LinearSegmentedColormap.from_list(
    "error", ["#1B4F9C", "#4CC9F0", "#7BE495", "#FFD23F", "#F72585"])
superficie = ax.plot_surface(GX, GY, GZ, cmap=paleta, rstride=1, cstride=1, linewidth=0,
                             antialiased=True, alpha=0.95, zorder=1)
ax.plot_wireframe(GX, GY, GZ, rstride=5, cstride=5, color="#0E1117", lw=0.4, alpha=0.35,
                  zorder=2)
ax.set_xlim(-3, 3)
ax.set_ylim(-3, 3)
ax.set_zlim(0, 3)

artistas = []


def add(a):
    artistas.append(a)
    return a


def limpiar():
    while artistas:
        artistas.pop().remove()


def bola(ruta, t0, t1, t, color, ms=13):
    f_ = np.clip((t - t0) / (t1 - t0), 0, 1)
    k = f_ * (len(ruta) - 1)
    i = int(np.floor(k))
    a = k - i
    p = ruta[min(i, len(ruta) - 1)] if i >= len(ruta) - 1 else ruta[i] * (1 - a) + ruta[i + 1] * a
    hecho = ruta[: i + 1]
    if len(hecho) > 1:
        add(ax.plot(hecho[:, 0], hecho[:, 1], f(hecho[:, 0], hecho[:, 1]) + 0.04, color=color,
                    lw=3, zorder=8)[0])
    add(ax.plot([p[0]], [p[1]], [f(*p) + 0.12], "o", color=color, ms=ms, mec=FG, mew=2,
                zorder=10)[0])
    return p


def etiqueta(texto, x, y, color=FG, size=15, alpha=1.0):
    add(ax.text2D(x, y, texto, transform=ax.transAxes, ha="center", va="center", size=size,
                  weight="black", color=color, alpha=alpha, zorder=12))


def draw(t):
    limpiar()
    # la cámara gira despacio alrededor del paisaje
    ax.view_init(elev=34 - 6 * np.sin(t / 6), azim=-62 + 3.2 * t)
    superficie.set_alpha(0.95 * ease(t / 0.6))

    if 4.6 <= t < 9.0:
        a = ease((t - 4.6) / 0.4)
        etiqueta("arriba: mucho error", 0.5, 0.93, C2, alpha=a)
        etiqueta("abajo: acierta", 0.5, 0.07, C1, alpha=a)

    if t >= T_A0:
        p = bola(PRINCIPAL, T_A0, T_A1, t, ACCENT)
        if t >= T_A1:
            etiqueta("¡fondo del valle!", 0.5, 0.93, C3)
        else:
            etiqueta(f"paso {int(np.clip((t - T_A0) / (T_A1 - T_A0), 0, 1) * 45)}"
                     f"   error {f(*p):.2f}", 0.5, 0.93, FG, size=13)
    if t >= T_B0:
        bola(ATASCADA, T_B0, T_B1, t, C2)
        if T_B1 <= t < T_C0:
            etiqueta("atascada en un valle pequeño", 0.5, 0.07, C2, size=13)
    if t >= T_C0:
        finales = []
        for k, ruta in enumerate(VARIAS):
            color = "#FFFFFF"
            if t >= T_C1:  # al final: verde la mejor, rosa la que se atascó
                color = C3 if f(*ruta[-1]) < 0.6 else C2
            finales.append(bola(ruta, T_C0 + 0.15 * k, T_C1, t, color, ms=10))
        if t >= T_C1:
            etiqueta("¡se queda con la mejor!", 0.5, 0.07, C3, size=14)


if __name__ == "__main__":
    reel.render(draw, "16_montanas_3d")
