"""IA desde cero #14 · El truco de la tercera dimensión (el "truco del núcleo" de las SVM)."""
import numpy as np

from base import Reel, ease, ACCENT, C1, C2, C3, FG, SERIE_CERO

rng = np.random.default_rng(17)
ang_d, r_d = rng.uniform(0, 2 * np.pi, 40), np.sqrt(rng.uniform(0, 0.8, 40))
DENTRO = np.c_[r_d * np.cos(ang_d), r_d * np.sin(ang_d)]                 # azules, en el centro
ang_f, r_f = rng.uniform(0, 2 * np.pi, 64), rng.uniform(1.6, 2.2, 64)
FUERA = np.c_[r_f * np.cos(ang_f), r_f * np.sin(ang_f)]                  # rosas, alrededor
K = 0.55                                                                  # altura = K·distancia²
CORTE = K * 1.25 ** 2                                                     # altura del plano

T_SUBE0, T_SUBE1 = 9.2, 12.2
T_PLANO = 13.6
T_ARRIBA0, T_ARRIBA1 = 18.8, 20.8

ESCENAS = [  # "!" = habla el robot (subtítulo amarillo); el resto, la narradora
    (0.0, 4.4, "Puntos azules en el centro, rosas alrededor. Hay que separarlos"),
    (4.4, 8.8, "Con una línea recta… es imposible"),
    (8.8, 13.4, "!¡Truco! Les doy altura: cuanto más lejos del centro, más arriba", "explica"),
    (13.4, 18.6, "Ahora un simple plano los separa"),
    (18.6, 23.6, "Y visto desde arriba, el plano dibuja… ¡un círculo perfecto!"),
    (23.6, 28.0, "Es el «truco del núcleo»: subir de dimensión para separar lo inseparable"),
    (28.0, 32.5, "!¡Sígueme! En el próximo, más magia en 3D"),
]
VOZ = {
    "gancho": "¿Separar esto con una línea? ¡Imposible… en 2D!",
    0: "Puntos azules en el centro. Rosas, alrededor. Hay que separarlos.",
    2: "¡Truco! Les doy altura: cuanto más lejos del centro, más arriba.",
    4: "Y visto desde arriba, el plano dibuja… ¡un círculo perfecto!",
    5: "Es el truco del núcleo: subir de dimensión para separar lo inseparable.",
}
EFECTOS = ([(0.4, "pop"), (4.8, "whoosh"), (6.0, "error"), (7.2, "error"),
            (T_SUBE0, "whoosh"), (T_PLANO, "pop"), (T_ARRIBA0, "whoosh"), (T_ARRIBA1, "pop")])
PORTADA = dict(titulo=["El truco", "de la tercera", "dimensión"], amarilla=1, t=16.5,
               gesto="explica")

reel = Reel(14, "El truco de la\ntercera dimensión", ESCENAS, 32.5, voz=VOZ, efectos=EFECTOS,
            serie=SERIE_CERO, musica={"bpm": 98}, portada=PORTADA, tres_d=True)
ax = reel.ax
ax.computed_zorder = False
ax.set_xlim(-2.3, 2.3)
ax.set_ylim(-2.3, 2.3)
ax.set_zlim(0, 2.8)

# suelo con cuadrícula (para que se note la profundidad)
for v in np.linspace(-2.2, 2.2, 9):
    ax.plot([v, v], [-2.2, 2.2], [0, 0], color="#253044", lw=0.8, zorder=0)
    ax.plot([-2.2, 2.2], [v, v], [0, 0], color="#253044", lw=0.8, zorder=0)
puntos_d = ax.scatter(DENTRO[:, 0], DENTRO[:, 1], 0, s=60, color=C1, edgecolors=FG,
                      linewidths=0.8, depthshade=False, zorder=3)
puntos_f = ax.scatter(FUERA[:, 0], FUERA[:, 1], 0, s=60, color=C2, edgecolors=FG,
                      linewidths=0.8, depthshade=False, zorder=7)
PX, PY = np.meshgrid(np.linspace(-2.3, 2.3, 2), np.linspace(-2.3, 2.3, 2))
plano = ax.plot_surface(PX, PY, np.full_like(PX, CORTE), color=ACCENT, alpha=0.0,
                        linewidth=0, zorder=5, shade=False)

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


def camara(t):
    """Desde arriba (2D) → inclinada (3D) → otra vez desde arriba → girando."""
    if t < T_SUBE0:
        return 89.9, -90
    if t < T_ARRIBA0:
        a = ease((t - T_SUBE0) / 2.4)
        return 89.9 - 70 * a, -90 + 40 * a + 4 * max(0, t - T_SUBE0 - 2.4)
    if t < 23.6:
        a = ease((t - T_ARRIBA0) / (T_ARRIBA1 - T_ARRIBA0))
        azim_ini = -50 + 4 * (T_ARRIBA0 - T_SUBE0 - 2.4)
        return 19.9 + 70 * a, azim_ini + (-90 - azim_ini) * a
    a = ease((t - 23.6) / 1.5)
    return 89.9 - 62 * a, -90 + 10 * (t - 23.6)


def draw(t):
    limpiar()
    elev, azim = camara(t)
    ax.view_init(elev=elev, azim=azim)

    sube = ease((t - T_SUBE0) / (T_SUBE1 - T_SUBE0))
    zd = K * (DENTRO ** 2).sum(1) * sube
    zf = K * (FUERA ** 2).sum(1) * sube
    puntos_d._offsets3d = (DENTRO[:, 0], DENTRO[:, 1], zd)
    puntos_f._offsets3d = (FUERA[:, 0], FUERA[:, 1], zf)
    aparece = ease(t / 0.5)
    puntos_d.set_alpha(aparece)
    puntos_f.set_alpha(aparece)

    # intentos de separar con una recta (fallan)
    if 4.8 <= t < 8.8:
        k = min(int((t - 4.8) / 1.2), 2)
        ang = np.radians([20, 80, 140][k])
        d = np.array([np.cos(ang), np.sin(ang)]) * 2.4
        off = np.array([-np.sin(ang), np.cos(ang)]) * [0.3, -0.5, 0.9][k]
        add(ax.plot([off[0] - d[0], off[0] + d[0]], [off[1] - d[1], off[1] + d[1]], [0, 0],
                    color=ACCENT, lw=3, zorder=9)[0])
        if (t - 4.8) % 1.2 > 0.5:
            etiqueta("✗ no los separa", 0.5, 0.08, C2)

    # el plano que los separa
    if t >= T_PLANO:
        plano.set_alpha(0.35 * ease((t - T_PLANO) / 0.6))
    else:
        plano.set_alpha(0.0)
    if T_PLANO + 0.6 <= t < T_ARRIBA0:
        etiqueta("un plano los separa", 0.5, 0.92, ACCENT)

    # el círculo que dibuja el plano visto desde arriba
    if t >= T_ARRIBA1 - 0.3:
        a = ease((t - T_ARRIBA1 + 0.3) / 0.5)
        th = np.linspace(0, 2 * np.pi * a, 120)
        add(ax.plot(1.25 * np.cos(th), 1.25 * np.sin(th), np.full_like(th, CORTE + 0.01),
                    color=ACCENT, lw=4, zorder=8)[0])
        if t < 23.6:
            etiqueta("¡un círculo!", 0.5, 0.92, ACCENT, size=17)
    if t >= 23.8:
        etiqueta("truco del núcleo", 0.5, 0.92, C3, alpha=ease((t - 23.8) / 0.4))


if __name__ == "__main__":
    reel.render(draw, "17_truco_3d")
