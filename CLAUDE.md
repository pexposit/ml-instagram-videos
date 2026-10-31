# CLAUDE.md · Contexto del proyecto @hacerlointeligente

Este archivo es para que Claude (u otra persona) retome el proyecto en un chat nuevo sin
perder contexto. **Responde siempre en español (castellano de España).**

## Qué es

Reels de Instagram que explican inteligencia artificial y machine learning a gente **sin
conocimientos previos**, para la cuenta **@hacerlointeligente**. Objetivo del usuario:
muchas visitas y contenido muy profesional. Los vídeos se generan 100 % con código
(Python + matplotlib + ffmpeg): animación, voz, música, efectos y un robot presentador.

## Estructura

```
generador/
  base.py        Plantilla común de todos los reels (clase Reel): formato, gancho,
                 subtítulos, barra de progreso, marca de agua, robot y mezcla de audio.
  robot.py       Robot presentador articulado (esqueleto + gestos tipo servo).
  audio.py       Voz (Piper TTS), música sintetizada, efectos y mezcla con "ducking".
  icono.py       Genera la foto de perfil (perfil/icono_*.png).
  portada.py     Genera las portadas (título + captura del algoritmo + robot).
  v01_…v07_…py   Un archivo por vídeo: escenas, voz, efectos y función draw(t).
  voz/           Modelo de voz (NO se sube a git; ver "Instalación").
videos/          MP4 finales (1080×1920, 30 fps, AAC). portadas/: portada de cada vídeo.
perfil/          Foto de perfil (foto_perfil.png = la elegida, amarilla) y DESCRIPCION.md.
PUBLICAR.md      Texto, hashtags y créditos para publicar cada vídeo + ideas futuras.
ANALISIS.md      Qué funciona en Instagram Reels (con fuentes).
LICENSE          Todos los derechos reservados (@hacerlointeligente) + terceros.
```

## Vídeos hechos

Serie **«IA desde cero»** (para principiantes, publicar PRIMERO), `serie=SERIE_CERO`:
1. `04_programar_vs_aprender` · "La IA no se programa. Se ENSEÑA." (manzanas/naranjas)
2. `05_neurona` · "Así decide una neurona artificial" (¿voy a la playa? pesos y umbral)
3. `06_red_neuronal` · "Cómo reconoce una IA un número escrito a mano"
4. `07_chatgpt` · "ChatGPT escribe adivinando palabra a palabra"

Serie **«Machine learning en 30 s»** (más técnica): `01_descenso_gradiente`,
`02_kmeans`, `03_sobreajuste`.

Ideas pendientes: al final de `PUBLICAR.md` (sesgo en los datos, CNN, spam/Naive Bayes,
KNN, árbol de decisión, random forest).

## Decisiones tomadas con el usuario (no cambiarlas sin preguntar)

- **Voz:** Piper `es_ES-sharvard-medium`, **locutor 0 (hombre)**, acento de España.
  El usuario rechazó la voz `carlfm` y las de Kokoro por no sonar castellanas.
  Licencia CC BY 3.0 → hay que citar: «Voz: corpus Sharvard (U. Edimburgo, CC BY 3.0)».
- **Música y efectos:** sintetizados en `audio.py` (sin derechos de autor). Nunca usar
  canciones con copyright.
- **Robot:** diseño propio articulado (blanco y azul, visor oscuro con ojos LED, boca de
  barras LED tipo ecualizador). El usuario pidió muchas articulaciones y movimiento
  realista de robot; el gesto «explica» debe ser **lento y suave** (se quejó de que era
  brusco). Gestos: `apagado`, `reposo`, `saludo`, `explica`, `senala`, `piensa`, `pulgar`.
  **No copiar** ilustraciones de bancos de imágenes que el usuario enseñe: inspirarse en
  el estilo y hacer un diseño propio (lo hablamos con un robot de stock que le gustaba).
- **Apariciones del robot:** grande durante el gancho (intro de 3,2 s) y en la última
  escena (llamada a la acción); pequeño, junto al subtítulo y señalando, en las escenas
  cuyo texto empieza por `!` (resaltadas en amarillo).
- **Marca de agua:** `@hacerlointeligente` bajo la barra de progreso + en diagonal y
  semitransparente sobre la animación (para que no se pueda recortar).
- **Licencia:** todos los derechos reservados. Repositorio **privado** recomendado
  (el usuario preguntó por hacerlo público; se le avisó de que se podrían descargar los
  vídeos y se vería su correo en el primer commit; decide él desde la web de GitHub).
- **Foto de perfil:** `perfil/foto_perfil.png` (robot saludando, fondo amarillo).
- **Perfil:** nombre «IA explicada fácil 🤖», biografía opción A de `perfil/DESCRIPCION.md`.
- **Cuenta:** el usuario reutilizará una cuenta antigua (se le aconsejó revisar
  *Estado de la cuenta*, archivar publicaciones viejas y pasarla a profesional/creador).

## Estilo de los vídeos

- 1080×1920, fondo `#0E1117`, acento amarillo `#FFD23F`, colores `C1/C2/C3` de `base.py`,
  fuente Inter. Zona segura: Instagram tapa ~12 % arriba y ~20 % abajo.
- Gancho fijo arriba desde el primer fotograma; subtítulos grandes (se entienden sin
  sonido); una sola idea por vídeo con un ejemplo cotidiano; 30–35 s.
- Escena con `!` delante = momento clave (subtítulo amarillo + robot pequeño señalando).
- Cada vídeo termina invitando a guardar/enviar/seguir y anunciando el siguiente.
- La voz lee el subtítulo salvo que se indique otra frase en `VOZ`; escribir números y
  siglas como se pronuncian («ca mins» para K-means, «hacerlo inteligente» para el usuario).

## Cómo crear un vídeo nuevo

1. Copia un `vNN_*.py` parecido. Define `ESCENAS` [(inicio, fin, texto)], `VOZ`,
   `EFECTOS` [(t, "pop"|"whoosh"|"error"|"servo")], el `Reel(...)` y `draw(t)`.
   Los tiempos son relativos al final de la intro (`INTRO = 3.2` s).
2. Calcula ~13 caracteres/segundo de voz para que la frase quepa en su escena; `audio.py`
   avisa si una frase empieza tarde o si la voz se sale del final (entonces alarga el vídeo).
3. Antes del render completo, comprueba fotogramas sueltos (dibuja `draw(t)` + robot y
   guarda PNG a baja resolución) para detectar solapes; es mucho más rápido.
4. Render: `cd generador && python3 vNN_nombre.py` (5–10 min por vídeo; lanzar en
   segundo plano y en paralelo). Genera `videos/NN_nombre.mp4` y `portadas/NN_nombre.png`.
5. Añade su texto a `PUBLICAR.md` y la fila al `README.md`.
6. Portada: cada vídeo define `PORTADA = dict(titulo=[líneas], amarilla=i, t=segundo de la
   animación, gesto=pose del robot)` y la pasa con `portada=PORTADA`. El usuario quiere que
   en la portada **se vea el algoritmo**. Se genera al final del render, o sin renderizar con
   `python3 portada.py v01_descenso_gradiente v02_kmeans …`. Todo lo importante debe quedar
   en la franja 3:4 central (y de 0.125 a 0.875), que es lo que enseña la cuadrícula del perfil.

## Instalación (entorno nuevo)

```bash
pip install numpy matplotlib piper-tts
# Voz: Hugging Face está bloqueado en el entorno en la nube; usar el espejo de GitHub
curl -L https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-es_ES-sharvard-medium.tar.bz2 | tar xj
mkdir -p generador/voz && mv vits-piper-es_ES-sharvard-medium/es_ES-sharvard-medium.onnx* generador/voz/
```
También hacen falta `ffmpeg` y la fuente Inter (`/usr/share/fonts/opentype/inter`).

## Git

- Rama de trabajo: `claude/ml-algorithms-instagram-videos-kglgpz`. No hacer PR salvo que
  el usuario lo pida.
- El clon es superficial y solo sigue `main`: después de hacer push, ejecutar
  `git fetch origin claude/ml-algorithms-instagram-videos-kglgpz:refs/remotes/origin/claude/ml-algorithms-instagram-videos-kglgpz`
  para que conste la rama remota (si no, el hook de parada avisa de «commits sin subir»).
- El repositorio `pexposit/juego-valenciano` NO tiene nada que ver con este proyecto: no tocarlo.

## Limitaciones conocidas del entorno en la nube

- Instagram, Meta (graph.facebook.com), Hugging Face y los servicios de voz de Microsoft y
  Google están bloqueados. No se puede publicar en Instagram desde aquí.
- No hay herramienta para cambiar la visibilidad del repositorio: lo hace el usuario en
  GitHub (Settings → Danger Zone; en el móvil, navegador en modo escritorio).
- Claude no puede ver ni oír los vídeos en movimiento: revisa fotogramas sueltos y
  niveles de audio, y pide al usuario que confirme cómo suenan y se mueven.

## Siguiente paso pendiente

**Publicación automática (opción elegida: la 2, gratis):** tarea programada de GitHub
Actions que publique el siguiente reel de una cola con la API oficial de Instagram
(subida «resumable» de Reels, sin URL pública). Falta:
1. Que el usuario pase la cuenta a profesional, la vincule a una página de Facebook, cree
   una app en developers.facebook.com y guarde el token como secreto de GitHub
   (`IG_USER_ID`, `IG_TOKEN`). Hay que darle una guía paso a paso en español.
2. Crear `cola.json` (orden: serie «IA desde cero» primero) y el workflow programado
   (propuesta: lunes, miércoles y viernes a las 19:00 hora de España) + renovación del
   token (caduca cada 60 días).
El usuario pidió antes generar más vídeos; lo de la publicación automática quedó a la
espera de que lo confirme.
