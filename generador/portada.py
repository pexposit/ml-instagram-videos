"""Portadas de los reels: título grande + el algoritmo en acción + el robot.

Instagram muestra la portada en la cuadrícula del perfil recortada a 3:4 (franja central de
1080×1440 de un vídeo 1080×1920), así que todo lo importante va dentro de esa franja.

Uso: crear_portada(reel, draw, nombre, PORTADA) con
  PORTADA = dict(titulo=["línea 1", "línea 2", ...], amarilla=índice de la línea destacada,
                 t=segundo de la animación que se enseña, gesto="senala" | "piensa" | ...,
                 robot_x=posición horizontal del robot (0.81 por defecto; ponerlo donde no
                 tape lo más importante de la gráfica))
"""
import io

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from base import ACCENT, BG, C1, CANAL, DPI, FG, H, MUTED, ROOT, W

ALTO = H / W


def _captura_animacion(reel, draw, t):
    """Dibuja la animación del vídeo en el segundo t y devuelve solo su zona como imagen."""
    rax = getattr(reel, "_rax", None)
    if rax is not None:
        for a in list(rax.patches):
            a.remove()
    reel.ax.set_visible(True)
    draw(t)
    buf = io.BytesIO()
    reel.fig.savefig(buf, dpi=DPI, facecolor=BG, format="png")
    buf.seek(0)
    img = plt.imread(buf)
    h, w = img.shape[:2]
    x0, y0, aw, ah = reel.ax.get_position().bounds
    return img[int(h * (1 - y0 - ah)):int(h * (1 - y0)), int(w * x0):int(w * (x0 + aw))]


def crear_portada(reel, draw, nombre, conf):
    from robot import Robot, pose_en

    anim = _captura_animacion(reel, draw, conf["t"])

    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI, facecolor=BG)
    # fondo con un halo de color detrás de la animación
    fondo = fig.add_axes([0, 0, 1, 1], zorder=0)
    fondo.axis("off")
    yy, xx = np.mgrid[0:1:200j, 0:1:120j]
    d = np.clip(np.hypot((xx - 0.5) * 0.56, yy - 0.45) / 0.55, 0, 1)[..., None]
    c0, c1 = np.array([0.10, 0.17, 0.30]), np.array(matplotlib_rgb(BG))
    fondo.imshow(c0 * (1 - d) + c1 * d, extent=(0, 1, 0, 1), origin="lower", aspect="auto")

    # etiqueta de la serie
    serie = f"{reel.serie}  ·  #{reel.numero}"
    ancho = 0.06 + 0.0172 * len(serie)
    fig.patches.append(FancyBboxPatch((0.5 - ancho / 2, 0.832), ancho, 0.034,
                                      boxstyle="round,pad=0,rounding_size=0.017",
                                      transform=fig.transFigure, fc=ACCENT, ec="none",
                                      zorder=2))
    fig.text(0.5, 0.849, serie, ha="center", va="center", size=12, weight="black",
             color="#0E1117", zorder=3)

    # título: una línea en amarillo para destacar la idea clave
    lineas = conf["titulo"]
    tam = 35 if max(len(x) for x in lineas) <= 15 else 31
    paso = tam * 1.18 / 72 * DPI / H
    y = 0.808
    for i, linea in enumerate(lineas):
        fig.text(0.5, y, linea, ha="center", va="top", size=tam, weight="black",
                 color=ACCENT if i == conf.get("amarilla", -1) else FG, zorder=3)
        y -= paso

    # el algoritmo en acción, grande y enmarcado
    alto_img = 0.32
    ancho_img = alto_img * H / W * anim.shape[1] / anim.shape[0]
    y_img = min(y - 0.012, 0.6) - alto_img
    x_img = 0.5 - ancho_img / 2
    marco = fig.add_axes([x_img - 0.012, y_img - 0.007, ancho_img + 0.024, alto_img + 0.014],
                         zorder=1)
    marco.axis("off")
    marco.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.04",
                                   transform=marco.transAxes, fc="#0B0F16", ec=C1, lw=2.5))
    img_ax = fig.add_axes([x_img, y_img, ancho_img, alto_img], zorder=2)
    img_ax.imshow(anim)
    img_ax.axis("off")

    # el robot, asomando abajo a la derecha
    rax = fig.add_axes([0, 0, 1, 1], zorder=4)
    rax.set_xlim(0, 1)
    rax.set_ylim(0, ALTO)
    rax.set_aspect("equal")
    rax.axis("off")
    rax.patch.set_alpha(0)
    gesto = conf.get("gesto", "saludo")
    pose = pose_en(2.0, [(0.0, gesto, 0.01)])
    # asomando por delante de la esquina inferior derecha de la gráfica (gusta al usuario)
    Robot(rax).dibujar(2.0, pose, cx=conf.get("robot_x", 0.81), cy=(y_img + 0.035) * ALTO,
                       s=0.16, boca=0.3)

    # firma del canal en el lado contrario al robot
    izq = conf.get("robot_x", 0.81) > 0.5
    xf, ha = (0.07, "left") if izq else (0.93, "right")
    fig.text(xf, y_img - 0.035, CANAL, ha=ha, va="center", size=15, weight="black",
             color=FG, zorder=3)
    fig.text(xf, y_img - 0.06, "La IA explicada fácil", ha=ha, va="center", size=12,
             weight="bold", color=MUTED, zorder=3)

    fig.savefig(ROOT / "portadas" / f"{nombre}.png", dpi=DPI, facecolor=BG)
    plt.close(fig)


def matplotlib_rgb(c):
    from matplotlib.colors import to_rgb
    return to_rgb(c)


if __name__ == "__main__":  # regenera las portadas sin volver a renderizar los vídeos
    import importlib
    import sys

    for mod in sys.argv[1:]:
        m = importlib.import_module(mod)
        nombre = mod[1:].split("_", 1)
        nombre = f"{nombre[0]}_{nombre[1]}"
        crear_portada(m.reel, m.draw, nombre, m.PORTADA)
        print("OK portada", nombre)
