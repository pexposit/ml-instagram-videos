"""IA desde cero #8 · Una IA aprendiendo a andar (aprendizaje por refuerzo).

El propio robot es el protagonista: se cae, prueba otra vez, gana y pierde puntos… y al
final anda solo. Como ya sale dentro de la animación, no se asoma junto al subtítulo.
"""
import numpy as np

from base import Reel, ease, ACCENT, C1, C2, C3, MUTED, FG, GRID, SERIE_CERO
from robot import Robot, pose_en, PIE_X, TOBILLO_Y

SUELO = 1.0
S = 1.6                       # tamaño del robot dentro de la escena
L = 0.25                      # longitud de medio paso (unidades del robot)

# Intentos: (inicio, x inicial, medios pasos antes de caer, duración de medio paso,
#            sentido de la caída (-1 delante, +1 detrás, 0 no se cae), nº de intento, puntos)
INTENTOS = [
    (4.6, 2.0, 1, 0.45, -1, 1, -10),
    (9.0, 4.6, 3, 0.4, +1, 2, -8),
    (12.7, 2.0, 2, 0.22, -1, 10, -5),
    (14.0, 2.0, 4, 0.2, -1, 100, 0),
    (15.3, 2.0, 7, 0.17, -1, 400, 6),
    (16.6, 2.0, 9, 0.15, -1, 800, 12),
    (18.0, 1.2, 15, 0.27, 0, 1000, 30),
]

ESCENAS = [  # "!" = habla el robot (subtítulo amarillo); el resto, la narradora
    (0.0, 4.2, "Esta IA tiene que aprender a andar. Nadie le dice cómo."),
    (4.2, 9.0, "Prueba a mover las piernas… y si se cae, pierde puntos"),
    (9.0, 12.6, "!¡Ay! Otra vez al suelo…"),
    (12.6, 18.0, "Si avanza sin caerse, gana puntos. Y lo intenta miles de veces"),
    (18.0, 24.0, "!¡Mírame! ¡Ya ando yo solito!"),
    (24.0, 28.6, "Es APRENDIZAJE POR REFUERZO: aprender probando, con premios y castigos"),
    (28.6, 33.0, "!¡Sígueme para más! Yo sigo practicando…"),
]
VOZ = {
    "gancho": "¡Hoy aprendo a andar! … Creo.",
    0: "Esta IA tiene que aprender a andar. Nadie le dice cómo.",
    1: "Prueba a mover las piernas. Y si se cae, pierde puntos.",
    3: "Si avanza sin caerse, gana puntos. Y lo intenta miles de veces.",
    5: "Es aprendizaje por refuerzo: aprender probando, con premios y castigos.",
}


def _t_caida(intento):
    t0, _x, n, h, sentido, *_r = intento
    return t0 + n * h if sentido else None


EFECTOS = ([(it[0], "servo") for it in INTENTOS]
           + [(_t_caida(it) + 0.45, "error") for it in INTENTOS if it[4]]
           + [(18.0 + 0.27 * k, "pop") for k in range(0, 15, 2)] + [(22.4, "pop"), (24.2, "pop")])
PORTADA = dict(titulo=["Una IA", "aprendiendo", "a andar"], amarilla=1, t=6.5,
               gesto="piensa")

reel = Reel(8, "Una IA aprendiendo\na andar", ESCENAS, 33.0, voz=VOZ, efectos=EFECTOS,
            serie=SERIE_CERO, musica={"bpm": 104}, portada=PORTADA, asoma=False)
ax = reel.ax
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.8)
ax.set_aspect("equal")
robot = Robot(ax)
ax.plot([0.2, 9.8], [SUELO, SUELO], color=GRID, lw=3, zorder=1)

artistas = []


def add(a):
    artistas.append(a)
    return a


def limpiar():
    while artistas:
        artistas.pop().remove()


def intento_en(t):
    actual = INTENTOS[0]
    for it in INTENTOS:
        if t >= it[0]:
            actual = it
    return actual


def andar(tt, h):
    """Medios pasos alternos: devuelve (avance del cuerpo, desplazamiento de pies, fase)."""
    k = int(tt // h)
    f = (tt % h) / h
    b = L * tt / h
    if k % 2 == 0:   # se mueve el pie derecho
        der = ((k - 1) + 2 * ease(f)) * L
        izq = k * L
        dy_d, dy_i = 0.13 * np.sin(np.pi * f), 0.0
    else:            # se mueve el izquierdo
        izq = ((k - 1) + 2 * ease(f)) * L
        der = k * L
        dy_d, dy_i = 0.0, 0.13 * np.sin(np.pi * f)
    return b, (izq - b, dy_i, der - b, dy_d), k + f


def draw(t):
    limpiar()
    t0, x0, n, h, sentido, numero, puntos = intento_en(t)
    guion = [(0.0, "reposo", 0.3), (22.3, "saludo", 0.45), (24.0, "pulgar", 0.45),
             (28.6, "reposo", 0.3)]
    pose = pose_en(t, guion, reel.boca_t)
    pies, giro, pivote = None, 0.0, None
    x = x0

    tt = t - t0
    if t >= 4.6 and tt >= 0:
        t_andar = n * h
        b, pies, fase = andar(min(tt, t_andar), h)
        x = x0 + b * S
        if not (sentido == 0 and tt > t_andar):
            balanceo = np.sin(np.pi * fase)
            pose["hd"] += 18 * balanceo
            pose["hi"] -= 18 * balanceo
            pose["bob"] -= 0.025 * abs(np.sin(np.pi * fase))
        if sentido == 0 and tt > t_andar:
            pies = None
        if sentido and tt > t_andar:  # se tambalea y se cae
            c = tt - t_andar
            if c < 0.45:
                giro = sentido * 95 * (c / 0.45) ** 2
            else:
                giro = sentido * (90 + 6 * np.exp(-(c - 0.45) * 8)
                                  * np.cos((c - 0.45) * 25))
            pivote = (-sentido * PIE_X, TOBILLO_Y - 0.1)
            pose["cab"] += sentido * 10
            pose["hd"], pose["hi"] = 70, 70        # brazos al aire
            pose["cd"], pose["ci"] = -20, -20
            pose["ojos"] = -sentido * 0.8
    if t < 4.6:
        x = INTENTOS[0][1]

    robot.dibujar(t, pose, cx=x, cy=SUELO + 1.0 * S + 0.02, s=S, boca=reel.boca_t, pies=pies,
                  giro=giro, pivote=pivote)

    # ---------------------------------------------- marcador de intento y puntos
    if t >= 4.6:
        add(ax.text(0.4, 7.45, f"intento {numero:,}".replace(",", "."), size=16,
                    weight="black", color=FG, va="top", zorder=8))
        t_caida = _t_caida(intento_en(t))
        if t_caida and t >= t_caida + 0.4:
            f = min((t - t_caida - 0.4) / 1.2, 1)
            add(ax.text(x - sentido * 1.4, 4.6 + 0.6 * f, f"{puntos:+d} puntos", size=16,
                        weight="black", color=C2 if puntos < 0 else C3, ha="center",
                        alpha=1 - f ** 3, zorder=8))
    if 22.3 <= t < 24.0:
        add(ax.text(x - 2.2, 4.0, "+30 puntos", size=18, weight="black", color=C3,
                    ha="center", alpha=ease((t - 22.3) / 0.3), zorder=8))

    # ---------------------------------------------- gráfica de puntos por intento
    if t >= 4.6:
        gx0, gx1, gy0, gy1 = 6.4, 9.6, 5.2, 7.3
        add(ax.plot([gx0, gx0, gx1], [gy1, gy0, gy0], color=MUTED, lw=1.5, zorder=6)[0])
        add(ax.text(gx0 - 0.1, gy1, "puntos", size=10, color=MUTED, ha="right", va="top",
                    zorder=6))
        add(ax.text(gx1, gy0 - 0.12, "intentos →", size=10, color=MUTED, ha="right", va="top",
                    zorder=6))
        hechos = [it for it in INTENTOS if (_t_caida(it) or it[0] + 4.0) + 0.4 <= t]
        if hechos:
            xs = [gx0 + 0.2 + (gx1 - gx0 - 0.4) * np.log10(it[5]) / 3 for it in hechos]
            ys = [gy0 + 0.15 + (gy1 - gy0 - 0.3) * (it[6] + 10) / 40 for it in hechos]
            add(ax.plot(xs, ys, color=ACCENT, lw=3, marker="o", ms=6, zorder=7)[0])

    if t >= 24.0 and t < 28.6:
        a = ease((t - 24.2) / 0.4)
        add(ax.text(3.2, 4.5, "APRENDIZAJE\nPOR REFUERZO", size=20, weight="black",
                    color=ACCENT, ha="center", va="center", alpha=a, zorder=8,
                    linespacing=1.0))
        add(ax.text(3.2, 3.55, "probar · premio · castigo · repetir", size=12,
                    weight="bold", color=FG, ha="center", va="center", alpha=a, zorder=8))


if __name__ == "__main__":
    reel.render(draw, "11_aprende_a_andar")
