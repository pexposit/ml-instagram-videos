"""Personajes secundarios originales de @hacerlointeligente (bocetos).

- Paco, «el cuñado»: entiende la IA siempre al revés; el robot le corrige.
- Dra. Chispa, «la científica chiflada»: lo explica todo con entusiasmo exagerado.

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
    """El cuñado: pelo rizado castaño, bigote, polo rojo y gafas de sol en la cabeza."""
    PIEL, PIEL2, PELO, POLO, POLO2 = "#F1C19A", "#D99B72", "#6B3E26", "#D7263D", "#A61B2E"
    L = _L(ax, cx, cy + 0.01 * s * np.sin(2 * np.pi * 0.8 * t), s)
    # cuerpo (polo con cuello y botones)
    L.caja(0, -0.78, 1.25, 0.75, POLO, r=0.3)
    L.poli([(-0.22, -0.42), (0, -0.62), (0.22, -0.42)], "#FFFFFF", borde=1.6)
    L.circ(0, -0.7, 0.025, "#FFFFFF", borde=0)
    L.circ(0, -0.8, 0.025, "#FFFFFF", borde=0)
    L.caja(0, -0.45, 0.24, 0.16, PIEL, r=0.06, borde=1.6)                    # cuello
    # brazo con el móvil
    if gesto == "movil":
        L.caja(0.55, -0.55, 0.22, 0.42, POLO2, r=0.1)
        L.caja(0.62, -0.2, 0.2, 0.34, "#22262E", r=0.04)
        L.caja(0.62, -0.2, 0.15, 0.26, "#4CC9F0", r=0.02, borde=0)
        L.circ(0.55, -0.32, 0.09, PIEL)
    # cabeza
    for sx in (-1, 1):
        L.elip(sx * 0.47, 0.05, 0.16, 0.24, PIEL)                            # orejas
    L.elip(0, 0.08, 0.92, 1.0, PIEL)
    # pelo rizado
    for k, x in enumerate(np.linspace(-0.4, 0.4, 7)):
        L.circ(x, 0.5 + 0.05 * np.cos(k * 1.7), 0.13, PELO, borde=1.4)
    for x in (-0.44, 0.44):
        L.circ(x, 0.32, 0.1, PELO, borde=1.4)
    # gafas de sol subidas a la cabeza
    for sx in (-1, 1):
        L.caja(sx * 0.17, 0.5, 0.26, 0.13, "#1D1F26", r=0.05, borde=1.2)
    L.linea([(-0.04, 0.52), (0.04, 0.52)], "#1D1F26", 5)
    # cejas (una levantada si está confuso)
    ceja_d = 0.08 if gesto == "confuso" else 0.0
    L.linea([(-0.3, 0.25), (-0.1, 0.27)], PELO, 9)
    L.linea([(0.1, 0.27 + ceja_d), (0.3, 0.24 + ceja_d * 1.5)], PELO, 9)
    parpado = 0.15 if (t % 3.1) < 0.12 else 1.0
    _ojos(L, 0.13, 0.19, mira=0.6 if gesto == "confuso" else 0.0, parpado=parpado)
    L.elip(0, -0.02, 0.17, 0.2, PIEL2, borde=1.6)                            # nariz
    # bigote y boca
    L.poli([(-0.27, -0.13), (-0.05, -0.08), (0, -0.11), (0.05, -0.08), (0.27, -0.13),
            (0.2, -0.2), (0, -0.16), (-0.2, -0.2)], PELO, borde=1.4)
    ab = 0.03 + 0.12 * boca
    L.elip(0, -0.26, 0.2, ab, "#7A2533", borde=1.6)
    if gesto == "confuso":
        L.texto(0.62, 0.55, "?", "#FFD23F", 44)


# ---------------------------------------------------------------------- DRA. CHISPA
def chispa(ax, t, cx, cy, s, boca=0.0, gesto="eureka"):
    """La científica: melena morada con un mechón blanco, gafas de laboratorio en la frente,
    pecas, bata blanca y un matraz que burbujea."""
    PIEL, PELO, PELO2, BATA, CAMISA = "#C98B62", "#7B2CBF", "#9D4EDD", "#F4F6FA", "#2EC4B6"
    L = _L(ax, cx, cy + 0.012 * s * np.sin(2 * np.pi * 1.1 * t), s)
    # melena por detrás
    for k, a in enumerate(np.linspace(0, 2 * np.pi, 14, endpoint=False)):
        L.circ(0.5 * np.cos(a), 0.12 + 0.55 * np.sin(a), 0.2 + 0.03 * np.sin(3 * k), PELO2
               if k % 3 else PELO, borde=1.4)
    # bata y camiseta
    L.caja(0, -0.8, 1.3, 0.8, BATA, r=0.32)
    L.poli([(-0.2, -0.42), (0.2, -0.42), (0, -0.85)], CAMISA, borde=1.6)
    L.poli([(-0.2, -0.42), (-0.05, -0.75), (-0.32, -0.62)], "#DDE3EC", borde=1.4)   # solapas
    L.poli([(0.2, -0.42), (0.05, -0.75), (0.32, -0.62)], "#DDE3EC", borde=1.4)
    L.caja(-0.42, -0.9, 0.2, 0.14, "#DDE3EC", r=0.03, borde=1.2)                   # bolsillo
    L.linea([(-0.46, -0.86), (-0.46, -0.76)], "#F72585", 5)                       # bolígrafo
    L.caja(0, -0.45, 0.22, 0.16, PIEL, r=0.06, borde=1.6)
    # cara
    L.elip(0, 0.08, 0.86, 0.98, PIEL)
    for x, y in ((-0.2, 0.0), (-0.26, -0.04), (-0.15, -0.05), (0.2, 0.0), (0.26, -0.04),
                 (0.15, -0.05)):
        L.circ(x, y, 0.014, "#8A5A3C", borde=0)                                  # pecas
    # flequillo con mechón blanco
    for k, x in enumerate(np.linspace(-0.36, 0.36, 6)):
        L.circ(x, 0.5 - 0.03 * (k % 2), 0.13, "#FFFFFF" if k == 4 else PELO, borde=1.4)
    # gafas de laboratorio en la frente
    L.linea([(-0.44, 0.42), (0.44, 0.42)], "#3A3F4B", 7)
    for sx in (-1, 1):
        L.circ(sx * 0.17, 0.42, 0.13, "#FF9F1C", borde=1.6)
        L.circ(sx * 0.17, 0.42, 0.09, "#BDE8F5", borde=1.2)
        L.circ(sx * 0.17 - 0.03, 0.45, 0.025, "#FFFFFF", borde=0)
    # cejas y ojos grandes (entusiasmo)
    L.arco(-0.19, 0.24, 0.2, 0.1, 20, 160, "#4A1A6B", 6)
    L.arco(0.19, 0.24, 0.2, 0.1, 20, 160, "#4A1A6B", 6)
    parpado = 0.15 if (t % 2.9) < 0.12 else 1.0
    _ojos(L, 0.12, 0.19, parpado=parpado, grande=1.15)
    L.arco(0, 0.0, 0.1, 0.08, 200, 340, "#8A5A3C", 4)                             # nariz
    # boca: sonrisa enorme, abierta al hablar
    ab = 0.08 + 0.12 * boca
    L.poli([(-0.2, -0.17)] + [(0.2 * np.cos(a), -0.17 + ab * np.sin(a))
                             for a in np.linspace(np.pi, 2 * np.pi, 16)] + [(0.2, -0.17)],
           "#7A2533", borde=1.6)
    L.caja(0, -0.185, 0.24, 0.035, "#FFFFFF", r=0.01, borde=0)                     # dientes
    # brazo con matraz que burbujea
    if gesto == "eureka":
        L.caja(0.6, -0.48, 0.22, 0.5, BATA, r=0.1)
        L.poli([(0.56, 0.02), (0.68, 0.02), (0.68, -0.08), (0.82, -0.32), (0.42, -0.32),
                (0.56, -0.08)], "#E8F7FF", borde=1.6, alpha=0.95)
        L.poli([(0.48, -0.22), (0.76, -0.22), (0.82, -0.32), (0.42, -0.32)], "#7BE495",
               borde=0)
        for k in range(4):
            fase = (t * 0.8 + k * 0.27) % 1
            L.circ(0.62 + 0.05 * np.sin(k * 2 + t * 3), -0.1 + 0.45 * fase, 0.03 + 0.02 * k % 2,
                   "#7BE495", borde=1, alpha=1 - fase)
        L.circ(0.62, -0.3, 0.09, PIEL)
        L.texto(0.95, 0.35, "✦", "#FFD23F", 30)
        L.texto(0.3, 0.75, "✦", "#FFD23F", 20)
