#!/bin/bash
# VenBraX — Cadena de estudio/podcast (broadcast) para la voz oficial de Alfonso.
# Distinta de clean_voice.sh: aquí SÍ se usa compresión + de-esser porque el
# destino es reproducción directa (podcast, narración de video), no el
# entrenamiento de un clonador de voz (que rinde mejor con audio menos
# procesado — para eso usar clean_voice.sh).
#
# Uso: ./clean_voice_podcast.sh entrada.m4a [salida_base]
# Produce: <salida_base>.wav (48kHz mono 24-bit) y <salida_base>_256k.mp3
#
# Cadena: highpass 80Hz (rumble) → afftdn moderado (piso de ruido -30dB,
# denoise suave para evitar artefactos "robóticos") → de-esser → EQ: -1.5dB
# @200Hz (limpia barro de graves), +2dB @3kHz (presencia/inteligibilidad),
# +1.5dB @8kHz (aire) → compresor broadcast (ratio 2.8:1, ataque 8ms,
# release 180ms, makeup +3dB) → loudnorm a -16 LUFS / -1 dBTP (estándar
# Spotify/Apple Podcasts).
set -euo pipefail

IN="${1:?Uso: clean_voice_podcast.sh entrada.m4a [salida_base]}"
OUT="${2:-voz_podcast}"

FF="$(command -v ffmpeg || true)"
if [ -z "$FF" ]; then
  FF="$(python3 -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())' 2>/dev/null || true)"
fi
[ -n "$FF" ] || { echo "ffmpeg no encontrado (instala ffmpeg o 'pip install imageio-ffmpeg')"; exit 1; }

FILTROS="highpass=f=80,afftdn=nf=-30:tn=1,deesser=i=0.15:m=0.5:f=0.5:s=o,equalizer=f=200:t=q:w=1:g=-1.5,equalizer=f=3000:t=q:w=1.3:g=2,equalizer=f=8000:t=q:w=1.5:g=1.5,acompressor=threshold=-18dB:ratio=2.8:attack=8:release=180:makeup=3,loudnorm=I=-16:TP=-1:LRA=8"

"$FF" -hide_banner -y -i "$IN" -af "$FILTROS" -ar 48000 -ac 1 -c:a pcm_s24le "${OUT}.wav"
"$FF" -hide_banner -y -i "${OUT}.wav" -c:a libmp3lame -b:a 256k "${OUT}_256k.mp3"

echo "--- Verificación de niveles (${OUT}.wav):"
"$FF" -hide_banner -i "${OUT}.wav" -af "astats=metadata=1:reset=0" -f null - 2>&1 | grep -E "Peak level dB|Noise floor dB|RMS level dB|Flat factor" | sort -u
echo "Listo: ${OUT}.wav y ${OUT}_256k.mp3 — escuchar SIEMPRE antes de usar."
