from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

app = Flask(__name__)
CORS(app)

@app.route("/search", methods=["POST"])
def search_videos():
    api_key = request.form.get("api_key")
    query = request.form.get("query")
    youtube = build("youtube", "v3", developerKey=api_key)

    try:
        response = youtube.search().list(
            part="id,snippet",
            q=query,
            type="video",
            maxResults=50,
            fields="items(id(videoId),snippet(publishedAt,channelId,channelTitle,title,description,thumbnails(default(url)),liveBroadcastContent))",
            videoDefinition="high",
        ).execute()
    except HttpError as e:
        return jsonify({"error": str(e)}), 400

    video_ids = [item["id"]["videoId"] for item in response["items"]]
    video_list_response = youtube.videos().list(
        part="statistics,contentDetails",
        id=",".join(video_ids),
        fields="items(id,statistics(viewCount,likeCount,dislikeCount,commentCount),contentDetails(duration))",
    ).execute()

    videos = {}
    for item in video_list_response["items"]:
        videos[item["id"]] = {
            "statistics": item["statistics"],
            "duration": item["contentDetails"]["duration"],
        }

    results = []
    for item in response["items"]:
        video_id = item["id"]["videoId"]
        video_data = videos.get(video_id, {})
        results.append({
            "id": video_id,
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "publishDate": item["snippet"]["publishedAt"],
            "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
            "channelTitle": item["snippet"]["channelTitle"],
            "viewCount": int(video_data.get("statistics", {}).get("viewCount", 0)),
            "likeCount": int(video_data.get("statistics", {}).get("likeCount", 0)),
            "duration": video_data.get("duration", ""),
        })

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
