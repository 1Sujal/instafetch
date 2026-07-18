import json
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup

class InstagramParser:
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=0, i",
        "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def find_key(self, obj, target):
        """Recursively find a key inside nested JSON."""
        if isinstance(obj, dict):
            if target in obj:
                return obj[target]
            for value in obj.values():
                result = self.find_key(value, target)
                if result is not None:
                    return result
        elif isinstance(obj, list):
            for item in obj:
                result = self.find_key(item, target)
                if result is not None:
                    return result
        return None

    def parse_dash_manifest(self, dash_manifest):
        """Extract highest quality video URL from DASH manifest."""
        try:
            root = ET.fromstring(dash_manifest)
        except Exception:
            return None

        videos = []
        for rep in root.iter():
            if not rep.tag.endswith("Representation"):
                continue

            width = int(rep.attrib.get("width", 0))
            height = int(rep.attrib.get("height", 0))
            bandwidth = int(rep.attrib.get("bandwidth", 0))

            base_url = None
            for elem in rep.iter():
                if elem.tag.endswith("BaseURL") and elem.text:
                    base_url = elem.text.replace("&amp;", "&").replace("\\/", "/")
                    break

            if base_url:
                videos.append({
                    "width": width,
                    "height": height,
                    "bandwidth": bandwidth,
                    "url": base_url,
                })

        if not videos:
            return None

        videos.sort(key=lambda x: (x["height"], x["width"], x["bandwidth"]), reverse=True)
        return videos[0]["url"]

    def get_video_url(self, post_url):
        response = self.session.get(post_url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Optional: local debug dump removed to keep things clean across machines,
        # but you can add it back if you specifically need it.

        scripts = soup.find_all("script", attrs={"type": "application/json", "data-sjs": True})
        if not scripts:
            raise Exception("No Instagram JSON scripts found")

        data = None
        for script in scripts:
            if not script.string:
                continue
            try:
                obj = json.loads(script.string)
            except Exception:
                continue

            if self.find_key(obj, "video_versions") or self.find_key(obj, "video_dash_manifest"):
                data = obj
                break

        if data is None:
            raise Exception("Video JSON not found")

        # Method 1: Direct video_versions
        video_versions = self.find_key(data, "video_versions")
        if video_versions:
            video_versions = sorted(
                video_versions,
                key=lambda x: (x.get("height", 0), x.get("width", 0), x.get("type", 0)),
                reverse=True
            )
            for video in video_versions:
                if video.get("url"):
                    return video["url"]

        # Method 2: DASH
        dash_manifest = self.find_key(data, "video_dash_manifest")
        if dash_manifest:
            url = self.parse_dash_manifest(dash_manifest)
            if url:
                return url

        return None

    def download_video(self, video_url, filename="instagram_video.mp4"):
        print(f"Downloading video to {filename}...")
        with self.session.get(video_url, stream=True, timeout=60) as response:
            response.raise_for_status()
            with open(filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        file.write(chunk)
        print("Download complete!")