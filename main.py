from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import requests
import re

app = FastAPI(title="SnapInsta Private API")

# Request Model for JSON input
class VideoRequest(BaseModel):
    url: str

# --- CORE LOGIC ---
def get_snapinsta_link(target_link: str):
    """
    Sends the request to SnapInsta.top using the specific Multipart structure.
    """
    url = "https://snapinsta.top/action.php"

    # Headers from your capture
    # Note: We do NOT set 'Content-Type' manually here; 'requests' sets it automatically for multipart
    headers = {
        "Host": "snapinsta.top",
        "User-Agent": "Mozilla/5.0 (Linux; Android 15; RMX3870 Build/AP3A.240617.008) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.59 Mobile Safari/537.36",
        "Origin": "https://snapinsta.top",
        "Referer": "https://snapinsta.top/",
        "X-Requested-With": "XMLHttpRequest",  # Important for AJAX requests
        "Accept": "*/*",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    }

    # Session Cookie (Required)
    # If this expires, you must capture a new PHPSESSID from your browser/sniffer
    cookies = {
        "PHPSESSID": "vhv8e7avhmjv7meft3qtqorn6g"
    }

    # Data Payload (Multipart)
    # Passed as 'files' to ensure correct multipart/form-data encoding
    files = {
        'url': (None, target_link),
        'action': (None, 'post'),
        'lang': (None, 'en')
    }

    try:
        # Send POST request
        response = requests.post(url, headers=headers, cookies=cookies, files=files, timeout=15)

        if response.status_code == 200:
            response_text = response.text
            
            # Regex to find the download link (dl.php?token=...)
            match = re.search(r'dl\.php\?token=[^"\']+', response_text)
            
            if match:
                token_part = match.group(0)
                # Ensure we have the full URL
                if "https" not in token_part:
                    return f"https://snapinsta.top/{token_part}"
                else:
                    return token_part
            
            # Fallback: Sometimes it gives a direct link (googlevideo, etc.)
            match_direct = re.search(r'href=["\'](https://[^"\']*googlevideo[^"\']*)["\']', response_text)
            if match_direct:
                return match_direct.group(1)

            print("Debug: No link found in response.")
            return None
        else:
            print(f"Server Error: {response.status_code}")
            return None

    except Exception as e:
        print(f"Exception: {e}")
        return None

# --- ENDPOINT 1: Get JSON (For Apps/Bots) ---
@app.post("/api/get-link")
async def get_link(video: VideoRequest):
    """
    Send JSON body: {"url": "https://instagram..."}
    Returns JSON: {"download_url": "..."}
    """
    download_url = get_snapinsta_link(video.url)
    
    if download_url:
        return {"status": "success", "download_url": download_url}
    else:
        raise HTTPException(status_code=400, detail="Could not extract video link. Session may be expired.")

# --- ENDPOINT 2: Direct Download (For Browsers) ---
@app.get("/api/download")
async def download_video(url: str = Query(..., description="The Instagram URL")):
    """
    Visit: http://localhost:8000/api/download?url=YOUR_INSTA_LINK
    This will redirect you immediately to the video file.
    """
    download_url = get_snapinsta_link(url)
    
    if download_url:
        return RedirectResponse(url=download_url)
    else:
        raise HTTPException(status_code=400, detail="Could not fetch video.")

if __name__ == "__main__":
    import uvicorn
    # Run on localhost port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
