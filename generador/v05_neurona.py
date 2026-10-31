"""IA desde cero #2 · Una neurona artificial decide si vamos a la playa."""
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch

from base import Reel, ease, ACCENT, C1, C2, C3, MUTED, FG, SERIE_CERO

PANEL = "#161D2A"
ENTRADAS = [("¿Hace sol?", 6.1), ("¿Hace calor?", 3.9), ("¿Trabajas?", 1.7)]
PESOS = [3, 2, -5]
UMBRAL = 4
NEURONA = np.array([6.1, 3.9])
SALIDA = np.array([8.85, 3.9])

ESCENAS = [
    (0.0, 4.0, "Una neurona recibe datos: ¿hace sol? ¿calor? ¿trabajas?"),
    (4.0, 8.2, "Cada dato tiene un PESO: lo mucho que importa"),
    (8.2, 13.6, "Hoy hace sol y calor, y no trabajas: 3 + 2 + 0 = 5"),
    (13.6, 17.2, "5 supera el umbral de 4… ¡SÍ, a la playa!"),
    (17.2, 22.4, "!¿Y si trabajas? 3 + 2 − 5 = 0… NO hay playa"),
    (22.4, 27.0, "Aprender es ajustar esos pesos con muchos ejemplos"),
    (27.0, 31.5, "!Sigue a @hacerlointeligente: en el próximo, una red entera"),
]
VOZ = {
    "gancho": "Así toma una decisión una neurona artificial.",
    0: "Una neurona recibe datos. ¿Hace sol? ¿Hace calor? ¿Trabajas?",
    1: "Cada dato tiene un peso: lo mucho que le importa.",
    2: "Hoy hace sol y calor, y no trabajas. Tres, más dos, más cero: cinco.",
    3: "Cinco supera el umbral de cuatro. ¡Sí, a la playa!",
    4: "¿Y si trabajas? Tres, más dos, menos cinco: cero. No hay playa.",
    5: "Aprender es ajustar esos pesos con muchos ejemplos.",
    6: "Sigue a hacerlo inteligente. En el próximo, una red entera.",
}
EFECTOS = ([(0.4 + 0.5 * k, "pop") for k in range(3)] + [(1.9, "pop")]
           + [(4.4 + 0.6 * k, "whoosh") for k in range(3)]
           + [(9.0, "pop"), (10.4, "whoosh"), (14.0, "pop"), (17.8, "pop"), (18.6, "whoosh"),
              (19.8, "error")])

PORTADA = dict(titulo=["Así decide", "una neurona", "artificial"], amarilla=1, t=15.0, gesto="pulgar")

reel = Reel(2, "Así decide una\nneurona artificial", ESCENAS, 31.5, voz=VOZ, efectos=EFECTOS,
            serie=SERIE_CERO, musica={"bpm": 92},
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


def caja(x, y, w, h, color=PANEL, borde=C1, alpha=1.0, lw=2.2, z=4):
    return add(ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                           boxstyle="round,pad=0,rounding_size=0.25",
                                           fc=color, ec=borde, lw=lw, alpha=alpha, zorder=z)))


def texto(x, y, s, size=14, color=FG, alpha=1.0, **kw):
    kw.setdefault("ha", "center")
    kw.setdefault("va", "center")
    kw.setdefault("weight", "bold")
    return add(ax.text(x, y, s, size=size, color=color, alpha=alpha, zorder=8, **kw))


def valores_en(t):
    """Respuestas (1 = sí, 0 = no) a cada pregunta en el instante t (o None)."""
    if t < 8.2:
        return None
    if t < 17.8:
        return [1, 1, 0]
    return [1, 1, 1]


def pesos_en(t):
    if t < 22.8:
        return PESOS
    # "aprendiendo": los pesos tantean valores y se asientan
    rng = np.random.default_rng(int(t * 6))
    if t < 25.2:
        return [p + int(rng.integers(-2, 3)) for p in PESOS]
    return PESOS


def draw(t):
    limpiar()
    vals = valores_en(t)
    pesos = pesos_en(t)
    # ------------------------------------------------ conexiones con su peso
    for k, ((_txt, yy), w) in enumerate(zip(ENTRADAS, pesos)):
        a = ease((t - 4.4 - 0.6 * k) / 0.5)
        if a <= 0:
            continue
        p0 = np.array([3.05, yy])
        p1 = NEURONA + (p0 - NEURONA) / np.linalg.norm(p0 - NEURONA) * 0.95
        p = p0 + (p1 - p0) * a
        color = C3 if w > 0 else C2
        add(ax.plot([p0[0], p[0]], [p0[1], p[1]], color=color, lw=2 + 1.6 * abs(w),
                    alpha=0.85, solid_capstyle="round", zorder=2)[0])
        if a > 0.6:
            m = p0 + (p1 - p0) * 0.45
            caja(m[0], m[1] + 0.02, 0.95, 0.55, color="#0E1117", borde=color, lw=2, z=5)
            texto(m[0], m[1], f"×{w:+d}".replace("+", ""), size=14, color=color)
        # impulsos que viajan por la conexión cuando hay datos
        if vals is not None and vals[k]:
            for t0 in ((10.4,) if t < 17.8 else (18.6,)):
                f = (t - t0 - 0.12 * k) / 0.9
                if 0 < f < 1:
                    q = p0 + (p1 - p0) * f
                    add(ax.add_patch(Circle(q, 0.17, fc=ACCENT, ec="none", zorder=6)))

    # ------------------------------------------------ entradas
    for k, (txt, yy) in enumerate(ENTRADAS):
        a = ease((t - 0.4 - 0.5 * k) / 0.35)
        if a <= 0:
            continue
        caja(1.6, yy, 2.9 * a + 0.01, 1.2, alpha=a)
        texto(1.6, yy + 0.22, txt, size=13, alpha=a)
        if vals is None:
            texto(1.6, yy - 0.28, "·  ·  ·", size=12, color=MUTED, alpha=a)
        else:
            si = vals[k] == 1
            cambio = (k == 2 and 17.8 <= t < 18.3)
            texto(1.6, yy - 0.28, "SÍ  (1)" if si else "NO  (0)", size=13,
                  color=ACCENT if cambio else (C3 if si else MUTED))

    # ------------------------------------------------ neurona
    a = ease((t - 1.9) / 0.4)
    if a > 0:
        brillo = 0.0
        if vals is not None:
            suma = sum(v * w for v, w in zip(vals, pesos))
            t_suma = 11.5 if t < 17.8 else 19.6
            mostrar = t >= t_suma
            if mostrar:
                activa = suma > UMBRAL
                brillo = 0.6 + 0.4 * np.sin(2 * np.pi * 1.5 * t) if activa else 0.0
        if brillo > 0:
            add(ax.add_patch(Circle(NEURONA, 1.25, fc=C3, ec="none", alpha=0.15 * brillo,
                                    zorder=3)))
        add(ax.add_patch(Circle(NEURONA, 0.95 * a, fc=PANEL, ec=ACCENT, lw=3, zorder=4)))
        if vals is not None and t >= (11.5 if t < 17.8 else 19.6):
            texto(*NEURONA + [0, 0.18], f"{suma}", size=26, color=ACCENT)
            texto(*NEURONA + [0, -0.42], "suma", size=10, color=MUTED)
        else:
            texto(*NEURONA, "Σ", size=30, color=ACCENT, alpha=a)
        texto(NEURONA[0], NEURONA[1] - 1.45, f"umbral: {UMBRAL}", size=12, color=MUTED,
              alpha=a)

    # ------------------------------------------------ salida
    if a > 0:
        add(ax.plot([NEURONA[0] + 0.95, SALIDA[0] - 0.85], [NEURONA[1]] * 2, color=MUTED, lw=3,
                    zorder=2)[0])
        texto(SALIDA[0], SALIDA[1] + 1.15, "¿playa?", size=13, color=MUTED)
        decision = None
        if vals is not None:
            if 14.0 <= t < 17.8:
                decision = True
            elif t >= 19.8:
                decision = False
        color = MUTED if decision is None else (C3 if decision else C2)
        caja(SALIDA[0], SALIDA[1], 1.6, 1.3, borde=color, lw=3)
        texto(*SALIDA, "?" if decision is None else ("SÍ" if decision else "NO"),
              size=24 if decision is not None else 20, color=color)
    if 22.4 <= t < 27.0:
        texto(6.1, 7.4, "ajustando pesos…" if t < 25.2 else "¡pesos aprendidos!", size=14,
              color=ACCENT)


if __name__ == "__main__":
    reel.render(draw, "05_neurona")
