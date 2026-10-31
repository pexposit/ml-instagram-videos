# ml-instagram-videos

Reels verticales para Instagram que explican algoritmos de machine learning en unos 30 segundos.

| # | Vídeo | Gancho |
|---|---|---|
| 1 | [`videos/01_descenso_gradiente.mp4`](videos/01_descenso_gradiente.mp4) | Una IA no piensa. Hace ESTO millones de veces |
| 2 | [`videos/02_kmeans.mp4`](videos/02_kmeans.mp4) | Nadie le dijo qué buscar… y lo encontró |
| 3 | [`videos/03_sobreajuste.mp4`](videos/03_sobreajuste.mp4) | Tu IA saca un 10 en casa y un 3 en el examen |

- [`ANALISIS.md`](ANALISIS.md): qué tipo de vídeos funciona en Instagram y por qué están hechos así.
- [`PUBLICAR.md`](PUBLICAR.md): texto, hashtags y guion de voz de cada vídeo, más ideas para los siguientes.
- `portadas/`: imagen de portada de cada reel.

Los vídeos van **sin audio** para que añadas una canción en tendencia o tu voz desde Instagram.

## Regenerar o crear vídeos nuevos

Necesita Python 3, `ffmpeg` y la fuente Inter.

```bash
pip install -r requirements.txt
cd generador
python3 v01_descenso_gradiente.py   # crea videos/01_... y portadas/01_...
```

`generador/base.py` tiene la plantilla común: formato 1080×1920, gancho, subtítulos, barra de
progreso y colores. Cada vídeo nuevo solo define sus escenas y su animación.
