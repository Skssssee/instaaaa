from fastapi import FastAPI, HTTPException, Query
import httpx
import asyncio

app = FastAPI()

# --- Config ---
PROVIDERS = {
    "tiktok": ["tiktokio", "snaptik", "tmate", "ssstik", "tikmate", "savett", "ttdownloader", "lovetik", "sstik", "tiktokdownload"],
    "insta": ["thesocialcat", "sssinstagram", "igram", "fsmvid", "snapdownloader", "instasave", "nuelink", "postsyncer", "reelsnap", "indown", "ytdownload"]
}

BASE_URLS = {
    "tiktok": "https://tiktok-dlx.vercel.app/api",
    "insta": "https://instaaaa-pi.vercel.app/api"
}

def detect_platform(url: str):
    u = url.lower()
    if "tiktok.com" in u: return "tiktok"
    if "instagram.com" in u or "instagr.am" in u: return "insta"
    return None

def extract_links(data):
    """Sare possible links extract karne ke liye logic."""
    res = {"video": [], "audio": []}
    # Check common keys from your JSON
    for key in ["no_watermark_hd", "no_watermark", "video", "url", "download_link"]:
        link = data.get(key)
        if link and isinstance(link, str) and len(link) > 10 and link != "/":
            res["video"].append(link)
    
    mp3 = data.get("mp3") or data.get("audio")
    if mp3 and len(mp3) > 10:
        res["audio"].append(mp3)
        
    return res

@app.get("/download")
async def download(url: str = Query(...)):
    platform = detect_platform(url)
    if not platform:
        raise HTTPException(status_code=400, detail="Unsupported URL.")

    services = PROVIDERS[platform]
    base = BASE_URLS[platform]
    all_extracted = {"videos": [], "audios": [], "raw_data": {}}

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        tasks = [client.get(f"{base}/{s}", params={"url": url}) for s in services]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, res in enumerate(responses):
            svc = services[i]
            if isinstance(res, httpx.Response) and res.status_code == 200:
                data = res.json()
                all_extracted["raw_data"][svc] = data
                found = extract_links(data)
                all_extracted["videos"].extend(found["video"])
                all_extracted["audios"].extend(found["audio"])

    # Remove duplicates
    all_extracted["videos"] = list(set(all_extracted["videos"]))
    all_extracted["audios"] = list(set(all_extracted["audios"]))
    
    return all_extracted
