"""Plantilla común para generar Reels verticales (1080x1920, 30 fps) con matplotlib.

Cada vídeo define:
  - un gancho (texto fijo arriba, visible desde el primer fotograma),
  - una lista de escenas (inicio, fin, subtítulo),
  - una función draw(t) que actualiza la animación central en el segundo t.
"""
import subprocess
import tempfile
import textwrap
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.animation import FuncAnimation, FFMpegWriter  # noqa: E402

_INTER = Path("/usr/share/fonts/opentype/inter")
for _f in ["Inter-Regular.otf", "Inter-SemiBold.otf", "Inter-Bold.otf",
           "Inter-ExtraBold.otf", "Inter-Black.otf"]:
    if (_INTER / _f).exists():
        font_manager.fontManager.addfont(str(_INTER / _f))
plt.rcParams["font.family"] = ["Inter", "DejaVu Sans"]

# Paleta (fondo oscuro, colores muy saturados: destacan en el feed)
BG = "#0E1117"
FG = "#F5F5F5"
MUTED = "#8B95A5"
GRID = "#232A36"
ACCENT = "#FFD23F"
C1 = "#4CC9F0"
C2 = "#F72585"
C3 = "#7BE495"

FPS = 30
W, H, DPI = 1080, 1920, 180
ROOT = Path(__file__).resolve().parent.parent
SERIE = "MACHINE LEARNING EN 30 s"
SERIE_CERO = "IA DESDE CERO"  # serie para quien empieza sin saber nada
CANAL = "@hacerlointeligente"
INTRO = 3.2  # segundos iniciales en los que la voz lee el gancho


def ease(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def wrap(text, width):
    """Ajusta líneas; respeta los saltos de línea escritos a mano."""
    return "\n".join(l for parte in text.split("\n") for l in textwrap.wrap(parte, width))


class Reel:
    def __init__(self, numero, gancho, escenas, duracion, voz=None, efectos=(), musica=None,
                 serie=SERIE, portada=None):
        """Los tiempos de escenas, voz y efectos son relativos al final de la intro.

        voz: {índice de escena: texto hablado o (texto, t_fin)}; "" = silencio;
             "gancho" = cómo se lee el gancho. Por defecto se lee el subtítulo.
        efectos: [(t, "pop" | "whoosh" | "error")].
        """
        self.escenas = escenas
        self.duracion = duracion
        self.total = INTRO + duracion
        self.gancho = gancho
        self.voz = voz or {}
        self.efectos = efectos
        self.musica = musica
        self.serie = serie
        self.numero = numero
        self.portada = portada  # dict(titulo, amarilla, t, gesto); ver portada.py
        self.fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI, facecolor=BG)

        # Zona segura: Instagram tapa ~12 % arriba y ~20 % abajo con su interfaz.
        self.fig.text(0.5, 0.885, f"{serie} · #{numero}", ha="center", va="center",
                      size=12, weight="bold", color=ACCENT)
        self.fig.text(0.5, 0.865, wrap(gancho, 21), ha="center", va="top",
                      size=26, weight="black", color=FG, linespacing=1.12)

        self.ax = self.fig.add_axes([0.08, 0.31, 0.84, 0.37])
        self.ax.set_facecolor(BG)
        for s in self.ax.spines.values():
            s.set_visible(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        self.sub = self.fig.text(0.5, 0.29, "", ha="center", va="top", size=21,
                                 weight="bold", color=FG, linespacing=1.2)
        # Barra de progreso: invita a ver hasta el final
        self.barra_fondo = self.fig.add_artist(plt.Rectangle(
            (0.08, 0.715), 0.84, 0.006, transform=self.fig.transFigure, color=GRID))
        self.barra = self.fig.add_artist(plt.Rectangle(
            (0.08, 0.715), 0.0, 0.006, transform=self.fig.transFigure, color=ACCENT))

        # Marca de agua: firma visible bajo la barra + marca diagonal sobre la animación
        # (en el centro, para que no se pueda recortar sin destrozar el vídeo).
        self.fig.text(0.5, 0.699, CANAL, ha="center", va="center", size=11,
                      weight="bold", color=MUTED)
        self.fig.text(0.5, 0.495, CANAL, ha="center", va="center", size=30, weight="black",
                      color=FG, alpha=0.07, rotation=28, zorder=10)

    # ------------------------------------------------------------ robot presentador
    S_GRANDE, S_PEQ = 0.29, 0.10
    ALTO = H / W  # alto del fotograma en unidades de ancho

    def robot_guion(self):
        """Qué gesto hace el robot en cada momento (tiempos absolutos)."""
        t_final = INTRO + self.escenas[-1][0]
        g = [(0.0, "saludo", 0.4), (1.7, "explica", 0.5), (INTRO, "reposo", 0.3)]
        for t0, t1, texto in self.escenas[:-1]:
            if texto.startswith("!"):  # se asoma y señala la animación
                g += [(INTRO + t0, "senala", 0.45), (INTRO + t1, "reposo", 0.3)]
        g += [(t_final, "explica", 0.5), (t_final + 1.8, "saludo", 0.45)]
        return sorted(g)

    def robot_estado(self, ta):
        """Dónde está el robot en el segundo absoluto `ta`. Devuelve (dict | None, grande)."""
        t = ta - INTRO
        grande = dict(cx=0.5, cy=0.47 * self.ALTO)
        t_final = self.escenas[-1][0]
        if ta < INTRO:  # presenta el gancho
            s = self.S_GRANDE * ease(ta / 0.35) * (1 - ease((ta - INTRO + 0.35) / 0.35))
            return dict(grande, s=s), True
        if t >= t_final:  # despedida y llamada a la acción
            return dict(grande, s=self.S_GRANDE * ease((t - t_final) / 0.35)), True
        for t0, t1, texto in self.escenas[:-1]:  # se asoma en los momentos clave
            if texto.startswith("!") and t0 <= t < t1:
                s = self.S_PEQ * min(ease((t - t0) / 0.3), ease((t1 - t) / 0.25))
                return dict(cx=0.13, cy=0.25 * self.ALTO, s=s), False
        return None, False

    def subtitulo(self, t):
        for t0, t1, texto in self.escenas:
            if t0 <= t < t1:
                alpha = min(ease((t - t0) / 0.35), ease((t1 - t) / 0.25))
                color = ACCENT if texto.startswith("!") else FG
                return wrap(texto.lstrip("!"), 26), alpha, color
        return "", 0.0, FG

    def pistas_voz(self):
        gancho = self.voz.get("gancho", self.gancho.replace("\n", " "))
        lineas = [(0.15, gancho, INTRO - 0.1)]
        for i, (t0, t1, texto) in enumerate(self.escenas):
            hablado = self.voz.get(i, texto.lstrip("!"))
            if isinstance(hablado, tuple):  # (texto, fin): la frase ocupa varias escenas
                hablado, t1 = hablado
            if hablado:
                lineas.append((INTRO + t0 + 0.1, hablado, INTRO + t1))
        return lineas

    def render(self, draw, nombre, portada_t=None):
        from audio import banda_sonora  # import tardío: solo hace falta al renderizar
        from robot import Robot, pose_en

        rax = self.fig.add_axes([0, 0, 1, 1], zorder=5)
        rax.set_xlim(0, 1)
        rax.set_ylim(0, self.ALTO)
        rax.set_aspect("equal")
        rax.axis("off")
        rax.patch.set_alpha(0)
        self._rax = rax
        robot = Robot(rax)
        guion = self.robot_guion()
        salida = ROOT / "videos" / f"{nombre}.mp4"
        with tempfile.TemporaryDirectory() as d:
            mudo, sonido = Path(d) / "mudo.mp4", Path(d) / "audio.wav"

            # 1) audio primero: la boca del robot se mueve con la voz
            efectos = [(INTRO + t, tipo) for t, tipo in self.efectos]
            # zumbido de motor cuando el robot cambia de gesto y se le ve
            efectos += [(tg, "servo") for tg, _g, _d in guion
                        if self.robot_estado(tg + 0.05)[0] is not None and tg > 0]
            voz = banda_sonora(self.total, self.pistas_voz(), efectos, sonido, self.musica)
            spf = len(voz) // int(self.total * FPS)
            rms = np.sqrt(np.mean(voz[: spf * int(self.total * FPS)].reshape(-1, spf) ** 2, 1))
            boca = np.clip(rms / (np.percentile(rms[rms > 0.01], 90) + 1e-9), 0, 1) ** 0.7

            # 2) vídeo
            def update(i):
                ta = i / FPS
                t = ta - INTRO
                estado, grande = self.robot_estado(ta)
                self.ax.set_visible(not grande)
                draw(max(t, 0.0))
                b = boca[min(i, len(boca) - 1)]
                if estado and estado["s"] > 0.003:
                    robot.dibujar(ta, pose_en(ta, guion, b), boca=b, **estado)
                else:
                    for a in list(rax.patches):
                        a.remove()
                texto, alpha, color = self.subtitulo(t) if t >= 0 else ("", 0.0, FG)
                if estado and not grande:  # robot asomado a la izquierda del subtítulo
                    texto = wrap(texto.replace("\n", " "), 19)
                    self.sub.set_x(0.58)
                else:
                    self.sub.set_x(0.5)
                self.sub.set_text(texto)
                self.sub.set_alpha(alpha)
                self.sub.set_color(color)
                self.barra.set_width(0.84 * ta / self.total)
                return []


            anim = FuncAnimation(self.fig, update, frames=int(self.total * FPS), blit=False)
            writer = FFMpegWriter(fps=FPS, codec="libx264", bitrate=-1, extra_args=[
                "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium"])
            anim.save(mudo, writer=writer, dpi=DPI, savefig_kwargs={"facecolor": BG})
            plt.close(self.fig)

            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mudo), "-i", str(sonido),
                            "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest",
                            "-movflags", "+faststart", str(salida)], check=True)
        if self.portada:
            from portada import crear_portada
            crear_portada(self, draw, nombre, self.portada)
        print("OK", salida)
