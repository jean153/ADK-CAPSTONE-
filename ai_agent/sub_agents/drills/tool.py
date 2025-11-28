
import os
from googleapiclient.discovery import build

API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_KEY)

def search_youtube(query, max_results=5):
    search_request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results
    )
    search_response = search_request.execute()
    

    items = search_response.get("items", [])
    if not items:
        print("No videos found.")
        return []

    video_ids = [item["id"]["videoId"] for item in items]

    details_request = youtube.videos().list(
        part="snippet,statistics",
        id=",".join(video_ids)
    )
    details_response = details_request.execute()

    videos = []
    for item in details_response.get("items", []):
        videos.append({
            "title": item["snippet"]["title"],
            "video_id": item["id"],
            "url": f"https://www.youtube.com/watch?v={item['id']}",
            "channel_id": item["snippet"]["channelId"],
            "channel_name": item["snippet"]["channelTitle"],
            "views": int(item["statistics"]["viewCount"])
        })
    return videos


