"""Reel #2 · K-means: la IA encuentra grupos sin que nadie le diga nada."""
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.colors import to_rgba

from base import Reel, ease, ACCENT, C1, C2, C3, MUTED, FG

rng = np.random.default_rng(7)
CENTROS_REALES = np.array([[-2.2, 1.6], [2.3, 1.9], [0.2, -2.0]])
X = np.vstack([c + rng.normal(0, 0.75, (30, 2)) for c in CENTROS_REALES])
COLORES = np.array([to_rgba(c) for c in (C1, C2, C3)])
GRIS = np.array(to_rgba(MUTED))

# Capitanes iniciales mal colocados para que el algoritmo se note (converge en 3 vueltas)
historia = [np.array([[-4.0, 3.5], [-3.5, -3.0], [1.0, -3.8]])]
asignaciones = []
for _ in range(4):
    c = historia[-1]
    a = np.argmin(((X[:, None, :] - c[None]) ** 2).sum(-1), axis=1)
    asignaciones.append(a)
    historia.append(np.array([X[a == k].mean(0) if (a == k).any() else c[k] for k in range(3)]))

T_ITER = 3.0
T0_ITER = 6.4
ESCENAS = [
    (0.0, 3.2, "Tienes datos… pero nadie te dice qué son"),
    (3.2, 6.4, "!¡Pongo 3 capitanes al azar! Ahí, ahí y ahí."),
]
for i in range(4):
    t = T0_ITER + i * T_ITER
    ESCENAS += [(t, t + 1.5, "Cada punto se une a su capitán más cercano"),
                (t + 1.5, t + T_ITER, "Cada capitán se mueve al centro de su grupo")]
ESCENAS += [
    (18.4, 22.0, "Repite hasta que nada cambie: grupos encontrados SIN etiquetas"),
    (22.0, 25.4, "K-MEANS: así se agrupan clientes, canciones o píxeles"),
    (25.4, 30.0, "!¡Envíaselo a quien estudie IA! Yo ya lo he hecho."),
]

VOZ = {
    "gancho": "¡Nadie me dijo qué buscar… y lo encontré!",
    1: "¡Pongo tres capitanes al azar! Ahí, ahí, y ahí.",
    2: ("Cada punto se une a su capitán más cercano. "
        "Y cada capitán se mueve al centro de su grupo.", 12.4),
    3: "", 4: "", 5: "",
    6: ("Y se repite. Otra vez. Y otra.", 18.4),
    7: "", 8: "", 9: "",
    10: "Hasta que nada cambia. Grupos encontrados, sin etiquetas.",
    11: "Esto es ca mins: así se agrupan clientes o canciones.",
}
EFECTOS = [(3.2, "pop")] + [(T0_ITER + i * T_ITER + 1.5, "whoosh") for i in range(3)] \
    + [(18.4, "pop")]

PORTADA = dict(titulo=["Nadie le dijo", "qué buscar…", "y lo encontró"], amarilla=2, t=18.5, gesto="piensa")

reel = Reel(2, "Nadie le dijo qué buscar… y lo encontró", ESCENAS, 30.0,
            voz=VOZ, efectos=EFECTOS, musica={"bpm": 104,
            "progresion": ((50, 53, 57), (46, 50, 53), (53, 57, 60), (48, 52, 55))},
            portada=PORTADA)
ax = reel.ax
ax.set_xlim(-5, 5)
ax.set_ylim(-4.6, 4.2)

lineas = LineCollection([], linewidths=1.2, zorder=1)
ax.add_collection(lineas)
puntos = ax.scatter(X[:, 0], X[:, 1], s=70, c=[GRIS] * len(X), edgecolors="none", zorder=2)
capitanes = ax.scatter(historia[0][:, 0], historia[0][:, 1], s=0, marker="*", c=COLORES,
                       edgecolors=FG, linewidths=1.8, zorder=4)
etiqueta = ax.text(4.9, 4.0, "", color=FG, size=15, weight="bold", ha="right", va="top")


def draw(t):
    lineas.set_segments([])
    if t < 3.2:
        puntos.set_facecolors([GRIS] * len(X))
        capitanes.set_sizes([0] * 3)
        etiqueta.set_text("")
        return
    if t < T0_ITER:
        a = ease((t - 3.2) / 0.8)
        capitanes.set_offsets(historia[0])
        capitanes.set_sizes([520 * a] * 3)
        capitanes.set_facecolors(COLORES)
        return
    capitanes.set_sizes([520] * 3)
    i = min(int((t - T0_ITER) // T_ITER), 3)
    tt = t - T0_ITER - i * T_ITER
    if t >= T0_ITER + 4 * T_ITER:
        i, tt = 3, T_ITER
    asign = asignaciones[i]
    previo = GRIS[None].repeat(len(X), 0) if i == 0 else COLORES[asignaciones[i - 1]]
    if tt < 1.5:
        a = ease(tt / 0.9)
        puntos.set_facecolors(previo + (COLORES[asign] - previo) * a)
        capitanes.set_offsets(historia[i])
        seg = [[X[j], historia[i][asign[j]]] for j in range(len(X))]
        lineas.set_segments(seg)
        col = COLORES[asign].copy()
        col[:, 3] = 0.45 * (1 - ease((tt - 0.9) / 0.6))
        lineas.set_colors(col)
    else:
        a = ease((tt - 1.5) / 1.2)
        puntos.set_facecolors(COLORES[asign])
        capitanes.set_offsets(historia[i] + (historia[i + 1] - historia[i]) * a)
    etiqueta.set_text(f"vuelta {i + 1}" if t < 18.4 else "¡3 grupos!")
    etiqueta.set_color(ACCENT if t >= 18.4 else FG)


if __name__ == "__main__":
    reel.render(draw, "02_kmeans", portada_t=11.0)
