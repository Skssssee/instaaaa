from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import requests
import re

app = FastAPI(title="InstaSave API")

# Request Model for JSON input
class VideoRequest(BaseModel):
    url: str

# --- CORE LOGIC ---
def extract_insta_link(target_link: str):
    """
    Sends the request to Instasave and extracts the CDN URL.
    """
    api_url = "https://api.instasave.website/media"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 15; RMX3870) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36",
        "Referer": "https://instasave.website/",
        "Origin": "https://instasave.website",
        "X-Requested-With": "mark.via.gp",
        "Content-Type": "application/x-www-form-urlencoded",
        # Note: These cookies might expire eventually and need refreshing
        "Cookie": "fpestid=zI1KrdoiWPO7woH9KnDLgOuWdPsKYUcjd_XqStswxsS1kV36q92ERmtFN3pQmYTD3tFxggoA; _cc_id=8e89079ebe8bfhhf3d25246b6ae2b96a1"
    }
    
    payload = {"url": target_link}

    try:
        response = requests.post(api_url, data=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            # Regex to find the CDN link
            match = re.search(r'href=\\"(https://cdn\.instasave\.website/\?token=.*?)\\"', response.text)
            
            if match:
                # Clean up escaped slashes
                final_url = match.group(1).replace('\\/', '/')
                return final_url
            else:
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
    download_url = extract_insta_link(video.url)
    
    if download_url:
        return {"status": "success", "download_url": download_url}
    else:
        raise HTTPException(status_code=400, detail="Could not extract video link. Check URL or Cookies.")

# --- ENDPOINT 2: Direct Download (For Browsers) ---
@app.get("/api/download")
async def download_video(url: str = Query(..., description="The Instagram URL")):
    """
    Visit: http://localhost:8000/api/download?url=YOUR_INSTA_LINK
    This will redirect you immediately to the video file to start downloading.
    """
    download_url = extract_insta_link(url)
    
    if download_url:
        # Redirects the browser directly to the file
        return RedirectResponse(url=download_url)
    else:
        raise HTTPException(status_code=400, detail="Could not fetch video.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

