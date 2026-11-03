"""Foto de perfil de @hacerlointeligente: el robot de medio cuerpo saludando.

Genera perfil/icono_<variante>.png (1080×1080). Instagram la recorta en círculo, así que
todo lo importante queda dentro del círculo central.
"""
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import base  # noqa: E402,F401  (fuentes y estilo)
from robot import Robot, pose_en  # noqa: E402

SALIDA = Path(__file__).resolve().parent.parent / "perfil"
VARIANTES = {  # centro y borde del degradado de fondo
    "oscuro": ("#26406B", "#0B0F16"),
    "amarillo": ("#FFE27A", "#F4A90E"),
    "azul": ("#6FD6F7", "#2160D9"),
}


def icono(nombre, centro, borde, t=1.15):
    fig = plt.figure(figsize=(6, 6), dpi=180)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect("equal")
    ax.axis("off")
    # degradado radial
    yy, xx = np.mgrid[-1:1:600j, -1:1:600j]
    r = np.clip(np.hypot(xx, yy + 0.15) / 1.25, 0, 1)[..., None]
    c0 = np.array(matplotlib.colors.to_rgb(centro))
    c1 = np.array(matplotlib.colors.to_rgb(borde))
    ax.imshow(c0 * (1 - r) + c1 * r, extent=(-1, 1, -1, 1), origin="lower", zorder=0)
    # robot de medio cuerpo, saludando
    robot = Robot(ax)
    pose = pose_en(t, [(0.0, "saludo", 0.01)])
    pose["cab"] = 7
    robot.dibujar(t, pose, cx=-0.05, cy=-0.78, s=1.28, boca=0.35)
    fig.savefig(SALIDA / f"icono_{nombre}.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    SALIDA.mkdir(exist_ok=True)
    for n, (c0, c1) in VARIANTES.items():
        icono(n, c0, c1)
        print("OK", SALIDA / f"icono_{n}.png")
