from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
import httpx
import asyncio

app = FastAPI()

# Configuration from your screenshots
PROVIDERS = {
    "tiktok": ["tmate", "snaptik", "savett", "thesocialcat", "tiktokio", "ssstik", "sstik", "tikmate", "ttdownloader", "tiktokdownload", "lovetik", "watermarkremover"],
    "insta": ["thesocialcat", "sssinstagram", "igram", "fsmvid", "snapdownloader", "instasave", "nuelink", "postsyncer", "reelsnap", "indown", "ytdownload"],
    "facebook": ["fbdown", "getfb", "socialplug", "fbvideodl", "solyptube", "fsmvid", "fdownload", "fdownloader", "postsyncer", "f-down", "ytdownload"],
    "spotify": ["spotisongdownloader", "spotisaver", "spowload", "spotmate"],
    "youtube": ["flvto", "savenow", "ytdownload", "ytdown", "yt1s"]
}

BASE_URLS = {
    "tiktok": "https://tiktok-dlx.vercel.app/api",
    "insta": "https://insta-dlx.vercel.app/api",
    "facebook": "https://fb-dlx.vercel.app/api",
    "spotify": "https://spoti-dlx.vercel.app/api",
    "youtube": "https://yt-dlx.vercel.app/api"
}

@app.get("/docs", response_class=HTMLResponse)
async def get_docs():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mega-Aggregator API Docs</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: -apple-system, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: auto; background: #f4f4f9; }
            code { background: #e2e2e2; padding: 2px 5px; border-radius: 4px; font-weight: bold; }
            .platform-card { background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            h2 { color: #333; border-bottom: 2px solid #ddd; padding-bottom: 5px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { text-align: left; padding: 8px; border-bottom: 1px solid #eee; }
            .endpoint { color: #d63384; }
        </style>
    </head>
    <body>
        <h1>🚀 Mega-Aggregator API Documentation</h1>
        <p>A unified interface for multiple downloading engines.</p>
        
        <div class="platform-card">
            <h2>📥 Main Endpoint</h2>
            <p><strong>Method:</strong> <code>GET</code></p>
            <p><strong>URL:</strong> <code class="endpoint">/download?url=YOUR_URL</code></p>
        </div>

        <div class="platform-card">
            <h2>📱 Supported Platforms</h2>
            <table>
                <tr><th>Platform</th><th>Keywords</th></tr>
                <tr><td><b>TikTok</b></td><td>tiktok.com, vt.tiktok</td></tr>
                <tr><td><b>Instagram</b></td><td>instagram.com, instagr.am</td></tr>
                <tr><td><b>Facebook</b></td><td>facebook.com, fb.watch</td></tr>
                <tr><td><b>Spotify</b></td><td>spotify.com</td></tr>
                <tr><td><b>YouTube</b></td><td>youtube.com, youtu.be</td></tr>
            </table>
        </div>

        <div class="platform-card">
            <h2>🛠️ Integrated Engines</h2>
            <ul>
                <li><b>TikTok:</b> tmate.cc, snaptik.app, savett.cc, etc.</li>
                <li><b>Instagram:</b> thesocialcat.com, igram.website, indown.io, etc.</li>
                <li><b>Facebook:</b> fbdown.blog, getfb.net, fdownloader.link, etc.</li>
                <li><b>Spotify:</b> spotisongdownloader.com, spotmate.online, etc.</li>
                <li><b>YouTube:</b> FLVTO, SaveNow, YT1s, etc.</li>
            </ul>
        </div>
    </body>
    </html>
    """

# ... rest of your download_all logic goes here ...
