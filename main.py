from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
import httpx
import asyncio

app = FastAPI(title="Mega-Aggregator API")

# --- Full Configuration from Screenshots ---
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
    ]  #
}

BASE_URLS = {
    "tiktok": "https://tiktok-dlx.vercel.app/api",
    "insta": "https://insta-dlx.vercel.app/api",
    "facebook": "https://fb-dlx.vercel.app/api",
    "spotify": "https://spoti-dlx.vercel.app/api",
    "youtube": "https://yt-dlx.vercel.app/api"
}

# --- Detection & Helper Logic ---
def detect_platform(url: str):
    url = url.lower()
    if "tiktok.com" in url: return "tiktok"
    if "instagram.com" in url or "instagr.am" in url: return "insta"
    if "facebook.com" in url or "fb.watch" in url: return "facebook"
    if "spotify.com" in url: return "spotify"
    if "youtube.com" in url or "youtu.be" in url: return "youtube"
    return None

# --- Endpoints ---

@app.get("/", response_class=HTMLResponse)
@app.get("/docs", response_class=HTMLResponse)
async def get_docs():
    """Mobile-friendly documentation page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Docs</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: sans-serif; padding: 20px; background: #f4f4f9; max-width: 800px; margin: auto; }
            .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
            code { background: #eee; padding: 3px 6px; border-radius: 4px; color: #d63384; font-weight: bold; }
            h2 { border-bottom: 2px solid #ddd; padding-bottom: 10px; }
        </style>
    </head>
    <body>
        <h1>🚀 Mega-Aggregator API</h1>
        <div class="card">
            <h2>📥 Usage</h2>
            <p>Send a GET request to: <br><code>/download?url=YOUR_LINK</code></p>
        </div>
        <div class="card">
            <h2>✅ Supported Services</h2>
            <ul>
                <li><b>TikTok:</b> tmate, snaptik, ssstik...</li>
                <li><b>Instagram:</b> igram, indown, ytdownload...</li>
                <li><b>Facebook:</b> fbdown, getfb, fdownloader...</li>
                <li><b>Spotify:</b> spotisongdownloader, spotmate...</li>
                <li><b>YouTube:</b> flvto, ytdownload, yt1s...</li>
            </ul>
        </div>
    </body>
    </html>
    """

@app.get("/download")
async def download_all(url: str = Query(..., description="The link to scrape")):
    platform = detect_platform(url)
    if not platform:
        raise HTTPException(status_code=400, detail="Unsupported platform.")

    base_url = BASE_URLS[platform]
    services = PROVIDERS[platform]
    all_responses = {}

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        # Run all provider requests in parallel for maximum speed
        tasks = []
        for service in services:
            target = f"{base_url}/{service}"
            tasks.append(client.get(target, params={"url": url}))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, response in enumerate(results):
            service_name = services[i]
            if isinstance(response, httpx.Response) and response.status_code == 200:
                all_responses[service_name] = response.json()
            else:
                all_responses[service_name] = {"status": "failed", "error": str(response)}

    return {
        "success": True,
        "platform": platform,
        "providers_checked": len(services),
        "results": all_responses
    }
