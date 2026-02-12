
from fastapi import FastAPI, HTTPException, Query
import httpx
import random

app = FastAPI()

# --- Configuration from your provided sources ---
PROVIDERS = {
    "tiktok": [
        "tiktokio", "snaptik", "tmate", "ssstik", "tikmate", "savett", 
        "sstik", "ttdownloader", "tiktokdownload", "lovetik"
    ],
    "insta": [
        "ytdownload", "thesocialcat", "sssinstagram", "igram", "fsmvid", 
        "snapdownloader", "instasave", "nuelink", "postsyncer", "reelsnap", "indown"
    ],
    "facebook": [
        "fbdown", "getfb", "socialplug", "fbvideodl", "solyptube", "fsmvid", 
        "fdownload", "fdownloader", "postsyncer", "f-down", "ytdownload"
    ],
    "spotify": [
        "spotisongdownloader", "spotisaver", "spowload", "spotmate"
    ],
    "youtube": [
        "flvto", "savenow", "ytdownload", "ytdown", "yt1s"
    ]
}

BASE_URLS = {
    "tiktok": "https://tiktok-dlx.vercel.app/api",
    "insta": "https://insta-dlx.vercel.app/api",
    "facebook": "https://fb-dlx.vercel.app/api",
    "spotify": "https://spoti-dlx.vercel.app/api",
    "youtube": "https://yt-dlx.vercel.app/api"
}

def detect_platform(url: str):
    url = url.lower()
    if "tiktok.com" in url: return "tiktok"
    if "instagram.com" in url or "instagr.am" in url: return "insta"
    if "facebook.com" in url or "fb.watch" in url: return "facebook"
    if "spotify.com" in url: return "spotify"
    if "youtube.com" in url or "youtu.be" in url: return "youtube"
    return None

def extract_best_link(data):
    keys = ["no_watermark_hd", "no_watermark", "download_link", "video", "url", "audio"]
    for key in keys:
        val = data.get(key)
        if val and isinstance(val, str) and len(val) > 10 and val != "/":
            return val
    if "responseFinal" in data:
        links = data["responseFinal"].get("links", [])
        if links: return links[0].get("url")
    return None

@app.get("/download")
async def download(url: str = Query(...)):
    platform = detect_platform(url)
    if not platform:
        raise HTTPException(status_code=400, detail="Platform not supported.")

    provider_list = PROVIDERS[platform].copy()
    random.shuffle(provider_list)

    async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
        for service in provider_list:
            try:
                response = await client.get(f"{BASE_URLS[platform]}/{service}", params={"url": url})
                if response.status_code == 200:
                    data = response.json()
                    dl_link = extract_best_link(data)
                    if dl_link:
                        return {
                            "success": True,
                            "platform": platform,
                            "provider": service,
                            "title": data.get("title") or "Media File",
                            "download_url": dl_link,
                            "full_details": data 
                        }
            except: continue

    raise HTTPException(status_code=502, detail="All engines failed.")
