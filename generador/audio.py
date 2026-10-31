"""Banda sonora de los reels: voz en off (Piper TTS, offline) + música propia + efectos.

La música se sintetiza aquí mismo con numpy, así que no tiene derechos de autor.
"""
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

SR = 44100
# Voz "sharvard" de España (Piper), locutor masculino. Datos: Sharvard corpus, CC BY 3.0.
VOZ_MODELO = Path(__file__).resolve().parent / "voz" / "es_ES-sharvard-medium.onnx"
VOZ_LOCUTOR = "0"  # 0 = hombre, 1 = mujer


# ---------------------------------------------------------------- utilidades
def leer_wav(path):
    with wave.open(str(path)) as w:
        datos = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
        return datos.astype(np.float32) / 32768.0


def escribir_wav(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def tts(texto, velocidad=1.0):
    """Sintetiza `texto` y lo devuelve a 44,1 kHz (acelerado si velocidad > 1)."""
    with tempfile.TemporaryDirectory() as d:
        bruto, final = Path(d) / "v.wav", Path(d) / "f.wav"
        subprocess.run(["python3", "-m", "piper", "-m", str(VOZ_MODELO), "-s", VOZ_LOCUTOR, "-f", str(bruto),
                        "--sentence-silence", "0.15"],
                       input=texto.encode(), check=True, capture_output=True)
        filtros = f"atempo={velocidad:.3f}," if abs(velocidad - 1) > 1e-3 else ""
        # un poco de grave y compresión para que suene más "de radio"
        filtros += "highpass=f=80,bass=g=3:f=150,acompressor=threshold=-18dB:ratio=3"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(bruto), "-af", filtros,
                        "-ar", str(SR), "-ac", "1", str(final)], check=True)
        x = leer_wav(final)
    return 0.9 * x / (np.abs(x).max() + 1e-9)


# ---------------------------------------------------------------- música
def _nota(n):
    """Frecuencia de la nota MIDI n."""
    return 440.0 * 2 ** ((n - 69) / 12)


def musica(duracion, bpm=96, progresion=((57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62))):
    n = int(duracion * SR)
    t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    beat = 60 / bpm
    compas = 4 * beat
    rng = np.random.default_rng(0)

    # pad de acordes (cambia cada compás)
    for i in range(int(duracion / compas) + 1):
        acorde = progresion[i % len(progresion)]
        a, b = int(i * compas * SR), min(n, int((i + 1) * compas * SR) + int(0.3 * SR))
        if a >= n:
            break
        tt = t[a:b] - t[a]
        env = np.minimum(1, tt / 0.4) * np.minimum(1, np.maximum(0, (compas + 0.3 - tt) / 0.5))
        pad = sum(np.sin(2 * np.pi * _nota(m) * f * tt) for m in acorde for f in (1.0, 1.003))
        out[a:b] += 0.05 * env * pad
        # bajo en tiempos 1 y 3
        for k in (0, 2):
            s = a + int(k * beat * SR)
            e = min(n, s + int(beat * 1.6 * SR))
            if s < n:
                tb = t[s:e] - t[s]
                out[s:e] += 0.16 * np.sin(2 * np.pi * _nota(acorde[0] - 12) * tb) * np.exp(-tb * 2.2)
        # arpegio en corcheas
        for k in range(8):
            s = a + int(k * beat / 2 * SR)
            e = min(n, s + int(0.4 * SR))
            if s < n:
                ta = t[s:e] - t[s]
                f0 = _nota(acorde[k % 3] + 12)
                out[s:e] += 0.045 * np.sin(2 * np.pi * f0 * ta) * np.exp(-ta * 9)

    # batería: bombo (1 y 3), palmada suave (2 y 4), charles en corcheas
    for k in range(int(duracion / beat * 2) + 1):
        s = int(k * beat / 2 * SR)
        if s >= n:
            break
        if k % 4 == 0:
            e = min(n, s + int(0.35 * SR))
            tk = t[s:e] - t[s]
            fase = 2 * np.pi * np.cumsum(45 + 90 * np.exp(-tk * 30)) / SR
            out[s:e] += 0.5 * np.sin(fase) * np.exp(-tk * 9)
        if k % 4 == 2:
            e = min(n, s + int(0.2 * SR))
            tk = t[s:e] - t[s]
            out[s:e] += 0.08 * np.diff(rng.normal(size=e - s + 1)) * np.exp(-tk * 18)
        e = min(n, s + int(0.05 * SR))
        tk = t[s:e] - t[s]
        if e > s:
            out[s:e] += 0.025 * np.diff(rng.normal(size=e - s + 2), 2) * np.exp(-tk * 80)

    # fundido de entrada/salida
    out *= np.minimum(1, t / 0.5) * np.minimum(1, (duracion - t) / 1.5)
    return out / (np.abs(out).max() + 1e-9)


def efecto(tipo):
    """Pequeños sonidos para marcar acciones en pantalla."""
    if tipo == "pop":
        tt = np.arange(int(0.12 * SR)) / SR
        return np.sin(2 * np.pi * (500 + 900 * np.exp(-tt * 40)) * tt) * np.exp(-tt * 35)
    if tipo == "whoosh":
        tt = np.arange(int(0.45 * SR)) / SR
        ruido = np.random.default_rng(1).normal(size=len(tt))
        ruido = np.convolve(ruido, np.ones(12) / 12, "same")
        return 0.6 * ruido * np.sin(np.pi * tt / tt[-1]) ** 2
    if tipo == "error":
        tt = np.arange(int(0.35 * SR)) / SR
        return 0.5 * np.sign(np.sin(2 * np.pi * 140 * tt)) * np.exp(-tt * 8)
    if tipo == "servo":  # zumbido corto de motor al mover una articulación
        tt = np.arange(int(0.22 * SR)) / SR
        f = 170 + 140 * tt / tt[-1]
        onda = 2 * ((np.cumsum(f) / SR) % 1.0) - 1
        onda = np.convolve(onda, np.ones(6) / 6, "same")
        return 0.35 * onda * np.sin(np.pi * tt / tt[-1]) ** 0.5 * (1 + 0.3 * np.sin(2 * np.pi * 38 * tt))
    raise ValueError(tipo)


# ---------------------------------------------------------------- mezcla
def banda_sonora(duracion, voz, efectos, salida, musica_kw=None):
    """voz: [(t, texto, t_max_fin)], efectos: [(t, tipo)].

    Escribe la mezcla en `salida` y devuelve la pista de voz sola (para mover la boca del robot).
    """
    n = int(duracion * SR)
    pista_voz = np.zeros(n, np.float32)
    fin_anterior = 0.0
    for t, texto, t_fin in voz:
        inicio = max(t, fin_anterior + 0.1)
        x = tts(texto)
        hueco = t_fin - inicio
        if len(x) / SR > hueco:  # acelera un poco si no cabe
            vel = min(1.25, (len(x) / SR) / max(hueco, 0.5))
            x = tts(texto, vel)
        if inicio - t > 0.6:
            print(f"  aviso: «{texto}» empieza {inicio - t:.1f}s tarde")
        a = int(inicio * SR)
        b = min(n, a + len(x))
        pista_voz[a:b] += x[: b - a]
        fin_anterior = inicio + len(x) / SR
    if fin_anterior > duracion - 0.3:
        print(f"  aviso: la voz termina en {fin_anterior:.1f}s y el vídeo dura {duracion:.1f}s")

    pista_fx = np.zeros(n, np.float32)
    for t, tipo in efectos:
        x = efecto(tipo)
        a = int(t * SR)
        b = min(n, a + len(x))
        if a < n:
            pista_fx[a:b] += x[: b - a]

    # la música baja cuando hay voz (ducking)
    activa = (np.abs(pista_voz) > 0.02).astype(np.float64)
    k = int(0.25 * SR)
    acum = np.concatenate([[0.0], np.cumsum(activa)])
    idx = np.arange(n)
    env = (acum[np.minimum(idx + k // 2, n)] - acum[np.maximum(idx - k // 2, 0)]) / k
    gan_musica = 0.22 - 0.13 * np.clip(env * 3, 0, 1)
    mezcla = pista_voz + gan_musica * musica(duracion, **(musica_kw or {})) + 0.18 * pista_fx
    mezcla = 0.95 * mezcla / (np.abs(mezcla).max() + 1e-9)
    escribir_wav(salida, mezcla)
    return pista_voz
