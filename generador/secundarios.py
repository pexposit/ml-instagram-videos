"""Personajes secundarios originales de @hacerlointeligente (bocetos).

- Paco, «el cuñado» (60 y pico años): entiende la IA siempre al revés; el robot le corrige.
- Profesor Voltio, «el científico loco»: lo explica todo con entusiasmo exagerado.

Ambos tienen la misma interfaz: dibujar(ax, t, cx, cy, s, boca=0..1, gesto=...).
Unidades del personaje: mide unas 2 unidades de alto (de -1 a 1) y `s` escala.
"""
import numpy as np
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, Polygon, Rectangle, Arc

TINTA = "#141821"


class _L:
    def __init__(self, ax, cx, cy, s):
        self.ax, self.cx, self.cy, self.s = ax, cx, cy, s

    def P(self, x, y):
        return self.cx + x * self.s, self.cy + y * self.s

    def lw(self, w):
        x0 = self.ax.transData.transform((0, 0))[0]
        x1 = self.ax.transData.transform((self.s, 0))[0]
        return w * abs(x1 - x0) * 72 / self.ax.figure.dpi / 130

    def caja(self, x, y, w, h, color, r=0.1, borde=2.0, **kw):
        x0, y0 = self.P(x - w / 2, y - h / 2)
        self.ax.add_patch(FancyBboxPatch(
            (x0, y0), w * self.s, h * self.s,
            boxstyle=f"round,pad=0,rounding_size={min(r, w / 2, h / 2) * self.s}",
            fc=color, ec=TINTA if borde else "none", lw=self.lw(borde), **kw))

    def elip(self, x, y, w, h, color, borde=2.0, ang=0, **kw):
        self.ax.add_patch(Ellipse(self.P(x, y), w * self.s, h * self.s, angle=ang, fc=color,
                                  ec=TINTA if borde else "none", lw=self.lw(borde), **kw))

    def circ(self, x, y, r, color, borde=2.0, **kw):
        self.ax.add_patch(Circle(self.P(x, y), r * self.s, fc=color,
                                 ec=TINTA if borde else "none", lw=self.lw(borde), **kw))

    def poli(self, pts, color, borde=2.0, **kw):
        self.ax.add_patch(Polygon([self.P(*p) for p in pts], closed=True, fc=color,
                                  ec=TINTA if borde else "none", lw=self.lw(borde),
                                  joinstyle="round", **kw))

    def linea(self, pts, color, w, **kw):
        xs, ys = zip(*[self.P(*p) for p in pts])
        self.ax.plot(xs, ys, color=color, lw=self.lw(w), solid_capstyle="round", **kw)

    def arco(self, x, y, w, h, t1, t2, color, lw):
        self.ax.add_patch(Arc(self.P(x, y), w * self.s, h * self.s, theta1=t1, theta2=t2,
                              color=color, lw=self.lw(lw), capstyle="round"))

    def texto(self, x, y, txt, color, size):
        self.ax.text(*self.P(x, y), txt, ha="center", va="center", color=color, weight="black",
                     size=size * self.s / 1.0)


def _ojos(L, y, sep, mira=0.0, parpado=1.0, grande=1.0):
    for sx in (-1, 1):
        L.elip(sx * sep, y, 0.17 * grande, 0.21 * grande * parpado, "#FFFFFF", borde=1.6)
        if parpado > 0.3:
            L.circ(sx * sep + 0.03 * mira, y - 0.01, 0.045 * grande, TINTA, borde=0)
            L.circ(sx * sep + 0.03 * mira + 0.015, y + 0.02, 0.014 * grande, "#FFFFFF", borde=0)


# ---------------------------------------------------------------------------- PACO
def paco(ax, t, cx, cy, s, boca=0.0, gesto="confuso"):
    """El cuñado, ya mayor: entradas y pelo canoso rizado a los lados, bigote gris, arrugas,
    gafas de leer en la punta de la nariz, papada y polo rojo."""
    PIEL, PIEL2, PELO, POLO, POLO2 = "#EDBB96", "#D3946B", "#B8BCC4", "#C62F3E", "#9E2331"
    ARRUGA = "#B9835F"
    L = _L(ax, cx, cy + 0.01 * s * np.sin(2 * np.pi * 0.7 * t), s)
    # cuerpo con algo de barriga
    L.caja(0, -0.8, 1.4, 0.78, POLO, r=0.36)
    L.poli([(-0.22, -0.42), (0, -0.62), (0.22, -0.42)], "#FFFFFF", borde=1.6)
    L.circ(0, -0.7, 0.025, "#FFFFFF", borde=0)
    L.circ(0, -0.8, 0.025, "#FFFFFF", borde=0)
    L.caja(0, -0.45, 0.26, 0.16, PIEL, r=0.06, borde=1.6)
    if gesto == "movil":
        L.caja(0.6, -0.55, 0.24, 0.42, POLO2, r=0.1)
        L.caja(0.67, -0.2, 0.2, 0.34, "#22262E", r=0.04)
        L.caja(0.67, -0.2, 0.15, 0.26, "#4CC9F0", r=0.02, borde=0)
        L.circ(0.6, -0.32, 0.09, PIEL)
    # cabeza (más ancha abajo: papada)
    for sx in (-1, 1):
        L.elip(sx * 0.48, 0.05, 0.17, 0.26, PIEL)
    L.elip(0, 0.08, 0.94, 1.02, PIEL)
    L.arco(0, -0.36, 0.42, 0.12, 200, 340, ARRUGA, 3)                      # papada
    # entradas: pelo canoso rizado solo a los lados y un poco detrás
    for sx in (-1, 1):
        for k in range(3):
            L.circ(sx * (0.42 - 0.03 * k), 0.38 - 0.12 * k, 0.1, PELO, borde=1.4)
    L.arco(0, 0.42, 0.4, 0.14, 25, 155, ARRUGA, 3)                          # arrugas frente
    L.arco(0, 0.36, 0.34, 0.1, 25, 155, ARRUGA, 3)
    # cejas grises (una levantada si está confuso)
    ceja_d = 0.08 if gesto == "confuso" else 0.0
    L.linea([(-0.3, 0.25), (-0.1, 0.27)], "#8D929B", 10)
    L.linea([(0.1, 0.27 + ceja_d), (0.3, 0.24 + ceja_d * 1.5)], "#8D929B", 10)
    parpado = 0.15 if (t % 3.1) < 0.12 else 0.85
    _ojos(L, 0.13, 0.19, mira=0.6 if gesto == "confuso" else 0.0, parpado=parpado)
    for sx in (-1, 1):                                                     # patas de gallo
        L.linea([(sx * 0.31, 0.16), (sx * 0.37, 0.19)], ARRUGA, 3)
        L.linea([(sx * 0.31, 0.12), (sx * 0.37, 0.11)], ARRUGA, 3)
    L.elip(0, -0.02, 0.19, 0.22, PIEL2, borde=1.6)                          # nariz
    # gafas de leer en la punta de la nariz
    for sx in (-1, 1):
        L.caja(sx * 0.13, -0.04, 0.2, 0.11, "none", r=0.04, borde=2.2)
    # bigote gris y boca
    L.poli([(-0.28, -0.13), (-0.05, -0.08), (0, -0.11), (0.05, -0.08), (0.28, -0.13),
            (0.21, -0.21), (0, -0.16), (-0.21, -0.21)], PELO, borde=1.4)
    ab = 0.03 + 0.12 * boca
    L.elip(0, -0.27, 0.2, ab, "#7A2533", borde=1.6)
    if gesto == "confuso":
        L.texto(0.64, 0.55, "?", "#FFD23F", 44)


# --------------------------------------------------------------- PROFESOR VOLTIO
def voltio(ax, t, cx, cy, s, boca=0.0, gesto="eureka"):
    """El científico loco: cabeza alargada y calva por arriba, barba pelirroja enorme y
    alborotada, lupa de relojero en un ojo (que lo hace gigante), pajarita, bata VERDE y
    guantes amarillos. Siempre hay alguna chispa eléctrica cerca."""
    PIEL, BARBA, BARBA2 = "#F0C6A4", "#D9622B", "#F08A3E"
    BATA, BATA2, GUANTE = "#5FBF8F", "#3E9A6E", "#FFD23F"
    L = _L(ax, cx, cy + 0.012 * s * np.sin(2 * np.pi * 1.2 * t), s)
    # bata verde
    L.caja(0, -0.82, 1.3, 0.78, BATA, r=0.32)
    L.poli([(-0.2, -0.42), (-0.05, -0.8), (-0.34, -0.62)], BATA2, borde=1.4)
    L.poli([(0.2, -0.42), (0.05, -0.8), (0.34, -0.62)], BATA2, borde=1.4)
    L.poli([(-0.16, -0.46), (0, -0.52), (0.16, -0.46), (0.16, -0.6), (0, -0.54),
            (-0.16, -0.6)], "#7B2CBF", borde=1.4)                           # pajarita
    L.circ(0, -0.53, 0.04, "#9D4EDD", borde=1.2)
    # cabeza alargada (calva arriba)
    for sx in (-1, 1):
        L.elip(sx * 0.42, 0.1, 0.15, 0.24, PIEL)
    L.elip(0, 0.18, 0.8, 1.15, PIEL)
    L.elip(-0.12, 0.6, 0.18, 0.08, "#FFFFFF", borde=0, alpha=0.5)            # brillo calva
    # mechones laterales disparados hacia fuera (pelirrojos)
    for sx in (-1, 1):
        for k, (dx, dy) in enumerate(((0.47, 0.35), (0.55, 0.25), (0.5, 0.45))):
            L.poli([(sx * 0.36, 0.3 + 0.04 * k), (sx * (dx + 0.08), dy + 0.08),
                    (sx * (dx + 0.02), dy - 0.02)], BARBA2, borde=1.2)
    # barba enorme y alborotada
    for k, a in enumerate(np.linspace(np.pi * 1.05, np.pi * 1.95, 9)):
        L.circ(0.36 * np.cos(a), -0.12 + 0.34 * np.sin(a), 0.14 + 0.02 * (k % 2),
               BARBA if k % 2 else BARBA2, borde=1.4)
    L.elip(0, -0.2, 0.5, 0.36, BARBA, borde=0)
    # cejas pelirrojas muy arqueadas
    L.arco(-0.17, 0.3, 0.22, 0.14, 20, 160, BARBA, 8)
    L.arco(0.17, 0.32, 0.22, 0.16, 20, 160, BARBA, 8)
    parpado = 0.15 if (t % 2.7) < 0.12 else 1.0
    # ojo izquierdo normal, ojo derecho tras la lupa de relojero (gigante)
    L.elip(-0.17, 0.18, 0.16, 0.2 * parpado, "#FFFFFF", borde=1.6)
    if parpado > 0.3:
        L.circ(-0.16, 0.17, 0.045, TINTA, borde=0)
    L.linea([(0.17, 0.33), (0.4, 0.42)], "#3A3F4B", 6)                       # cinta
    L.circ(0.17, 0.18, 0.17, "#3A3F4B", borde=1.6)
    L.circ(0.17, 0.18, 0.13, "#FFFFFF", borde=1.2)
    if parpado > 0.3:
        L.circ(0.18, 0.17, 0.08, TINTA, borde=0)
        L.circ(0.21, 0.21, 0.025, "#FFFFFF", borde=0)
    L.circ(0.12, 0.24, 0.04, "#FFFFFF", borde=0, alpha=0.6)
    L.elip(0.0, 0.02, 0.13, 0.17, "#E3A882", borde=1.6)                     # nariz
    # boca dentro de la barba: sonrisa enorme
    ab = 0.07 + 0.13 * boca
    L.poli([(-0.17, -0.12)] + [(0.17 * np.cos(a), -0.12 + ab * np.sin(a))
                              for a in np.linspace(np.pi, 2 * np.pi, 16)] + [(0.17, -0.12)],
           "#7A2533", borde=1.6)
    L.caja(0, -0.135, 0.2, 0.03, "#FFFFFF", r=0.01, borde=0)
    # brazo con una bombilla chisporroteando
    if gesto == "eureka":
        L.caja(0.62, -0.5, 0.22, 0.48, BATA, r=0.1)
        L.circ(0.66, 0.08, 0.15, "#FFF3B0", borde=1.6)
        L.caja(0.66, -0.12, 0.12, 0.1, "#9AA5B4", r=0.02, borde=1.4)
        brillo = 0.5 + 0.5 * np.sin(2 * np.pi * 3 * t)
        L.circ(0.66, 0.08, 0.26, "#FFD23F", borde=0, alpha=0.25 * brillo)
        L.circ(0.62, -0.22, 0.09, GUANTE)
        L.linea([(0.88, 0.3), (0.98, 0.42), (0.92, 0.44), (1.04, 0.58)], "#4CC9F0", 5)
        L.linea([(0.42, 0.34), (0.36, 0.46), (0.42, 0.47), (0.34, 0.6)], "#4CC9F0", 5)
