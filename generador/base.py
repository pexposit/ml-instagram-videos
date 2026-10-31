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
INTRO = 3.2  # segundos iniciales en los que la voz lee el gancho


def ease(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def wrap(text, width):
    """Ajusta líneas; respeta los saltos de línea escritos a mano."""
    return "\n".join(l for parte in text.split("\n") for l in textwrap.wrap(parte, width))


class Reel:
    def __init__(self, numero, gancho, escenas, duracion, voz=None, efectos=(), musica=None):
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
        self.fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI, facecolor=BG)

        # Zona segura: Instagram tapa ~12 % arriba y ~20 % abajo con su interfaz.
        self.fig.text(0.5, 0.885, f"{SERIE} · #{numero}", ha="center", va="center",
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

    def render(self, draw, nombre, portada_t):
        def update(i):
            t = i / FPS - INTRO
            draw(max(t, 0.0))
            if t >= 0:
                texto, alpha, color = self.subtitulo(t)
            else:
                texto, alpha, color = "", 0.0, FG
            self.sub.set_text(texto)
            self.sub.set_alpha(alpha)
            self.sub.set_color(color)
            self.barra.set_width(0.84 * (t + INTRO) / self.total)
            return []

        update(int((INTRO + portada_t) * FPS))
        self.fig.savefig(ROOT / "portadas" / f"{nombre}.png", dpi=DPI, facecolor=BG)

        from audio import banda_sonora  # import tardío: solo hace falta al renderizar

        salida = ROOT / "videos" / f"{nombre}.mp4"
        with tempfile.TemporaryDirectory() as d:
            mudo, sonido = Path(d) / "mudo.mp4", Path(d) / "audio.wav"
            anim = FuncAnimation(self.fig, update, frames=int(self.total * FPS), blit=False)
            writer = FFMpegWriter(fps=FPS, codec="libx264", bitrate=-1, extra_args=[
                "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium"])
            anim.save(mudo, writer=writer, dpi=DPI, savefig_kwargs={"facecolor": BG})
            plt.close(self.fig)

            efectos = [(INTRO + t, tipo) for t, tipo in self.efectos]
            banda_sonora(self.total, self.pistas_voz(), efectos, sonido, self.musica)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mudo), "-i", str(sonido),
                            "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest",
                            "-movflags", "+faststart", str(salida)], check=True)
        print("OK", salida)
