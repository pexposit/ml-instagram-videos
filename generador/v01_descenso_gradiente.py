"""Reel #1 · Descenso del gradiente: así aprende una IA."""
import numpy as np

from base import Reel, ease, ACCENT, C1, C2, C3, MUTED, FG, GRID


def f(x):
    return 0.25 * (x - 1) ** 2 + 0.3


def df(x):
    return 0.5 * (x - 1)


def pasos(x0, lr, n):
    xs = [x0]
    for _ in range(n):
        xs.append(xs[-1] - lr * df(xs[-1]))
    return xs


BUENOS = pasos(-3.6, 0.9, 10)    # converge
MALOS = pasos(0.2, 4.8, 5)     # se pasa de largo y diverge
T_PASO = 0.65

ESCENAS = [
    (0.0, 3.2, "Esta curva es el ERROR de la IA"),
    (3.2, 6.4, "Arriba: se equivoca mucho. Abajo: acierta."),
    (6.4, 9.4, "La IA mira hacia dónde baja la pendiente…"),
    (9.4, 16.4, "…y da un paso cuesta abajo. Una y otra vez."),
    (16.4, 21.0, "!Pero si el paso es demasiado grande… se pasa de largo"),
    (21.0, 25.0, "DESCENSO DEL GRADIENTE: así se entrenan casi todas las IAs"),
    (25.0, 29.5, "!Guárdalo y sigue a @hacerlointeligente para el #2"),
]

VOZ = {
    "gancho": "Una IA no piensa. Hace esto, millones de veces.",
    0: "Esta curva es el error de la IA.",
    1: "Arriba, mucho error. Abajo, acierta.",
    3: "Y da un paso cuesta abajo. Y otro. Y otro. Una y otra vez.",
    5: "Esto es el descenso del gradiente: así aprenden casi todas las IAs.",
    6: "Guárdalo, y sigue a hacerlo inteligente para el número dos.",
}
EFECTOS = ([(9.4 + k * T_PASO, "pop") for k in range(len(BUENOS) - 1)]
           + [(16.4 + k * T_PASO, "error") for k in range(len(MALOS) - 1)]
           + [(21.0, "whoosh")])

reel = Reel(1, "Una IA no piensa.\nHace ESTO millones\nde veces", ESCENAS, 29.5,
            voz=VOZ, efectos=EFECTOS)
ax = reel.ax
xs = np.linspace(-4.2, 6.2, 400)
ax.plot(xs, f(xs), color=C1, lw=4, solid_capstyle="round")
ax.axhline(0, color=GRID, lw=1.5)
ax.set_xlim(-4.4, 6.4)
ax.set_ylim(-0.6, 7.6)
ax.text(-4.2, 7.3, "error", color=MUTED, size=13, va="top")
ax.text(6.2, -0.45, "parámetro del modelo", color=MUTED, size=13, ha="right")

estela, = ax.plot([], [], "o", color=ACCENT, alpha=0.6, ms=8)
bola, = ax.plot([], [], "o", color=ACCENT, ms=22, mec=FG, mew=2, zorder=5)
tangente, = ax.plot([], [], color=C2, lw=3, zorder=4)
flecha = ax.annotate("", xy=(0, 0), xytext=(0, 0),
                     arrowprops=dict(arrowstyle="-|>", color=C3, lw=3, mutation_scale=28))
contador = ax.text(6.2, 7.3, "", color=FG, size=15, weight="bold", ha="right", va="top")


def posicion(trayectoria, tt):
    """Posición de la bola tras tt segundos recorriendo la trayectoria."""
    k = min(int(tt // T_PASO), len(trayectoria) - 2)
    a = ease((tt - k * T_PASO) / (T_PASO * 0.8))
    x0, x1 = trayectoria[k], trayectoria[k + 1]
    x = x0 + (x1 - x0) * a
    # salto en arco: se ve claramente cada "paso"
    y = f(x0) + (f(x1) - f(x0)) * a + 0.25 * abs(x1 - x0) * 4 * a * (1 - a)
    hechos = min(int(tt // T_PASO) + (1 if a >= 1 else 0), len(trayectoria) - 1)
    return x, y, hechos


def draw(t):
    tangente.set_data([], [])
    flecha.set_visible(False)
    contador.set_text("")
    if t < 9.4:
        x = BUENOS[0]
        bola.set_data([x], [f(x)])
        estela.set_data([], [])
        if t >= 6.4:
            a = ease((t - 6.4) / 0.8)
            dx = 1.3 * a
            tangente.set_data([x - dx, x + dx], [f(x) - df(x) * dx, f(x) + df(x) * dx])
            if t >= 7.4:
                flecha.set_visible(True)
                # flecha "cuesta abajo", un poco por debajo de la tangente
                flecha.xy = (x + 1.6, f(x) + df(x) * 1.6 - 0.7)
                flecha.set_position((x + 0.3, f(x) + df(x) * 0.3 - 0.7))
    elif t < 16.4:
        x, y, hechos = posicion(BUENOS, t - 9.4)
        bola.set_data([x], [y])
        estela.set_data(BUENOS[:hechos + 1], [f(v) for v in BUENOS[:hechos + 1]])
        contador.set_text(f"paso {hechos}   error {y:.2f}")
    elif t < 21.0:
        x, y, hechos = posicion(MALOS, t - 16.4)
        bola.set_data([x], [y])
        estela.set_data(MALOS[:hechos + 1], [f(v) for v in MALOS[:hechos + 1]])
        contador.set_text(f"paso {hechos}   error {y:.2f}")
        contador.set_color(ACCENT)
    else:
        x = BUENOS[-1]
        bola.set_data([x], [f(x)])
        estela.set_data(BUENOS, [f(v) for v in BUENOS])
        contador.set_color(FG)
        contador.set_text("¡mínimo encontrado!")


if __name__ == "__main__":
    reel.render(draw, "01_descenso_gradiente", portada_t=12.0)
