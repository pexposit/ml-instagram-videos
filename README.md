# ml-instagram-videos · @hacerlointeligente

Reels verticales para Instagram que explican algoritmos de machine learning en unos 30 segundos.

| # | Vídeo | Gancho |
|---|---|---|
| 1 | [`videos/01_descenso_gradiente.mp4`](videos/01_descenso_gradiente.mp4) | Una IA no piensa. Hace ESTO millones de veces |
| 2 | [`videos/02_kmeans.mp4`](videos/02_kmeans.mp4) | Nadie le dijo qué buscar… y lo encontró |
| 3 | [`videos/03_sobreajuste.mp4`](videos/03_sobreajuste.mp4) | Tu IA saca un 10 en casa y un 3 en el examen |

- [`ANALISIS.md`](ANALISIS.md): qué tipo de vídeos funciona en Instagram y por qué están hechos así.
- [`PUBLICAR.md`](PUBLICAR.md): texto, hashtags y guion de voz de cada vídeo, más ideas para los siguientes.
- `portadas/`: imagen de portada de cada reel.

Los vídeos llevan **voz en off en castellano**, **música de fondo** y efectos de sonido.
Todo está generado aquí, así que no tiene derechos de autor: Instagram no los silenciará.
Si prefieres una canción en tendencia, puedes bajar el volumen del audio original al subirlo
y añadirla desde Instagram.

## Regenerar o crear vídeos nuevos

Necesita Python 3, `ffmpeg` y la fuente Inter.

```bash
pip install -r requirements.txt
# voz en castellano (Piper es_ES-sharvard); no se sube al repositorio por su tamaño
curl -L https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-es_ES-sharvard-medium.tar.bz2 | tar xj
mkdir -p generador/voz && mv vits-piper-es_ES-sharvard-medium/es_ES-sharvard-medium.onnx* generador/voz/
cd generador
python3 v01_descenso_gradiente.py   # crea videos/01_... y portadas/01_...
```

`generador/base.py` tiene la plantilla común: formato 1080×1920, gancho, subtítulos, barra de
progreso y colores. `generador/audio.py` genera la voz, la música y los efectos, y los mezcla
(la música baja cuando habla la voz). Cada vídeo nuevo solo define sus escenas, su animación,
qué dice la voz y en qué momentos suenan los efectos.

## Licencia

© 2026 @hacerlointeligente. **Todos los derechos reservados.** No se permite volver a
publicar, modificar ni usar comercialmente los vídeos, guiones o código sin permiso. Sí se
pueden compartir los reels originales desde Instagram. Detalles en [`LICENSE`](LICENSE).

Todos los vídeos llevan la marca de agua `@hacerlointeligente`: una firma bajo la barra de
progreso y otra en diagonal sobre la animación, que no se puede recortar sin estropear el vídeo.

## Créditos

- Voz: modelo Piper `es_ES-sharvard-medium`, entrenado con el corpus Sharvard
  (Universidad de Edimburgo), licencia [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).
- Música y efectos: generados por el propio código (`generador/audio.py`).
