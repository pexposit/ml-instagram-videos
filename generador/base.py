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
from matplotlib.colors import to_rgb  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

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
PANEL = "#0B0F16"  # fondo del marco de la animación
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


# Quién habla en cada escena, según cómo empieza su texto:
#   "!"  → el robot (amarillo) · "P:" → Paco, el cuñado · "V:" → el Profesor Voltio
#   sin prefijo → la narradora (blanco)
COLOR_HABLANTE = {"robot": ACCENT, "paco": "#FF8A65", "voltio": "#7BE495", "narrador": FG}


def hablante(texto):
    if texto.startswith("!"):
        return "robot"
    if texto.startswith("P:"):
        return "paco"
    if texto.startswith("V:"):
        return "voltio"
    return "narrador"


def limpio(texto):
    for pre in ("!", "P:", "V:"):
        if texto.startswith(pre):
            return texto[len(pre):].strip()
    return texto


class Reel:
    def __init__(self, numero, gancho, escenas, duracion, voz=None, efectos=(), musica=None,
                 serie=SERIE, portada=None, asoma=True, tres_d=False, teaser=None,
                 retratos=False):
        """Los tiempos de escenas, voz y efectos son relativos al final de la intro.

        voz: {índice de escena: texto hablado o (texto, t_fin)}; "" = silencio;
             "gancho" = cómo se lee el gancho. Por defecto se lee el subtítulo.
        efectos: [(t, "pop" | "whoosh" | "error")].
        """
        self.escenas = escenas
        self.duracion = duracion
        # teaser = dict(t=segundo del momento más llamativo, texto="gancho en pantalla",
        #               pregunta="◀◀ …", dur=segundos, y=altura del gancho en la pantalla). Si existe, el vídeo EMPIEZA por ese
        #               momento (con el gancho en grande) y luego rebobina al principio, en
        #               lugar de la intro con el robot grande.
        self.teaser = teaser
        # retratos=True: personajes con acabado de plastilina (realistas.py) en lugar del
        # robot dibujado con vectores; además pueden intervenir Paco y el Profesor Voltio.
        self.retratos = retratos
        self.intro = teaser.get("dur", 2.6) if teaser else INTRO
        self.total = self.intro + duracion
        self.gancho = gancho
        self.voz = voz or {}
        self.efectos = efectos
        self.musica = musica
        self.serie = serie
        self.numero = numero
        self.portada = portada  # dict(titulo, amarilla, t, gesto); ver portada.py
        self.asoma = asoma      # False: el robot no se asoma junto al subtítulo (p. ej. si
        #                         ya sale dentro de la animación); sigue hablando igual
        self.boca_t = 0.0       # apertura de la boca del robot en el fotograma actual
        self.fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI, facecolor=BG)

        # Fondo con halo azul (mismo estilo que las portadas)
        fondo = self.fig.add_axes([0, 0, 1, 1], zorder=-10)
        fondo.axis("off")
        yy, xx = np.mgrid[0:1:200j, 0:1:120j]
        d = np.clip(np.hypot((xx - 0.5) * 0.56, yy - 0.47) / 0.55, 0, 1)[..., None]
        c0, c1 = np.array([0.10, 0.17, 0.30]), np.array(to_rgb(BG))
        fondo.imshow(c0 * (1 - d) + c1 * d, extent=(0, 1, 0, 1), origin="lower",
                     aspect="auto")

        # Zona segura: Instagram tapa ~12 % arriba y ~20 % abajo con su interfaz.
        # Etiqueta amarilla de la serie
        etiqueta = f"{serie}  ·  #{numero}"
        ancho = 0.06 + 0.0172 * len(etiqueta)
        self.fig.patches.append(FancyBboxPatch(
            (0.5 - ancho / 2, 0.84), ancho, 0.03, boxstyle="round,pad=0,rounding_size=0.015",
            transform=self.fig.transFigure, fc=ACCENT, ec="none", zorder=2))
        self.fig.text(0.5, 0.855, etiqueta, ha="center", va="center", size=11,
                      weight="black", color=BG, zorder=3)
        # Título: el de la portada (una línea en amarillo) o, si no hay, el gancho
        if portada:
            lineas, amarilla = portada["titulo"], portada.get("amarilla", -1)
        else:
            lineas, amarilla = wrap(gancho, 21).split("\n"), -1
        tam = 30 if max(len(x) for x in lineas) <= 15 else 27
        paso = tam * 1.18 / 72 * DPI / H
        y = 0.826
        for k, linea in enumerate(lineas):
            self.fig.text(0.5, y, linea, ha="center", va="top", size=tam, weight="black",
                          color=ACCENT if k == amarilla else FG, zorder=3)
            y -= paso

        # Panel enmarcado donde va la animación
        # tres_d=True: la animación es una escena 3D (cámara que gira, superficies…)
        if tres_d:
            self.ax = self.fig.add_axes([0.08, 0.30, 0.84, 0.345], projection="3d")
            self.ax.set_facecolor(PANEL)
            self.ax.set_axis_off()
            self.ax.set_box_aspect((1, 1, 0.75), zoom=1.25)
        else:
            self.ax = self.fig.add_axes([0.08, 0.30, 0.84, 0.345])
            self.ax.set_facecolor(PANEL)
            for s in self.ax.spines.values():
                s.set_visible(False)
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        self.marco = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.02",
                                    transform=self.fig.transFigure, fc=PANEL, ec=C1, lw=2.5,
                                    zorder=-5)
        self.fig.patches.append(self.marco)

        self.sub = self.fig.text(0.5, 0.282, "", ha="center", va="top", size=21,
                                 weight="bold", color=FG, linespacing=1.2)
        # Barra de progreso: invita a ver hasta el final
        self.barra_fondo = self.fig.add_artist(plt.Rectangle(
            (0.08, 0.676), 0.84, 0.006, transform=self.fig.transFigure, color=GRID))
        self.barra = self.fig.add_artist(plt.Rectangle(
            (0.08, 0.676), 0.0, 0.006, transform=self.fig.transFigure, color=ACCENT))

        # Marca de agua: firma visible bajo la barra + marca diagonal sobre la animación
        # (en el centro, para que no se pueda recortar sin destrozar el vídeo).
        self.fig.text(0.5, 0.664, CANAL, ha="center", va="center", size=11,
                      weight="bold", color=MUTED)
        self.fig.text(0.5, 0.475, CANAL, ha="center", va="center", size=30, weight="black",
                      color=FG, alpha=0.07, rotation=28, zorder=10)

    # ------------------------------------------------------------ robot presentador
    S_GRANDE, S_PEQ = 0.28, 0.10
    ALTO = H / W  # alto del fotograma en unidades de ancho

    def robot_guion(self):
        """Qué gesto hace el robot en cada momento (tiempos absolutos)."""
        t_final = self.intro + self.escenas[-1][0]
        if self.teaser:
            g = [(0.0, "senala", 0.3), (self.intro, "reposo", 0.3)]
        else:
            g = [(0.0, "saludo", 0.4), (1.7, "explica", 0.5), (self.intro, "reposo", 0.3)]
        for t0, t1, texto, *gesto in self.escenas[:-1]:
            if texto.startswith("!") and self.asoma:  # se asoma y habla (por defecto, señalando la animación)
                g += [(self.intro + t0, gesto[0] if gesto else "senala", 0.45),
                      (self.intro + t1, "reposo", 0.3)]
        g += [(t_final, "explica", 0.5), (t_final + 1.8, "saludo", 0.45)]
        return sorted(g)

    def robot_estado(self, ta):
        """Dónde está el robot en el segundo absoluto `ta`. Devuelve (dict | None, grande)."""
        t = ta - self.intro
        grande = dict(cx=0.5, cy=0.46 * self.ALTO)
        t_final = self.escenas[-1][0]
        if ta < self.intro and self.teaser:  # dice el gancho desde la esquina
            s = self.S_PEQ * min(ease(ta / 0.25), ease((self.intro - ta) / 0.2))
            return dict(cx=0.13, cy=0.25 * self.ALTO, s=s), False
        if ta < self.intro:  # presenta el gancho
            s = self.S_GRANDE * ease(ta / 0.35) * (1 - ease((ta - self.intro + 0.35) / 0.35))
            return dict(grande, s=s), True
        if t >= t_final:  # despedida y llamada a la acción
            return dict(grande, s=self.S_GRANDE * ease((t - t_final) / 0.35)), True
        for t0, t1, texto, *_g in self.escenas[:-1]:  # se asoma en los momentos clave
            if texto.startswith("!") and self.asoma and t0 <= t < t1:
                s = self.S_PEQ * min(ease((t - t0) / 0.3), ease((t1 - t) / 0.25))
                return dict(cx=0.13, cy=0.25 * self.ALTO, s=s), False
        return None, False

    # ------------------------------------------------------------ retratos de plastilina
    def _preparar_retratos(self, rax):
        """Pre-renderiza cada personaje con 5 aperturas de boca y ojos abiertos/cerrados."""
        from realistas import robot as r_robot, paco, voltio
        sprites = {}
        for b in range(5):
            for cerrado in (False, True):
                par = 0.08 if cerrado else 1.0
                for saluda in (False, True):
                    sprites[("robot", b, cerrado, saluda)] = r_robot(
                        t=0.0, boca=b / 4, parpado=par, saluda=saluda, tam=380)
                sprites[("paco", b, cerrado, False)] = paco(boca=b / 4, parpado=par, tam=320)
                sprites[("voltio", b, cerrado, False)] = voltio(boca=b / 4, parpado=par,
                                                                tam=320)
        self._sprite = rax.imshow(np.zeros((4, 4, 4)), extent=(0, 0.01, 0, 0.01), zorder=6,
                                  interpolation="bilinear")
        return sprites

    def _retrato(self, ta, t, estado, grande, bocas, i, sprites):
        """Coloca el personaje que toca (robot, Paco o Voltio). Devuelve (estado, grande)."""
        actor = "robot" if estado and estado["s"] > 0.003 else None
        if actor is None and t >= 0:
            for t0, t1, texto, *_g in self.escenas:
                q = hablante(texto)
                if q in ("paco", "voltio") and t0 <= t < t1:
                    s = self.S_PEQ * min(ease((t - t0) / 0.3), ease((t1 - t) / 0.25))
                    actor, estado, grande = q, dict(cx=0.2, cy=0.255 * self.ALTO, s=s), False
        if actor is None:
            self._sprite.set_visible(False)
            return estado, grande
        b = bocas.get(actor, bocas["robot"])
        nivel = int(round(4 * b[min(i, len(b) - 1)]))
        cerrado = (ta % 3.3) < 0.12
        saluda = actor == "robot" and grande and ta > self.total - 2.6
        img = sprites[(actor, nivel, cerrado, saluda)]
        ancho = (0.6 * estado["s"] / self.S_GRANDE) if grande else (0.42 * estado["s"] / self.S_PEQ)
        alto = ancho * 1.1
        cx, cy = estado["cx"], estado["cy"] + 0.004 * np.sin(2 * np.pi * 0.8 * ta)
        if grande:       # despedida: centrado y sin tapar el subtítulo
            cy = 0.48 * self.ALTO + 0.004 * np.sin(2 * np.pi * 0.8 * ta)
        if not grande:   # personaje de cuerpo entero, más grande, en la esquina inferior
            cx, cy = 0.2, 0.255 * self.ALTO + 0.004 * np.sin(2 * np.pi * 0.8 * ta)
        self._sprite.set_data(img)
        self._sprite.set_extent((cx - ancho / 2, cx + ancho / 2, cy - alto / 2, cy + alto / 2))
        self._sprite.set_visible(ancho > 0.005)
        return estado, grande

    # ------------------------------------------------------------ arranque "teaser"
    def _teaser(self, ta):
        """Primeros segundos: el momento más llamativo, el gancho en grande y un rebobinado.
        Devuelve el segundo de la animación que hay que dibujar."""
        tz = self.teaser
        if not hasattr(self, "_tz_texto"):
            self._tz_texto = self.fig.text(
                0.5, tz.get("y", 0.475), "", ha="center", va="center", size=28, weight="black",
                color=ACCENT, zorder=20, linespacing=1.1,
                bbox=dict(boxstyle="round,pad=0.45", fc=BG, ec=ACCENT, lw=3, alpha=0.9))
            self._tz_flash = self.fig.add_artist(plt.Rectangle(
                (0.08, 0.30), 0.84, 0.345, transform=self.fig.transFigure, color="#FFFFFF",
                zorder=19, alpha=0))
        rebobina = self.intro - 0.6
        self._tz_flash.set_alpha(0.35 * max(0.0, 1 - ta / 0.2))
        if ta < rebobina:
            palabras = tz["texto"].split()
            n = min(int(ta / 0.16) + 1, len(palabras))
            frac = (ta - (n - 1) * 0.16) / 0.16
            self._tz_texto.set_text(wrap(" ".join(palabras[:n]), 17))
            self._tz_texto.set_fontsize(28 * (1 + 0.18 * (1 - ease(frac))))
            self._tz_texto.set_color(ACCENT)
            self._tz_texto.set_visible(True)
            return tz["t"] + 0.35 * ta              # el momento clave, moviéndose un poco
        a = ease((ta - rebobina) / 0.55)
        self._tz_texto.set_text(tz.get("pregunta", "◀◀  ¿Cómo ha pasado esto?"))
        self._tz_texto.set_fontsize(24)
        self._tz_texto.set_color(FG)
        self._tz_texto.set_visible(True)
        return (tz["t"] + 0.35 * rebobina) * (1 - a)  # rebobina hasta el principio

    def _ocultar_teaser(self):
        if hasattr(self, "_tz_texto"):
            self._tz_texto.set_visible(False)
            self._tz_flash.set_alpha(0)

    def ajustar_marco(self):
        """Coloca el marco alrededor de la zona real de la animación (tras fijar su aspecto)."""
        self.ax.apply_aspect()
        x, y, w, h = self.ax.get_position().bounds
        self.marco.set_bounds(x - 0.012, y - 0.007, w + 0.024, h + 0.014)

    def subtitulo(self, t):
        for t0, t1, texto, *_g in self.escenas:
            if t0 <= t < t1:
                alpha = min(ease((t - t0) / 0.35), ease((t1 - t) / 0.25))
                return wrap(limpio(texto), 26), alpha, COLOR_HABLANTE[hablante(texto)]
        return "", 0.0, FG

    def pistas_voz(self):
        # el gancho lo dice el robot; las escenas con "!" también (subtítulo amarillo);
        # el resto, la narradora
        gancho = self.voz.get("gancho", self.gancho.replace("\n", " "))
        lineas = [(0.15, gancho, self.intro - 0.05, "robot")]
        for i, (t0, t1, texto, *_g) in enumerate(self.escenas):
            hablado = self.voz.get(i, limpio(texto))
            if isinstance(hablado, tuple):  # (texto, fin): la frase ocupa varias escenas
                hablado, t1 = hablado
            if hablado:
                quien = hablante(texto)
                lineas.append((self.intro + t0 + 0.1, hablado, self.intro + t1, quien))
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
        self.ajustar_marco()
        robot = Robot(rax)
        guion = self.robot_guion()
        salida = ROOT / "videos" / f"{nombre}.mp4"
        with tempfile.TemporaryDirectory() as d:
            mudo, sonido = Path(d) / "mudo.mp4", Path(d) / "audio.wav"

            # 1) audio primero: la boca del robot se mueve con la voz
            efectos = [(self.intro + t, tipo) for t, tipo in self.efectos]
            if self.teaser:  # golpe al empezar, "pop" por palabra y "rebobinado"
                n_pal = len(self.teaser["texto"].split())
                efectos += [(0.0, "whoosh"), (0.02, "pop")]
                efectos += [(0.12 + 0.16 * k, "pop") for k in range(1, n_pal, 2)]
                efectos += [(self.intro - 0.6, "whoosh")]
            # zumbido de motor cuando el robot cambia de gesto y se le ve
            efectos += [(tg, "servo") for tg, _g, _d in guion
                        if self.robot_estado(tg + 0.05)[0] is not None and tg > 0]
            pistas = banda_sonora(self.total, self.pistas_voz(), efectos, sonido, self.musica)
            nf = int(self.total * FPS)

            def apertura(voz):
                spf = len(voz) // nf
                rms = np.sqrt(np.mean(voz[: spf * nf].reshape(-1, spf) ** 2, 1))
                ref = np.percentile(rms[rms > 0.01], 90) if (rms > 0.01).any() else 1.0
                return np.clip(rms / (ref + 1e-9), 0, 1) ** 0.7

            bocas = {q: apertura(v) for q, v in pistas.items()}
            boca = bocas["robot"]
            sprites = self._preparar_retratos(rax) if self.retratos else None

            # 2) vídeo
            def update(i):
                ta = i / FPS
                t = ta - self.intro
                estado, grande = self.robot_estado(ta)
                self.ax.set_visible(not grande)
                self.marco.set_visible(not grande)
                b = boca[min(i, len(boca) - 1)]
                self.boca_t = b  # por si la animación dibuja al robot dentro de la escena
                if self.teaser and t < 0:
                    draw(self._teaser(ta))
                else:
                    self._ocultar_teaser()
                    draw(max(t, 0.0))
                if self.retratos:
                    robot.borrar()
                    estado, grande = self._retrato(ta, t, estado, grande, bocas, i, sprites)
                elif estado and estado["s"] > 0.003:
                    robot.dibujar(ta, pose_en(ta, guion, b), boca=b, **estado)
                else:
                    robot.borrar()
                texto, alpha, color = self.subtitulo(t) if t >= 0 else ("", 0.0, FG)
                if estado and not grande:  # personaje a la izquierda del subtítulo
                    texto = wrap(texto.replace("\n", " "), 16 if self.retratos else 19)
                    self.sub.set_x(0.64 if self.retratos else 0.58)
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
