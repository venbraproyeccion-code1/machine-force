"""
VenBraX Auto Instagram — automatiza el pipeline manual documentado en el
handoff: tarjeta HTML -> PNG (Chromium headless) -> bucket público (GCS) ->
publish_instagram(). Pensado para correr desde el mismo cron/wrapper que ya
ejecuta social_publisher.py en la VM.

Requiere en la máquina (ya presentes en venbratech-n8n):
  - chromium (o el binario que se pase con --chromium-bin / env CHROMIUM_BIN)
  - gsutil autenticado (scope cloud-platform de la VM ya lo cubre)
  - variables de entorno de social_publisher.py (IG_USER_ID, etc.)

Uso:
  python auto_instagram.py --slot 0 --dry-run
  python auto_instagram.py --slot 0
"""
import argparse
import os
import subprocess
from datetime import datetime

from content_engine import get_insight_of_day, format_for_platform
from visual_generator import generate_visual_html
from social_publisher import publish_instagram

DEFAULT_BUCKET = "venbrax-public-assets"


def render_png(html_path, png_path, chromium_bin):
    subprocess.run(
        [chromium_bin, "--headless", "--no-sandbox", "--disable-gpu",
         f"--screenshot={png_path}", "--window-size=1080,1350", html_path],
        check=True, capture_output=True, text=True,
    )


def upload_public(png_path, bucket, object_name):
    gcs_uri = f"gs://{bucket}/{object_name}"
    subprocess.run(["gsutil", "cp", png_path, gcs_uri], check=True,
                    capture_output=True, text=True)
    subprocess.run(["gsutil", "acl", "ch", "-u", "AllUsers:R", gcs_uri], check=True,
                    capture_output=True, text=True)
    return f"https://storage.googleapis.com/{bucket}/{object_name}"


def main():
    parser = argparse.ArgumentParser(description="VenBraX Auto Instagram")
    parser.add_argument("--slot", type=int, default=0, help="Slot del día 0-4")
    parser.add_argument("--handle", default="@venbrax")
    parser.add_argument("--bucket", default=os.environ.get("IG_BUCKET", DEFAULT_BUCKET))
    parser.add_argument("--chromium-bin", default=os.environ.get("CHROMIUM_BIN", "chromium"))
    parser.add_argument("--dry-run", action="store_true", help="No sube imagen ni publica")
    args = parser.parse_args()

    insight = get_insight_of_day(slot=args.slot)
    date_tag = datetime.utcnow().strftime("%Y%m%d")
    html_path = f"/tmp/venbrax-visual-{insight['id']}-{date_tag}.html"
    png_path = f"/tmp/venbrax-visual-{insight['id']}-{date_tag}.png"
    object_name = f"ig/{insight['id']}-{date_tag}.png"

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(generate_visual_html(insight, handle=args.handle))

    caption = format_for_platform(insight, "instagram")

    if args.dry_run:
        print(f"[AUTO-IG] dry-run: {insight['title']} -> {html_path} (sin render/upload/publish)")
        print(f"[AUTO-IG] caption ({len(caption)} chars): {caption[:120]}...")
        return

    render_png(html_path, png_path, args.chromium_bin)
    image_url = upload_public(png_path, args.bucket, object_name)
    print(f"[AUTO-IG] imagen pública: {image_url}")

    result = publish_instagram(caption, image_url)
    print(f"[AUTO-IG] publicado: {result}")


if __name__ == "__main__":
    main()
