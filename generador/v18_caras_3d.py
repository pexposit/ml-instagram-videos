"""IA desde cero #15 · Cómo te reconoce la cara el móvil (huella facial en 3D)."""
import numpy as np

from base import Reel, ease, ACCENT, C1, C2, C3, MUTED, FG, SERIE_CERO


def cara():
    """Una cara hecha de puntos en 3D (contorno, cejas, ojos, nariz y boca)."""
    pts = []
    th = np.linspace(0, 2 * np.pi, 46, endpoint=False)
    pts += [(0.8 * np.cos(a), 0.15 + 1.05 * np.sin(a), 0.25 * np.cos(a) ** 2) for a in th]
    for sx in (-1, 1):
        a = np.linspace(0, 2 * np.pi, 10, endpoint=False)
        pts += [(sx * 0.32 + 0.12 * np.cos(b), 0.38 + 0.07 * np.sin(b), 0.45) for b in a]
        pts += [(sx * (0.2 + 0.25 * k / 5), 0.6 + 0.04 * np.sin(np.pi * k / 5), 0.45)
                for k in range(6)]
    pts += [(0.0, 0.3 - 0.08 * k, 0.5 + 0.06 * k) for k in range(6)]
    pts += [(x, -0.4 - 0.12 * (1 - (x / 0.38) ** 2), 0.45) for x in np.linspace(-0.38, 0.38, 11)]
    return np.array(pts)


CARA = cara()
TU = np.array([0.7, 0.6, 0.9])                      # donde cae tu "huella"
rng = np.random.default_rng(18)
TUS_FOTOS = TU + rng.normal(0, 0.16, (8, 3))
OTROS = {C1: np.array([-1.2, 0.6, -0.6]), C3: np.array([0.6, -1.3, -0.2]),
         C2: np.array([-0.7, -0.9, 1.1])}
OTRAS = {c: p + rng.normal(0, 0.18, (7, 3)) for c, p in OTROS.items()}
RADIO = 0.55
INTENTO_TU = TU + np.array([0.12, -0.1, 0.08])
INTENTO_OTRO = OTROS[C2] + np.array([0.15, 0.1, -0.1])

T_NUM, T_JUNTA0, T_JUNTA1 = 2.4, 4.8, 6.0
T_OTROS, T_FOTOS, T_BURBUJA = 6.4, 9.2, 11.6
T_IN0, T_IN1, T_OUT0, T_OUT1 = 14.0, 15.4, 18.4, 19.8

ESCENAS = [  # "!" = habla el robot (subtítulo amarillo); el resto, la narradora
    (0.0, 4.4, "El móvil convierte tu cara en números: tu «huella facial»"),
    (4.4, 9.0, "Cada cara es un punto en un espacio: las parecidas, cerca"),
    (9.0, 13.6, "P:¿Y si me pongo gafas? A que no me reconoce"),
    (13.6, 18.0, "!¡Intento desbloquear… dentro de la burbuja: eres tú!", "pulgar"),
    (18.0, 23.0, "Otra persona cae lejos de tu burbuja: el móvil no se abre"),
    (23.0, 27.6, "V:¡En la realidad son cientos de números! La idea es la misma"),
    (27.6, 32.0, "!¡Sígueme para más IA en 3D!"),
]
VOZ = {
    "gancho": "¡Sé que eres tú… por tus números!",
    0: "El móvil convierte tu cara en números: tu huella facial.",
    1: "Cada cara es un punto en un espacio. Las parecidas, cerca.",
    3: "¡Intento desbloquear… dentro de la burbuja: eres tú!",
}
EFECTOS = ([(0.4, "pop"), (T_NUM, "pop"), (T_JUNTA0, "whoosh"), (T_OTROS, "pop"),
            (T_FOTOS, "pop"), (T_BURBUJA, "whoosh"), (T_IN0, "whoosh"), (T_IN1 + 0.2, "pop"),
            (T_OUT0, "whoosh"), (T_OUT1 + 0.2, "error")])
PORTADA = dict(titulo=["Cómo te reconoce", "la cara", "el móvil"], amarilla=1, t=16.5,
               gesto="pulgar")

TEASER = {'t': 15.9, 'texto': 'Así sabe tu móvil que eres tú', 'pregunta': '◀◀  ¿Cómo lo sabe?', 'y': 0.36}

reel = Reel(15, "Cómo te reconoce\nla cara el móvil", ESCENAS, 32.0, voz=VOZ, efectos=EFECTOS,
            serie=SERIE_CERO, musica={"bpm": 96}, portada=PORTADA, tres_d=True,
            teaser=TEASER, retratos=True)
ax = reel.ax
ax.computed_zorder = False
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_zlim(-1.6, 2.0)
ax.set_box_aspect((1, 1, 0.9), zoom=1.75)   # más cerca: puntos más grandes y visibles

artistas = []


def add(a):
    artistas.append(a)
    return a


def limpiar():
    while artistas:
        artistas.pop().remove()


def etiqueta(texto, x, y, color=FG, size=15, alpha=1.0):
    add(ax.text2D(x, y, texto, transform=ax.transAxes, ha="center", va="center", size=size,
                  weight="black", color=color, alpha=alpha, zorder=12))


def esfera(c, r, color, alpha):
    u, v = np.meshgrid(np.linspace(0, 2 * np.pi, 18), np.linspace(0, np.pi, 10))
    add(ax.plot_wireframe(c[0] + r * np.cos(u) * np.sin(v), c[1] + r * np.sin(u) * np.sin(v),
                          c[2] + r * np.cos(v), color=color, lw=0.8, alpha=alpha, zorder=4))


def ejes(alpha):
    for d, nombre in zip(np.eye(3) * 1.9, ("nº 1", "nº 2", "nº 3")):
        add(ax.plot([0, d[0]], [0, d[1]], [0, d[2]], color=MUTED, lw=1.2, alpha=alpha,
                    zorder=1)[0])
        add(ax.text(*(d * 1.08), nombre, color=MUTED, size=10, alpha=alpha, zorder=2))


def vuelo(p0, p1, t, t0, t1):
    a = ease((t - t0) / (t1 - t0))
    return p0 + (p1 - p0) * a + np.array([0, 0, 0.6]) * np.sin(np.pi * a)


def draw(t):
    limpiar()
    if t < T_JUNTA0:
        ax.view_init(elev=8, azim=-90 + 28 * np.sin(t * 0.9))     # la cara gira a un lado y otro
    else:
        ax.view_init(elev=22, azim=-60 + 4.5 * (t - T_JUNTA0))

    # ------------------------------------------------ la cara de puntos → un solo punto
    if t < T_JUNTA1:
        a = ease((t - T_JUNTA0) / (T_JUNTA1 - T_JUNTA0))
        pts = CARA * (1 - a) + TU * a
        # la cara se ve "de frente" girando sobre el eje vertical: x, z (profundidad), y
        add(ax.scatter(pts[:, 0], pts[:, 2], pts[:, 1], s=40 * (1 - 0.5 * a), color=ACCENT,
                       edgecolors="none", depthshade=True, alpha=ease(t / 0.5), zorder=6))
        if T_NUM <= t < T_JUNTA0 + 0.4:
            etiqueta("tu huella: (0,82 · −0,31 · 0,57 · …)", 0.5, 0.08, ACCENT, size=14,
                     alpha=ease((t - T_NUM) / 0.4))
        return

    ejes(ease((t - T_JUNTA1) / 0.5))
    # tu primer punto (el de la cara)
    add(ax.scatter(*TU, s=200, color=ACCENT, edgecolors=FG, linewidths=1.2, depthshade=False,
                   zorder=8))
    # otras personas
    for k, (color, nube) in enumerate(OTRAS.items()):
        a = ease((t - T_OTROS - 0.3 * k) / 0.4)
        if a > 0:
            add(ax.scatter(nube[:, 0], nube[:, 1], nube[:, 2], s=120 * a, color=color,
                           edgecolors=FG, linewidths=0.6, depthshade=False, zorder=7))
    if T_OTROS + 0.6 <= t < T_FOTOS:
        etiqueta("cada color: una persona distinta", 0.5, 0.08, FG, size=13)
    # tus otras fotos
    if t >= T_FOTOS:
        n = int(np.clip((t - T_FOTOS) / 0.25, 0, len(TUS_FOTOS)))
        if n:
            add(ax.scatter(TUS_FOTOS[:n, 0], TUS_FOTOS[:n, 1], TUS_FOTOS[:n, 2], s=140,
                           color=ACCENT, edgecolors=FG, linewidths=0.8, depthshade=False,
                           zorder=8))
    if t >= T_BURBUJA:
        esfera(TU, RADIO, ACCENT, 0.55 * ease((t - T_BURBUJA) / 0.5))
        if t < T_IN0:
            etiqueta("tu burbuja", 0.5, 0.92, ACCENT)

    # ------------------------------------------------ intento de desbloqueo: tú
    if t >= T_IN0:
        p = vuelo(np.array([0.0, 0.0, -1.4]), INTENTO_TU, t, T_IN0, T_IN1)
        add(ax.scatter(*p, s=320, color="#FFFFFF", edgecolors=ACCENT, linewidths=3,
                       depthshade=False, zorder=9))
        if T_IN1 + 0.2 <= t < T_OUT0:
            etiqueta("✓ ¡Desbloqueado!", 0.5, 0.92, C3, size=18)
    # ------------------------------------------------ intento: otra persona
    if t >= T_OUT0:
        p = vuelo(np.array([0.0, 0.0, -1.4]), INTENTO_OTRO, t, T_OUT0, T_OUT1)
        add(ax.scatter(*p, s=320, color="#FFFFFF", edgecolors=C2, linewidths=3,
                       depthshade=False, zorder=9))
        if t >= T_OUT1 + 0.2:
            d = np.linalg.norm(INTENTO_OTRO - TU)
            add(ax.plot(*zip(INTENTO_OTRO, TU), color=C2, lw=2, ls="--", zorder=6)[0])
            if t < 23.0:
                etiqueta(f"✗ Muy lejos de tu burbuja", 0.5, 0.92, C2, size=17)
    if t >= 23.2:
        etiqueta("en la realidad: cientos de números", 0.5, 0.92, FG, size=14,
                 alpha=ease((t - 23.2) / 0.4))


if __name__ == "__main__":
    reel.render(draw, "18_caras_3d")
