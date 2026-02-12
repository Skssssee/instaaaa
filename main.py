from fastapi import FastAPI, HTTPException, Query
import httpx
import asyncio

app = FastAPI()

# --- All Providers from your Screenshots ---
PROVIDERS = {
    "tiktok": ["tmate", "snaptik", "savett", "thesocialcat", "tiktokio", "ssstik", "sstik", "tikmate", "ttdownloader", "tiktokdownload", "lovetik", "watermarkremover"], #
    "insta": ["ytdownload", "thesocialcat", "sssinstagram", "igram", "fsmvid", "snapdownloader", "instasave", "nuelink", "postsyncer", "reelsnap", "indown"], #
    "facebook": ["fbdown", "getfb", "socialplug", "fbvideodl", "solyptube", "fsmvid", "fdownload", "fdownloader", "postsyncer", "f-down", "ytdownload"], #
    "spotify": ["spotisongdownloader", "spotisaver", "spowload", "spotmate"], #
    "youtube": ["flvto", "savenow", "ytdownload", "ytdown", "yt1s"] #
}

BASE_URLS = {
    "tiktok": "https://tiktok-dlx.vercel.app/api",
    "insta": "https://instaaaa-pi.vercel.app/api",
    "facebook": "https://fb-dlx.vercel.app/api",
    "spotify": "https://spoti-dlx.vercel.app/api",
    "youtube": "https://yt-dlx.vercel.app/api"
}

def extract_clean_link(data):
    """Watermarked links ko laat maarta hai aur sirf clean links nikaalta hai."""
    if not data or not isinstance(data, dict): return None
    
    # 1. TikTok/General: HD priority
    for key in ["no_watermark_hd", "no_watermark", "download_link", "video", "url"]:
        link = data.get(key)
        if link and isinstance(link, str) and len(link) > 10 and link != "/":
            # Strict Filter: Agar link mein 'watermark' word hai (par 'no_' nahi), toh reject
            if "watermark" in link.lower() and "no_watermark" not in link.lower() and "no-watermark" not in link.lower():
                continue
            return link

    # 2. Instagram Specific: responseFinal structure
    res_final = data.get("data", {}).get("responseFinal", {}) if isinstance(data.get("data"), dict) else data.get("responseFinal", {})
    if res_final and isinstance(res_final, dict):
        if res_final.get("videoUrl"): return res_final["videoUrl"]
        formats = res_final.get("formats", [])
        if formats: return formats[0].get("url")

    return None

@app.get("/download")
async def aggregate(url: str = Query(...)):
    u = url.lower()
    platform = None
    if "tiktok.com" in u: platform = "tiktok"
    elif "inst" in u: platform = "insta"
    elif "facebook.com" in u or "fb.watch" in u: platform = "facebook"
    elif "spotify.com" in u: platform = "spotify"
    elif "youtube.com" in u or "youtu.be" in u: platform = "youtube"

    if not platform:
        raise HTTPException(status_code=400, detail="URL support nahi hai.")

    services = PROVIDERS[platform]
    base = BASE_URLS[platform]
    
    async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
        tasks = [client.get(f"{base}/{s}", params={"url": url}) for s in services]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        full_json = {}
        best_link = None
        
        for i, res in enumerate(responses):
            svc = services[i]
            if isinstance(res, httpx.Response) and res.status_code == 200:
                data = res.json()
                full_json[svc] = data
                if not best_link:
                    best_link = extract_clean_link(data)
            else:
                full_json[svc] = {"status": "failed"}

    return {
        "success": True,
        "platform": platform,
        "clean_download_url": best_link,
        "all_results": full_json
            }
