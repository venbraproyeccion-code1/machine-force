#!/bin/bash
# VenBraX — Limpieza de muestra de voz para clonación (ElevenLabs / AI Studio)
# Uso: ./clean_voice.sh entrada.mp3 [salida_base]
# Produce: <salida_base>.wav (44.1kHz mono 16-bit) y <salida_base>_192k.mp3
#
# Cadena: highpass 75Hz (quita rumble) → afftdn (reducción de ruido FFT moderada,
# agresividad baja para no meter artefactos que arruinan el clon) → EQ: +1dB @250Hz
# (cuerpo), +2.5dB @3.5kHz (presencia/inteligibilidad), +1.5dB @6.5kHz (aire, dentro
# del límite de grabaciones 16kHz) → loudnorm EBU R128 a -18 LUFS / -2 dBTP →
# recorte de silencio inicial.
set -euo pipefail

IN="${1:?Uso: clean_voice.sh entrada.mp3 [salida_base]}"
OUT="${2:-voz_clean}"

FF="$(command -v ffmpeg || true)"
if [ -z "$FF" ]; then
  FF="$(python3 -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())' 2>/dev/null || true)"
fi
[ -n "$FF" ] || { echo "ffmpeg no encontrado (instala ffmpeg o 'pip install imageio-ffmpeg')"; exit 1; }

FILTROS="highpass=f=75,afftdn=nf=-28:tn=1,equalizer=f=250:t=q:w=1:g=1,equalizer=f=3500:t=q:w=1.2:g=2.5,equalizer=f=6500:t=q:w=1.5:g=1.5,loudnorm=I=-18:TP=-2:LRA=7,silenceremove=start_periods=1:start_threshold=-45dB:start_duration=0.3"

"$FF" -hide_banner -y -i "$IN" -af "$FILTROS" -ar 44100 -ac 1 -c:a pcm_s16le "${OUT}.wav"
"$FF" -hide_banner -y -i "${OUT}.wav" -c:a libmp3lame -b:a 192k "${OUT}_192k.mp3"

echo "--- Verificación de niveles (${OUT}.wav):"
"$FF" -hide_banner -i "${OUT}.wav" -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"
echo "Listo: ${OUT}.wav y ${OUT}_192k.mp3 — escuchar SIEMPRE antes de subir al clonador."
