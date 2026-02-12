from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
import httpx
import asyncio

app = FastAPI()

# --- Full Configuration from your Screenshots ---
PROVIDERS = {
    "tiktok": [
        "tmate", "snaptik", "savett", "thesocialcat", "tiktokio", 
        "ssstik", "sstik", "tikmate", "ttdownloader", "tiktokdownload", 
        "lovetik", "watermarkremover"
    ], #
    "insta": [
        "thesocialcat", "sssinstagram", "igram", "fsmvid", "snapdownloader", 
        "instasave", "nuelink", "postsyncer", "reelsnap", "indown", "ytdownload"
    ], #
    "facebook": [
        "fbdown", "getfb", "socialplug", "fbvideodl", "solyptube", "fsmvid", 
        "fdownload", "fdownloader", "postsyncer", "f-down", "ytdownload"
    ], #
    "spotify": [
        "spotisongdownloader", "spotisaver", "spowload", "spotmate"
    ], #
    "youtube": [
        "flvto", "savenow", "ytdownload", "ytdown", "yt1s"
    ] #
}

BASE_URLS = {
    "tiktok": "https://tiktok-dlx.vercel.app/api",
    "insta": "https://instaaaa-pi.vercel.app/api",
    "facebook": "https://fb-dlx.vercel.app/api",
    "spotify": "https://spoti-dlx.vercel.app/api",
    "youtube": "https://yt-dlx.vercel.app/api"
}

def detect_platform(url: str):
    u = url.lower()
    if "tiktok.com" in u: return "tiktok"
    if "instagram.com" in u or "instagr.am" in u: return "insta"
    if "facebook.com" in u or "fb.watch" in u: return "facebook"
    if "spotify.com" in u: return "spotify"
    if "youtube.com" in u or "youtu.be" in u: return "youtube"
    return None

@app.get("/", response_class=HTMLResponse)
async def docs():
    return "<h1>Mega API Online</h1><p>Use <code>/download?url=YOUR_URL</code></p>"

@app.get("/download")
async def aggregate_all(url: str = Query(...)):
    platform = detect_platform(url)
    if not platform:
        raise HTTPException(status_code=400, detail="Platform not supported.")

    base = BASE_URLS[platform]
    services = PROVIDERS[platform]
    
    async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
        # Ek saath saare providers ko call karega
        tasks = [client.get(f"{base}/{s}", params={"url": url}) for s in services]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        aggregated_results = {}
        for i, res in enumerate(responses):
            svc = services[i]
            if isinstance(res, httpx.Response) and res.status_code == 200:
                aggregated_results[svc] = res.json()
            else:
                aggregated_results[svc] = {"status": "failed", "msg": str(res)}

    return {
        "success": True,
        "platform": platform,
        "results": aggregated_results # Isme poora JSON milega har provider ka
    }
