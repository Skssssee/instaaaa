from fastapi import FastAPI, HTTPException, Query
import httpx
import asyncio

app = FastAPI()

# --- Configuration ---
PROVIDERS = {
    "tiktok": ["tiktokio", "snaptik", "tmate", "ssstik", "tikmate", "savett", "ttdownloader", "lovetik"],
    "insta": ["ytdownload", "thesocialcat", "sssinstagram", "igram", "snapdownloader", "indown"],
    "facebook": ["fbdown", "getfb", "fdownloader", "fbvideodl"],
    "spotify": ["spotisongdownloader", "spotmate", "spowload"],
    "youtube": ["flvto", "yt1s", "ytdownload"]
}

BASE_URLS = {
    "tiktok": "https://tiktok-dlx.vercel.app/api",
    "insta": "https://instaaaa-pi.vercel.app/api", # Teri nayi API
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

@app.get("/download")
async def download_all(url: str = Query(...)):
    platform = detect_platform(url)
    if not platform:
        raise HTTPException(status_code=400, detail="Unsupported platform.")

    services = PROVIDERS[platform]
    base_url = BASE_URLS[platform]
    all_results = {}

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        # Saare providers ko ek saath call karega (Parallel)
        tasks = [client.get(f"{base_url}/{s}", params={"url": url}) for s in services]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, res in enumerate(responses):
            service_name = services[i]
            if isinstance(res, httpx.Response) and res.status_code == 200:
                data = res.json()
                # Sirf vahi data lega jo kaam ka hai
                all_results[service_name] = data
            else:
                all_results[service_name] = {"status": "failed"}

    return {
        "success": True,
        "platform": platform,
        "results": all_results # Yahan saare JSON milenge
    }

@app.get("/")
def home():
    return {"msg": "Mega API is Online", "endpoint": "/download?url=YOUR_URL"}
