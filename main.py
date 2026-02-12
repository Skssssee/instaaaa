from fastapi import FastAPI, HTTPException, Query
import httpx
import asyncio

app = FastAPI()

# Screenshot ke hisaab se exact providers
PROVIDERS = {
    "tiktok": ["snaptik", "tmate", "ssstik", "tiktokio", "savett", "tikmate", "lovetik", "ttdownloader"],
    "insta": [
        "ytdownload", "thesocialcat", "sssinstagram", "igram", "fsmvid", 
        "snapdownloader", "instasave", "nuelink", "postsyncer", "reelsnap", "indown"
    ], #
    "facebook": ["fbdown", "getfb", "fdownloader", "fbvideodl"],
    "spotify": ["spotisongdownloader", "spotmate", "spowload"],
    "youtube": ["flvto", "yt1s", "ytdownload"]
}

# Multiple Bases for Instagram (Fallback ke liye)
BASE_URLS = {
    "tiktok": ["https://tiktok-dlx.vercel.app/api"],
    "insta": [
        "https://instaaaa-pi.vercel.app/api", 
        "https://insta-dlx.vercel.app/api" # Original Fallback
    ],
    "facebook": ["https://fb-dlx.vercel.app/api"],
    "spotify": ["https://spoti-dlx.vercel.app/api"],
    "youtube": ["https://yt-dlx.vercel.app/api"]
}

def extract_link(data):
    """Instagram aur TikTok dono ke formats ko handle karta hai."""
    if not data or not isinstance(data, dict): return None
    
    # Check simple keys first
    for k in ["no_watermark_hd", "no_watermark", "video", "url", "download_link", "videoUrl"]:
        if data.get(k) and len(str(data[k])) > 10: return data[k]
    
    # Check ytdownload format (Jo tumhare JSON mein tha)
    res_final = data.get("data", {}).get("responseFinal", {}) if isinstance(data.get("data"), dict) else data.get("responseFinal", {})
    if isinstance(res_final, dict):
        if res_final.get("videoUrl"): return res_final["videoUrl"]
        formats = res_final.get("formats", [])
        if formats and isinstance(formats, list): return formats[0].get("url")
    return None

@app.get("/download")
async def aggregate(url: str = Query(...)):
    u = url.lower()
    platform = "tiktok" if "tiktok.com" in u else "insta" if "inst" in u else "facebook" if "facebook" in u or "fb.watch" in u else "spotify" if "spotify" in u else "youtube" if "youtube" in u or "youtu.be" in u else None
    
    if not platform:
        raise HTTPException(status_code=400, detail="Invalid URL.")

    # Try all base URLs for the platform
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        for base in BASE_URLS[platform]:
            tasks = [client.get(f"{base}/{s}", params={"url": url}) for s in PROVIDERS[platform]]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_results = {}
            best_link = None
            
            success_count = 0
            for i, res in enumerate(responses):
                svc = PROVIDERS[platform][i]
                if isinstance(res, httpx.Response) and res.status_code == 200:
                    data = res.json()
                    all_results[svc] = data
                    success_count += 1
                    if not best_link:
                        best_link = extract_link(data)
                else:
                    all_results[svc] = {"status": "failed", "code": getattr(res, 'status_code', 'error')}
            
            # Agar kisi bhi provider ne data diya, toh result return karo
            if success_count > 0:
                return {
                    "success": True,
                    "platform": platform,
                    "base_used": base,
                    "clean_download_url": best_link,
                    "all_results": all_results
                }
    
    raise HTTPException(status_code=502, detail="All providers and bases failed.")
