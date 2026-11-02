"""IA desde cero #12 · Cómo sabe tu correo que es spam (filtro bayesiano, simplificado)."""
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

from base import Reel, ease, ACCENT, C1, C2, C3, MUTED, FG, SERIE_CERO

PANEL = "#161D2A"
# (palabra, sospecha que suma). Lo aprendió contando en qué correos sale cada palabra.
CORREO1 = [("¡¡ENHORABUENA!!", 18), ("Has", 0), ("GANADO", 22), ("un", 0), ("PREMIO", 25),
           ("GRATIS.", 28), ("Haz", 2), ("clic", 15), ("aquí", 6)]
CORREO2 = [("Hola,", -8), ("¿quedamos", -12), ("mañana", -6), ("para", 0), ("estudiar", -14),
           ("el", 0), ("examen?", -10)]
UMBRAL = 60

T_LEE1, T_PASO1 = 4.6, 0.9
T_SPAM = T_LEE1 + len(CORREO1) * T_PASO1 + 0.3       # ≈ 13.0
T_LEE2, T_PASO2 = 17.9, 0.45
T_OK = T_LEE2 + len(CORREO2) * T_PASO2 + 0.3

ESCENAS = [  # "!" = habla el robot (subtítulo amarillo); el resto, la narradora
    (0.0, 4.4, "Llega un correo. El filtro lo lee palabra a palabra"),
    (4.4, 8.8, "Cada palabra suma o resta SOSPECHA, según lo que aprendió"),
    (8.8, 13.0, "!¿«GRATIS»? ¿«PREMIO»? ¡A mí no me engañas!", "piensa"),
    (13.0, 17.6, "Pasa el límite… ¡directo a la carpeta de spam!"),
    (17.6, 22.6, "Otro correo: «¿quedamos mañana?». Poca sospecha: a tu bandeja"),
    (22.6, 27.2, "Aprendió contando palabras en millones de correos marcados como spam"),
    (27.2, 31.8, "!¡Sígueme! Y nunca hagas clic en premios gratis"),
]
VOZ = {
    "gancho": "¿Cómo sé que un correo es spam? ¡Te lo enseño!",
    1: "Cada palabra suma o resta sospecha, según lo que aprendió.",
    2: "¿Gratis? ¿Premio? ¡A mí no me engañas!",
    3: "Pasa el límite… ¡Directo a la carpeta de spam!",
    4: "Otro correo: ¿quedamos mañana? Poca sospecha: a tu bandeja de entrada.",
    5: "Aprendió contando palabras en millones de correos marcados como spam.",
    6: "¡Sígueme! Y nunca hagas clic en premios gratis.",
}
EFECTOS = ([(0.4, "whoosh")] + [(T_LEE1 + k * T_PASO1, "pop") for k in range(len(CORREO1))]
           + [(T_SPAM, "error"), (T_LEE2 - 0.4, "whoosh")]
           + [(T_LEE2 + k * T_PASO2, "pop") for k in range(len(CORREO2))] + [(T_OK, "pop")])
PORTADA = dict(titulo=["Cómo sabe", "tu correo", "que es spam"], amarilla=2, t=12.6,
               gesto="piensa")

reel = Reel(12, "Cómo sabe tu correo\nque es spam", ESCENAS, 31.8, voz=VOZ, efectos=EFECTOS,
            serie=SERIE_CERO, musica={"bpm": 100}, portada=PORTADA)
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


def correo(t, palabras, t_lee, paso, asunto, entra):
    """Dibuja el correo resaltando cada palabra al leerla; devuelve la sospecha acumulada."""
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    if not hasattr(reel.fig.canvas, "get_renderer"):
        FigureCanvasAgg(reel.fig)
    a = ease((t - entra) / 0.4)
    add(ax.add_patch(FancyBboxPatch((0.3, 4.2), 9.4, 3.3,
                                    boxstyle="round,pad=0,rounding_size=0.3",
                                    fc=PANEL, ec=C1, lw=2.2, alpha=a, zorder=3)))
    add(ax.text(0.65, 7.2, "✉  " + asunto, size=12, weight="bold", color=MUTED, va="top",
                alpha=a, zorder=6))
    r = reel.fig.canvas.get_renderer()
    inv = ax.transData.inverted()
    x, y = 0.7, 6.55
    sospecha = 0
    for k, (pal, peso) in enumerate(palabras):
        leida = t >= t_lee + k * paso
        actual = t_lee + k * paso <= t < t_lee + (k + 1) * paso
        color = FG
        if leida:
            color = C2 if peso > 10 else (C3 if peso < -5 else FG)
            sospecha += peso
        txt = add(ax.text(x, y, pal, size=17, weight="black", color=color, va="top", alpha=a,
                          zorder=6))
        bb = txt.get_window_extent(renderer=r)
        (a0, b0), (a1, b1) = inv.transform([[bb.x0, bb.y0], [bb.x1, bb.y1]])
        if x + (a1 - a0) > 9.3 and x > 0.7:
            x, y = 0.7, y - 0.75
            txt.set_position((x, y))
        if actual:
            add(ax.add_patch(Rectangle((x - 0.08, y - 0.62), (a1 - a0) + 0.16, 0.66, fc="none",
                                       ec=ACCENT, lw=2.5, zorder=7)))
            if peso:
                add(ax.text(x + (a1 - a0) / 2, y + 0.25, f"{peso:+d}", ha="center",
                            va="bottom", size=13, weight="black",
                            color=C2 if peso > 0 else C3, zorder=8))
        x += (a1 - a0) + 0.2
    return sospecha


def medidor(t, sospecha, aparece):
    a = ease((t - aparece) / 0.4)
    x0, x1, y = 0.7, 9.3, 2.9
    add(ax.text(x0, y + 0.7, "sospecha de spam", size=13, weight="bold", color=MUTED,
                alpha=a, zorder=6))
    add(ax.add_patch(FancyBboxPatch((x0, y - 0.3), x1 - x0, 0.6,
                                    boxstyle="round,pad=0,rounding_size=0.3",
                                    fc="#0B0F16", ec=MUTED, lw=1.5, alpha=a, zorder=4)))
    f = np.clip((sospecha + 50) / 160, 0.02, 1)
    color = C2 if sospecha >= UMBRAL else (ACCENT if sospecha > 20 else C3)
    add(ax.add_patch(FancyBboxPatch((x0, y - 0.3), (x1 - x0) * f, 0.6,
                                    boxstyle="round,pad=0,rounding_size=0.3",
                                    fc=color, ec="none", alpha=a, zorder=5)))
    xu = x0 + (x1 - x0) * (UMBRAL + 50) / 160
    add(ax.plot([xu, xu], [y - 0.55, y + 0.55], color=FG, lw=2.5, ls="--", alpha=a,
                zorder=6)[0])
    add(ax.text(xu, y - 0.85, "límite", ha="center", size=11, weight="bold", color=FG,
                alpha=a, zorder=6))


def sello(texto, color, t0, t):
    c = ease((t - t0) / 0.25)
    add(ax.text(5.0, 1.15, texto, ha="center", va="center", size=24 + 10 * (1 - c),
                weight="black", color=color, alpha=c, zorder=9,
                bbox=dict(boxstyle="round,pad=0.25", fc="#0E1117", ec=color, lw=3, alpha=c)))


def draw(t):
    limpiar()
    if t < T_LEE2 - 0.6:
        s = correo(t, CORREO1, T_LEE1, T_PASO1, "De: premios-ya@ofertas.xyz", 0.3)
        if t >= 4.4:
            medidor(t, s, 4.4)
        if t >= T_SPAM:
            sello("SPAM 🗑".replace(" 🗑", "  →  carpeta de spam"), C2, T_SPAM, t)
    elif t < 22.6:
        s = correo(t, CORREO2, T_LEE2, T_PASO2, "De: Lucía (clase de mates)", T_LEE2 - 0.6)
        medidor(t, s, T_LEE2 - 0.6)
        if t >= T_OK:
            sello("✓ a tu bandeja de entrada", C3, T_OK, t)
    else:
        # lo que aprendió: en cuántos correos de cada tipo aparece cada palabra
        a = ease((t - 22.7) / 0.4)
        add(ax.text(5.0, 7.3, "lo que aprendió contando palabras", ha="center", va="center",
                    size=14, weight="bold", color=MUTED, alpha=a, zorder=6))
        add(ax.text(4.5, 6.55, "en spam", ha="center", size=12, weight="black", color=C2,
                    alpha=a, zorder=6))
        add(ax.text(6.5, 6.55, "en normales", ha="center", size=12, weight="black", color=C3,
                    alpha=a, zorder=6))
        filas = [("GRATIS", "9.120", "12", "+28"), ("PREMIO", "7.480", "30", "+25"),
                 ("quedamos", "15", "6.200", "−12"), ("examen", "3", "4.800", "−10")]
        for k, (pal, sp, no, peso) in enumerate(filas):
            b = ease((t - 23.0 - 0.45 * k) / 0.3)
            y = 5.7 - k * 1.0
            add(ax.text(2.6, y, pal, ha="right", va="center", size=16, weight="black",
                        color=FG, alpha=b, zorder=6))
            add(ax.text(4.5, y, sp, ha="center", va="center", size=16, weight="bold",
                        color=C2, alpha=b, zorder=6))
            add(ax.text(6.5, y, no, ha="center", va="center", size=16, weight="bold",
                        color=C3, alpha=b, zorder=6))
            add(ax.text(8.8, y, peso, ha="center", va="center", size=16, weight="black",
                        color=C2 if peso.startswith("+") else C3, alpha=b, zorder=6))
        add(ax.text(8.8, 6.55, "sospecha", ha="center", size=12, weight="black",
                    color=ACCENT, alpha=a, zorder=6))


if __name__ == "__main__":
    reel.render(draw, "15_spam")
