"""Reel #3 · Sobreajuste: memorizar no es aprender."""
import numpy as np
from numpy.polynomial import Polynomial

from base import Reel, ease, ACCENT, C1, C2, C3, MUTED, FG

rng = np.random.default_rng(1)
x_train = np.sort(np.linspace(0.04, 0.96, 12) + rng.uniform(-0.025, 0.025, 12))
y_train = np.sin(2 * np.pi * x_train) + rng.normal(0, 0.25, 12)
# datos nuevos: justo en los huecos entre puntos de entrenamiento
x_test = ((x_train[:-1] + x_train[1:]) / 2)[[0, 2, 4, 6, 8, 10]]
y_test = np.sin(2 * np.pi * x_test) + rng.normal(0, 0.15, len(x_test))

XS = np.linspace(0, 1, 500)
MODELOS = {g: Polynomial.fit(x_train, y_train, g) for g in (1, 3, 11)}
CURVAS = {g: np.clip(m(XS), -3, 3) for g, m in MODELOS.items()}


def mse(g, x, y):
    return float(np.mean((MODELOS[g](x) - y) ** 2))


ESCENAS = [
    (0.0, 3.2, "Estos son los datos con los que estudia el modelo"),
    (3.2, 8.2, "Modelo demasiado simple: no capta nada"),
    (8.2, 13.2, "Modelo justo: entiende la forma"),
    (13.2, 18.2, "Modelo que se lo MEMORIZA: pasa por TODOS los puntos"),
    (18.2, 23.2, "!Llegan datos nuevos… y falla estrepitosamente"),
    (23.2, 26.4, "Memorizar no es aprender. Por eso se separan TRAIN y TEST."),
    (26.4, 29.5, "!Etiqueta a quien memoriza para el examen"),
]
FASES = [(3.2, 1, "INFRAAJUSTE", MUTED), (8.2, 3, "BIEN AJUSTADO", C3),
         (13.2, 11, "SOBREAJUSTE", C2)]

VOZ = {
    "gancho": "Tu IA saca un diez en casa, y un tres en el examen.",
    3: "Modelo que se lo memoriza: pasa por todos los puntos.",
    4: "Pero llegan datos nuevos. Y falla estrepitosamente.",
    5: "Memorizar no es aprender. Por eso se separan entrenamiento y prueba.",
}
EFECTOS = [(t0, "whoosh") for t0, *_r in FASES] + [(18.2, "pop")] \
    + [(19.0 + 0.25 * k, "error") for k in range(len(x_test))]

PORTADA = dict(titulo=["Un 10 en casa,", "un 3 en el examen"], amarilla=1, t=21.0, gesto="piensa")

reel = Reel(3, "Tu IA saca un 10\nen casa y un 3\nen el examen", ESCENAS, 29.5,
            voz=VOZ, efectos=EFECTOS, musica={"bpm": 90,
            "progresion": ((52, 55, 59), (48, 52, 55), (55, 59, 62), (50, 54, 57))},
            portada=PORTADA)
ax = reel.ax
ax.set_xlim(-0.03, 1.03)
ax.set_ylim(-2.6, 2.6)

curva, = ax.plot([], [], color=ACCENT, lw=4, zorder=3)
ax.scatter(x_train, y_train, s=110, color=C1, edgecolors=FG, linewidths=1.5, zorder=4)
test = ax.scatter(x_test, y_test, s=150, marker="D", color=C2, edgecolors=FG,
                  linewidths=1.5, zorder=5, alpha=0)
errores = [ax.plot([], [], color=C2, lw=2, ls=":", zorder=2)[0] for _ in x_test]
etiqueta = ax.text(0.5, 2.45, "", ha="center", va="top", size=17, weight="black")
marcador = ax.text(0.5, -2.5, "", ha="center", va="bottom", size=12, color=FG, weight="bold")
ax.text(0.0, 2.45, "● entrenamiento", color=C1, size=11, va="top")
leyenda_test = ax.text(1.0, 2.45, "◆ datos nuevos", color=C2, size=11, va="top", ha="right",
                       alpha=0)


def draw(t):
    for e in errores:
        e.set_data([], [])
    if t < 3.2:
        curva.set_data([], [])
        etiqueta.set_text("")
        marcador.set_text("")
        test.set_alpha(0)
        leyenda_test.set_alpha(0)
        return
    # fase actual y transición (morph) desde la anterior
    idx = max(i for i, (t0, *_r) in enumerate(FASES) if t >= t0)
    t0, g, nombre, color = FASES[idx]
    a = ease((t - t0) / 1.2)
    if idx == 0:
        n = max(2, int(len(XS) * a))
        curva.set_data(XS[:n], CURVAS[g][:n])
    else:
        prev = CURVAS[FASES[idx - 1][1]]
        curva.set_data(XS, prev + (CURVAS[g] - prev) * a)
    etiqueta.set_text(nombre)
    etiqueta.set_color(color)
    marcador.set_text(f"error estudiando: {mse(g, x_train, y_train):.2f}")

    if t >= 18.2:
        b = ease((t - 18.2) / 0.8)
        test.set_alpha(b)
        leyenda_test.set_alpha(b)
        pred = MODELOS[11](x_test)
        for k, e in enumerate(errores):
            c = ease((t - 19.0 - 0.25 * k) / 0.4)
            if c > 0:
                yp = np.clip(pred[k], -2.6, 2.6)
                e.set_data([x_test[k]] * 2, [y_test[k], y_test[k] + (yp - y_test[k]) * c])
        if t >= 20.5:
            marcador.set_text(f"error estudiando: {mse(11, x_train, y_train):.2f}   "
                              f"error en el examen: {mse(11, x_test, y_test):.2f}")
            marcador.set_color(ACCENT)
    else:
        marcador.set_color(FG)


if __name__ == "__main__":
    reel.render(draw, "03_sobreajuste", portada_t=21.0)
