"""
VenBraX Social Publisher — publicación directa vía API, SIN OAuth redirect.

Elimina el problema de "localhost / redirect URI" de raíz: en lugar del flujo
OAuth de n8n (que exige una redirect URI HTTPS registrada en Meta/LinkedIn),
usa tokens de larga duración generados una sola vez en los portales de
desarrollador. Cero dependencias — solo librería estándar.

Tokens requeridos (variables de entorno, en /opt/n8n/.env — NUNCA en git):
  FB_PAGE_ID              ID de la Facebook Page
  FB_PAGE_ACCESS_TOKEN    Page token de larga duración (no expira si viene
                          de un user token de larga duración)
  IG_USER_ID              instagram_business_account id (ver README)
  IG_ACCESS_TOKEN         (opcional — usa FB_PAGE_ACCESS_TOKEN si falta)
  LINKEDIN_ACCESS_TOKEN   Token con scope w_member_social
  LINKEDIN_AUTHOR_URN     urn:li:person:XXXX (de GET /v2/userinfo)

Uso:
  python social_publisher.py --platform facebook --dry-run
  python social_publisher.py --platform instagram --image-url https://...
  python social_publisher.py --platform linkedin
  python social_publisher.py --all --dry-run

Instagram requiere que la imagen esté en una URL pública (ej: Supabase
Storage). El caption sale del content engine; la imagen de la tarjeta
del visual_generator subida al bucket.
"""
import argparse
import base64
import hashlib
import hmac
import json
import os
import time
import urllib.request
import urllib.parse
import urllib.error

GRAPH = "https://graph.facebook.com/v21.0"


def _request(url, data=None, headers=None, method="POST"):
    """HTTP request con JSON de respuesta. Lanza RuntimeError con el error de la API."""
    body = None
    if data is not None:
        body = urllib.parse.urlencode(data).encode() if isinstance(data, dict) else data
    req = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:500]
        raise RuntimeError(f"API {e.code}: {detail}") from None
    except (urllib.error.URLError, OSError) as e:
        raise RuntimeError(f"Red: {e}") from None


def publish_facebook(message, page_id=None, token=None, dry_run=False):
    """Publica un post de texto en la Facebook Page."""
    if dry_run:
        return {"dry_run": True, "platform": "facebook", "chars": len(message)}
    page_id = page_id or os.environ["FB_PAGE_ID"]
    token = token or os.environ["FB_PAGE_ACCESS_TOKEN"]
    return _request(f"{GRAPH}/{page_id}/feed",
                    {"message": message, "access_token": token})


def publish_instagram(caption, image_url, ig_user_id=None, token=None, dry_run=False):
    """Publica una imagen en Instagram (proceso de 2 pasos: container → publish).

    image_url DEBE ser una URL pública (Supabase Storage, bucket público).
    """
    if dry_run:
        return {"dry_run": True, "platform": "instagram",
                "image_url": image_url, "chars": len(caption)}
    ig_user_id = ig_user_id or os.environ["IG_USER_ID"]
    token = token or os.environ.get("IG_ACCESS_TOKEN") or os.environ["FB_PAGE_ACCESS_TOKEN"]
    container = _request(f"{GRAPH}/{ig_user_id}/media",
                         {"image_url": image_url, "caption": caption,
                          "access_token": token})
    return _request(f"{GRAPH}/{ig_user_id}/media_publish",
                    {"creation_id": container["id"], "access_token": token})


def publish_linkedin(text, author_urn=None, token=None, dry_run=False):
    """Publica un post de texto en el perfil de LinkedIn."""
    if dry_run:
        return {"dry_run": True, "platform": "linkedin", "chars": len(text)}
    author_urn = author_urn or os.environ["LINKEDIN_AUTHOR_URN"]
    token = token or os.environ["LINKEDIN_ACCESS_TOKEN"]
    payload = json.dumps({
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }).encode()
    return _request("https://api.linkedin.com/v2/ugcPosts", payload, {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    })



def _twitter_oauth1(url, ck, cs, tk, ts_):
    """OAuth 1.0a header para Twitter API v2 (stdlib)."""
    import time as _t
    nonce = base64.b64encode(os.urandom(24)).decode().translate(str.maketrans("+/=", "xyz"))
    stamp = str(int(_t.time()))
    p = {"oauth_consumer_key": ck, "oauth_nonce": nonce,
         "oauth_signature_method": "HMAC-SHA1", "oauth_timestamp": stamp,
         "oauth_token": tk, "oauth_version": "1.0"}
    enc = lambda s: urllib.parse.quote(str(s), safe="")
    base = enc("POST") + "&" + enc(url) + "&" + enc(
        "&".join(f"{enc(k)}={enc(v)}" for k, v in sorted(p.items())))
    sig = base64.b64encode(
        hmac.new(f"{enc(cs)}&{enc(ts_)}".encode(), base.encode(), hashlib.sha1).digest()
    ).decode()
    p["oauth_signature"] = sig
    return "OAuth " + ", ".join(f'{enc(k)}="{enc(v)}"' for k, v in sorted(p.items()))


def publish_twitter(text, dry_run=False):
    """Publica un tweet via Twitter API v2 con OAuth 1.0a."""
    if dry_run:
        return {"dry_run": True, "platform": "twitter", "chars": len(text)}
    url = "https://api.twitter.com/2/tweets"
    auth = _twitter_oauth1(
        url,
        os.environ["TWITTER_API_KEY"],
        os.environ["TWITTER_API_SECRET"],
        os.environ["TWITTER_ACCESS_TOKEN"],
        os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
    )
    return _request(url, json.dumps({"text": text[:280]}).encode(),
                    {"Authorization": auth, "Content-Type": "application/json"})


PUBLISHERS = {
    "facebook": lambda content, args: publish_facebook(content, dry_run=args.dry_run),
    "instagram": lambda content, args: publish_instagram(
        content, args.image_url or os.environ.get("IG_IMAGE_URL", ""), dry_run=args.dry_run),
    "linkedin": lambda content, args: publish_linkedin(content, dry_run=args.dry_run),
    "twitter": lambda content, args: publish_twitter(content, dry_run=args.dry_run),
}

# plataforma del publisher → estilo del content engine
CONTENT_PLATFORM = {"facebook": "linkedin", "instagram": "instagram", "linkedin": "linkedin", "twitter": "twitter"}


def main():
    from content_engine import get_insight_of_day, format_for_platform

    parser = argparse.ArgumentParser(description="VenBraX Social Publisher")
    parser.add_argument("--platform", choices=list(PUBLISHERS.keys()))
    parser.add_argument("--all", action="store_true", help="Publica en las 3 plataformas")
    parser.add_argument("--dry-run", action="store_true", help="Muestra sin publicar")
    parser.add_argument("--image-url", help="URL pública de la imagen (Instagram)")
    parser.add_argument("--text", help="Texto manual (default: insight del día)")
    parser.add_argument("--slot", type=int, default=0, help="Slot del día 0-4 (múltiples posts/día)")
    args = parser.parse_args()

    if not args.platform and not args.all:
        parser.error("indica --platform o --all")
    platforms = list(PUBLISHERS.keys()) if args.all else [args.platform]

    insight = get_insight_of_day(slot=args.slot)
    for platform in platforms:
        content = args.text or format_for_platform(insight, CONTENT_PLATFORM[platform])
        try:
            result = PUBLISHERS[platform](content, args)
            print(f"[{platform.upper()}] {json.dumps(result, ensure_ascii=False)}")
        except KeyError as e:
            print(f"[{platform.upper()}] FALTA variable de entorno: {e}")
        except RuntimeError as e:
            print(f"[{platform.upper()}] ERROR: {e}")


if __name__ == "__main__":
    main()
