from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import requests

app = FastAPI(title="FastDL Private API")

# Request Model for JSON input
class VideoRequest(BaseModel):
    url: str

# --- CORE LOGIC ---
def get_fastdl_link(target_link: str):
    """
    Sends the request to FastDL API using captured headers/cookies.
    """
    api_url = "https://api-wh.fastdl.app/api/convert"

    # Headers exactly as captured
    headers = {
        "Host": "api-wh.fastdl.app",
        "User-Agent": "Mozilla/5.0 (Linux; Android 15; RMX3870 Build/AP3A.240617.008) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.59 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Origin": "https://fastdl.app",
        "X-Requested-With": "mark.via.gp",
        "Referer": "https://fastdl.app/",
        "Accept-Encoding": "gzip, deflate",  # Removed br/zstd for compatibility
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    }

    # Cookies from your capture
    cookies = {
        "CF_SSStikUiExpSample": "26",
        "CF_SSStikUiExp": "inactive",
        "uid": "21355bc87d39727f",
        "adsForm": "64",
        "adsAfterSearch": "59",
        "adsPopupClick": "88",
        "errorFallbackPopup": "67"
    }

    # payload data
    # NOTE: The '_s' (signature) and 'ts' are tied to the specific URL in 'sf_url'.
    # For a generic API, these values need to be generated dynamically via JS.
    data = {
        "sf_url": target_link,
        "ts": "1770269448048",
        "_ts": "1770240123231",
        "_tsc": "0",
        "_sv": "2",
        "_s": "1e82a8c861a0947d030523ab72064b7121c9319709bb09215c3bc58eb89d39e8" 
    }

    try:
        response = requests.post(api_url, headers=headers, cookies=cookies, data=data, timeout=10)

        if response.status_code == 200:
            json_data = response.json()
            
            # Logic to extract URL based on FastDL response structure
            if 'url' in json_data and isinstance(json_data['url'], list) and len(json_data['url']) > 0:
                # Format 1: url is a list of dicts
                return json_data['url'][0]['url']
            elif 'url' in json_data and isinstance(json_data['url'], str):
                # Format 2: url is a direct string
                return json_data['url']
            elif 'data' in json_data and isinstance(json_data['data'], list) and len(json_data['data']) > 0:
                # Format 3: data list
                return json_data['data'][0]['url']
            else:
                print(f"API Error: URL not found in JSON: {json_data}")
                return None
        else:
            print(f"Server Error: {response.status_code} - {response.text}")
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
    download_url = get_fastdl_link(video.url)
    
    if download_url:
        return {"status": "success", "download_url": download_url}
    else:
        raise HTTPException(status_code=400, detail="Could not extract video link. Signature may be expired.")

# --- ENDPOINT 2: Direct Download (For Browsers) ---
@app.get("/api/download")
async def download_video(url: str = Query(..., description="The Instagram URL")):
    """
    Visit: http://localhost:8000/api/download?url=YOUR_INSTA_LINK
    This will redirect you immediately to the video file.
    """
    download_url = get_fastdl_link(url)
    
    if download_url:
        return RedirectResponse(url=download_url)
    else:
        raise HTTPException(status_code=400, detail="Could not fetch video.")

if __name__ == "__main__":
    import uvicorn
    # Run on localhost port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
