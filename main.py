from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import math
import re

# .env 파일 로드
load_dotenv()

app = Flask(__name__)
# CORS 설정을 완전히 허용으로 변경 (개발 환경용)
CORS(app, 
     resources={r"/*": {
         "origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
     }},
     supports_credentials=True)

# 환경 변수에서 기본 API 키 가져오기
DEFAULT_API_KEY = os.getenv('YOUTUBE_API_KEY')

# 디버깅 로그 추가
@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())
    app.logger.debug('Path: %s', request.path)
    app.logger.debug('Method: %s', request.method)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    app.logger.debug('Response: %s', response.get_data())
    return response

@app.route("/search", methods=["POST"])
def search_videos():
    # FormData와 JSON 요청 모두 처리
    if request.is_json:
        data = request.get_json()
        api_key = data.get("api_key") or DEFAULT_API_KEY
        query = data.get("query")
    else:
        api_key = request.form.get("api_key") or DEFAULT_API_KEY
        query = request.form.get("query")
    
    if not api_key:
        return jsonify({"error": "API 키가 필요합니다. .env 파일이나 요청 파라미터를 통해 제공해주세요."}), 400
    
    if not query:
        return jsonify({"error": "검색어가 필요합니다."}), 400
    
    try:
        youtube = build("youtube", "v3", developerKey=api_key)

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
    
    if not video_ids:
        return jsonify([])  # 결과가 없는 경우 빈 배열 반환
    
    try:
        video_list_response = youtube.videos().list(
            part="statistics,contentDetails",
            id=",".join(video_ids),
            fields="items(id,statistics(viewCount,likeCount,dislikeCount,commentCount),contentDetails(duration))",
        ).execute()
    except HttpError as e:
        return jsonify({"error": f"동영상 상세 정보를 가져오는 중 오류 발생: {str(e)}"}), 400

    videos = {}
    for item in video_list_response.get("items", []):
        videos[item["id"]] = {
            "statistics": item.get("statistics", {}),
            "duration": item.get("contentDetails", {}).get("duration", ""),
        }

    results = []
    for item in response["items"]:
        video_id = item["id"]["videoId"]
        video_data = videos.get(video_id, {})
        
        # 안전하게 데이터 추출
        statistics = video_data.get("statistics", {})
        view_count = int(statistics.get("viewCount", 0)) if statistics.get("viewCount") else 0
        like_count = int(statistics.get("likeCount", 0)) if statistics.get("likeCount") else 0
        
        results.append({
            "id": video_id,
            "title": item["snippet"]["title"],
            "description": item["snippet"].get("description", ""),
            "publishDate": item["snippet"]["publishedAt"],
            "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
            "channelTitle": item["snippet"]["channelTitle"],
            "viewCount": view_count,
            "likeCount": like_count,
            "duration": video_data.get("duration", ""),
        })

    return jsonify(results)

@app.route("/analyze_video", methods=["POST"])
def analyze_video():
    """특정 동영상의 성과 분석 및 점수 계산"""
    if request.is_json:
        data = request.get_json()
        api_key = data.get("api_key") or DEFAULT_API_KEY
        video_id = data.get("video_id")
        channel_id = data.get("channel_id")
    else:
        api_key = request.form.get("api_key") or DEFAULT_API_KEY
        video_id = request.form.get("video_id")
        channel_id = request.form.get("channel_id")
    
    if not api_key:
        return jsonify({"error": "API 키가 필요합니다."}), 400
    
    if not video_id or not channel_id:
        return jsonify({"error": "동영상 ID와 채널 ID가 필요합니다."}), 400
    
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        
        # 1. 동영상 상세 정보 가져오기
        video_response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id
        ).execute()
        
        if not video_response.get("items"):
            return jsonify({"error": "동영상을 찾을 수 없습니다."}), 404
            
        video_data = video_response["items"][0]
        video_stats = video_data.get("statistics", {})
        video_snippet = video_data.get("snippet", {})
        publish_date = video_snippet.get("publishedAt")
        
        # 2. 채널 정보 가져오기
        channel_response = youtube.channels().list(
            part="statistics,snippet",
            id=channel_id
        ).execute()
        
        if not channel_response.get("items"):
            return jsonify({"error": "채널을 찾을 수 없습니다."}), 404
            
        channel_data = channel_response["items"][0]
        channel_stats = channel_data.get("statistics", {})
        
        # 3. 채널의 다른 동영상들 정보 가져오기 (최근 10개)
        channel_videos_response = youtube.search().list(
            part="id",
            channelId=channel_id,
            maxResults=10,
            type="video",
            order="date"
        ).execute()
        
        other_video_ids = [item["id"]["videoId"] for item in channel_videos_response.get("items", []) 
                          if item["id"]["videoId"] != video_id]
        
        other_videos_data = []
        if other_video_ids:
            other_videos_response = youtube.videos().list(
                part="statistics,snippet",
                id=",".join(other_video_ids)
            ).execute()
            other_videos_data = other_videos_response.get("items", [])
        
        # 4. 채널 성장 기여도 점수 계산
        growth_score = calculate_channel_growth_score(
            video_data, 
            channel_data, 
            other_videos_data
        )
        
        # 5. 독립적 영상 성과도 점수 계산
        performance_score = calculate_independent_performance_score(
            video_data, 
            channel_data, 
            other_videos_data
        )
        
        # 6. 콘텐츠 제작 인사이트 점수 계산
        insight_scores = calculate_content_insights(
            video_data,
            channel_data,
            other_videos_data
        )
        
        # 7. 세부 지표 및 설명 준비
        growth_factors = get_growth_factors(video_data, channel_data, other_videos_data)
        performance_factors = get_performance_factors(video_data, channel_data, other_videos_data)
        
        return jsonify({
            "video_id": video_id,
            "title": video_snippet.get("title", ""),
            "channel_id": channel_id,
            "channel_title": channel_data.get("snippet", {}).get("title", ""),
            "publish_date": publish_date,
            "view_count": int(video_stats.get("viewCount", 0)),
            "like_count": int(video_stats.get("likeCount", 0)),
            "comment_count": int(video_stats.get("commentCount", 0)),
            "channel_growth_score": growth_score,
            "independent_performance_score": performance_score,
            "growth_factors": growth_factors,
            "performance_factors": performance_factors,
            "content_insights": insight_scores
        })
        
    except HttpError as e:
        return jsonify({"error": f"YouTube API 오류: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"서버 오류: {str(e)}"}), 500

def calculate_channel_growth_score(video_data, channel_data, other_videos_data):
    """채널 성장 기여도 점수 계산"""
    video_stats = video_data.get("statistics", {})
    channel_stats = channel_data.get("statistics", {})
    
    # 가중치 설정
    view_weight = 0.4
    engagement_weight = 0.3
    relative_performance_weight = 0.3
    
    # 1. 조회수 기여 점수 (전체 채널 조회수 대비 이 영상의 조회수 비율)
    video_views = int(video_stats.get("viewCount", 0))
    channel_views = int(channel_stats.get("viewCount", 0))
    view_contribution = video_views / max(channel_views, 1) * 1000  # 스케일링
    view_score = min(view_contribution * 10, 10)  # 10점 만점
    
    # 2. 참여도 점수 (조회수 대비 좋아요+댓글 비율)
    likes = int(video_stats.get("likeCount", 0))
    comments = int(video_stats.get("commentCount", 0))
    engagement_ratio = (likes + comments) / max(video_views, 1)
    
    # 다른 영상들의 평균 참여도 계산
    other_engagement_ratios = []
    for other_video in other_videos_data:
        other_stats = other_video.get("statistics", {})
        other_views = int(other_stats.get("viewCount", 0))
        other_likes = int(other_stats.get("likeCount", 0))
        other_comments = int(other_stats.get("commentCount", 0))
        if other_views > 0:
            other_ratio = (other_likes + other_comments) / other_views
            other_engagement_ratios.append(other_ratio)
    
    avg_engagement = sum(other_engagement_ratios) / max(len(other_engagement_ratios), 1)
    relative_engagement = engagement_ratio / max(avg_engagement, 0.001)
    engagement_score = min(relative_engagement * 10, 10)  # 10점 만점
    
    # 3. 상대적 성과 점수 (채널의 다른 영상들 대비 성과)
    other_views = [int(v.get("statistics", {}).get("viewCount", 0)) for v in other_videos_data]
    avg_views = sum(other_views) / max(len(other_views), 1)
    relative_views = video_views / max(avg_views, 1)
    relative_score = min(relative_views * 10, 10)  # 10점 만점
    
    # 최종 점수 계산 (100점 만점)
    final_score = (
        view_score * view_weight +
        engagement_score * engagement_weight +
        relative_score * relative_performance_weight
    ) * 10
    
    return round(min(final_score, 100))

def calculate_independent_performance_score(video_data, channel_data, other_videos_data):
    """독립적 영상 성과도 점수 계산"""
    video_stats = video_data.get("statistics", {})
    channel_stats = channel_data.get("statistics", {})
    
    # 가중치 설정
    subscriber_ratio_weight = 0.4
    view_acceleration_weight = 0.3
    engagement_quality_weight = 0.3
    
    # 1. 구독자 대비 조회수 비율 (높을수록 비구독자가 많이 본 것으로 추정)
    subscribers = int(channel_stats.get("subscriberCount", 0))
    video_views = int(video_stats.get("viewCount", 0))
    
    # 구독자 대비 조회수 비율 - 높을수록 자체 성과가 좋음
    subscriber_view_ratio = video_views / max(subscribers, 1)
    
    # 다른 영상들의 평균 구독자 대비 조회수 비율
    other_ratios = []
    for other_video in other_videos_data:
        other_views = int(other_video.get("statistics", {}).get("viewCount", 0))
        other_ratio = other_views / max(subscribers, 1)
        other_ratios.append(other_ratio)
    
    avg_ratio = sum(other_ratios) / max(len(other_ratios), 1)
    relative_ratio = subscriber_view_ratio / max(avg_ratio, 0.001)
    subscriber_score = min(relative_ratio * 10, 10)  # 10점 만점
    
    # 2. 조회수 가속도 (최근 업로드 기간 고려)
    publish_date = datetime.fromisoformat(video_data.get("snippet", {}).get("publishedAt")[:-1])
    days_since_publish = (datetime.now() - publish_date).days
    
    # 업로드 후 경과 시간에 따른 조회수 정규화 (최근 영상은 조회수가 적을 수 있음)
    normalized_views = video_views / max(math.sqrt(days_since_publish + 1), 1)
    
    # 다른 영상들의 평균 정규화된 조회수
    other_normalized_views = []
    for other_video in other_videos_data:
        other_views = int(other_video.get("statistics", {}).get("viewCount", 0))
        other_date = datetime.fromisoformat(other_video.get("snippet", {}).get("publishedAt")[:-1])
        other_days = (datetime.now() - other_date).days
        norm_views = other_views / max(math.sqrt(other_days + 1), 1)
        other_normalized_views.append(norm_views)
    
    avg_norm_views = sum(other_normalized_views) / max(len(other_normalized_views), 1)
    view_acceleration = normalized_views / max(avg_norm_views, 1)
    acceleration_score = min(view_acceleration * 10, 10)  # 10점 만점
    
    # 3. 참여 품질 (좋아요 대 조회수 비율)
    likes = int(video_stats.get("likeCount", 0))
    like_ratio = likes / max(video_views, 1)
    
    # 다른 영상들의 평균 좋아요 비율
    other_like_ratios = []
    for other_video in other_videos_data:
        other_stats = other_video.get("statistics", {})
        other_views = int(other_stats.get("viewCount", 0))
        other_likes = int(other_stats.get("likeCount", 0))
        if other_views > 0:
            other_like_ratios.append(other_likes / other_views)
    
    avg_like_ratio = sum(other_like_ratios) / max(len(other_like_ratios), 1)
    relative_like_ratio = like_ratio / max(avg_like_ratio, 0.001)
    engagement_score = min(relative_like_ratio * 10, 10)  # 10점 만점
    
    # 최종 점수 계산 (100점 만점)
    final_score = (
        subscriber_score * subscriber_ratio_weight +
        acceleration_score * view_acceleration_weight +
        engagement_score * engagement_quality_weight
    ) * 10
    
    return round(min(final_score, 100))

def get_growth_factors(video_data, channel_data, other_videos_data):
    """채널 성장 기여도 세부 요소 계산"""
    video_stats = video_data.get("statistics", {})
    channel_stats = channel_data.get("statistics", {})
    
    video_views = int(video_stats.get("viewCount", 0))
    channel_views = int(channel_stats.get("viewCount", 0))
    
    # 다른 영상들의 평균 조회수
    other_views = [int(v.get("statistics", {}).get("viewCount", 0)) for v in other_videos_data]
    avg_views = sum(other_views) / max(len(other_views), 1) if other_views else 0
    
    return {
        "view_contribution": {
            "value": round(video_views / max(channel_views, 1) * 100, 2),
            "description": "이 영상의 조회수가 채널 전체 조회수에서 차지하는 비율"
        },
        "relative_performance": {
            "value": round(video_views / max(avg_views, 1), 2),
            "description": "채널의 다른 영상들 대비 이 영상의 조회수 비율"
        },
        "engagement_quality": {
            "value": round(int(video_stats.get("likeCount", 0)) / max(video_views, 1) * 100, 2),
            "description": "조회수 대비 좋아요 비율(%)"
        }
    }

def get_performance_factors(video_data, channel_data, other_videos_data):
    """독립적 영상 성과도 세부 요소 계산"""
    video_stats = video_data.get("statistics", {})
    channel_stats = channel_data.get("statistics", {})
    
    video_views = int(video_stats.get("viewCount", 0))
    subscribers = int(channel_stats.get("subscriberCount", 0))
    
    # 평균 비율 계산
    other_views = [int(v.get("statistics", {}).get("viewCount", 0)) for v in other_videos_data]
    avg_views = sum(other_views) / max(len(other_views), 1) if other_views else 0
    
    return {
        "subscriber_view_ratio": {
            "value": round(video_views / max(subscribers, 1), 2),
            "description": "구독자 수 대비 조회수 비율 (높을수록 비구독자 유입 많음)"
        },
        "channel_avg_comparison": {
            "value": round(video_views / max(avg_views, 1), 2),
            "description": "채널 평균 조회수 대비 이 영상의 조회수 비율"
        },
        "like_comment_ratio": {
            "value": round((int(video_stats.get("likeCount", 0)) + int(video_stats.get("commentCount", 0))) / max(video_views, 1) * 100, 2),
            "description": "조회수 대비 상호작용(좋아요+댓글) 비율(%)"
        }
    }

def calculate_content_insights(video_data, channel_data, other_videos_data):
    """콘텐츠 제작 인사이트 점수 계산"""
    try:
        # 트렌드 연관성 (인기 주제와의 연관성 및 시의성)
        trend_relevance = calculate_trend_relevance(video_data, other_videos_data)
        
        # 키워드 효율성 (제목, 태그, 설명의 검색 최적화 정도)
        keyword_efficiency = calculate_keyword_efficiency(video_data, other_videos_data)
        
        # 타겟 유입율 (새로운 시청자를 유입시키는 능력)
        target_acquisition = calculate_target_acquisition(video_data, channel_data)
        
        # 시청자 유지율 (시청자가 영상을 시청하는 정도)
        viewer_retention = calculate_viewer_retention(video_data, other_videos_data)
        
        # 경쟁 포화도 (유사한 주제의 경쟁 콘텐츠 포화 정도)
        competition_saturation = calculate_competition_saturation(video_data)
        
        # 썸네일 클릭률 (노출 대비 클릭 비율)
        thumbnail_ctr = calculate_thumbnail_ctr(video_data, other_videos_data)
        
        # 제목과 태그는 추천 생성시 사용
        title = video_data.get("snippet", {}).get("title", "")
        tags = video_data.get("snippet", {}).get("tags", [])
        description = video_data.get("snippet", {}).get("description", "")
        
        return {
            "trend_relevance": {
                "score": trend_relevance,
                "title": "트렌드 연관성",
                "description": "현재 인기 있는 주제와의 연관성",
                "recommendation": get_trend_recommendation(trend_relevance, title, tags)
            },
            "keyword_efficiency": {
                "score": keyword_efficiency,
                "title": "키워드 효율성",
                "description": "제목, 태그, 설명의 검색 최적화 정도",
                "recommendation": get_keyword_recommendation(keyword_efficiency, title, tags, description)
            },
            "target_acquisition": {
                "score": target_acquisition,
                "title": "타겟 유입율",
                "description": "새로운 시청자를 유입시키는 능력",
                "recommendation": get_target_recommendation(target_acquisition)
            },
            "viewer_retention": {
                "score": viewer_retention,
                "title": "시청자 유지율",
                "description": "시청자가 영상을 시청하는 평균 시간",
                "recommendation": get_retention_recommendation(viewer_retention)
            },
            "competition_saturation": {
                "score": competition_saturation,
                "title": "경쟁 포화도",
                "description": "유사한 주제의 경쟁 콘텐츠 포화 정도",
                "recommendation": get_competition_recommendation(competition_saturation, title)
            },
            "thumbnail_ctr": {
                "score": thumbnail_ctr,
                "title": "썸네일 클릭률",
                "description": "노출 대비 클릭 비율 추정치",
                "recommendation": get_thumbnail_recommendation(thumbnail_ctr)
            }
        }
    except Exception as e:
        print(f"인사이트 계산 중 오류 발생: {e}")
        # 오류 발생 시 기본값 반환
        return {
            "trend_relevance": {
                "score": 50,
                "title": "트렌드 연관성",
                "description": "현재 인기 있는 주제와의 연관성",
                "recommendation": "데이터 분석 중 오류가 발생했습니다. 다시 시도해주세요."
            },
            "keyword_efficiency": {
                "score": 50,
                "title": "키워드 효율성",
                "description": "제목, 태그, 설명의 검색 최적화 정도",
                "recommendation": "데이터 분석 중 오류가 발생했습니다. 다시 시도해주세요."
            },
            "target_acquisition": {
                "score": 50,
                "title": "타겟 유입율",
                "description": "새로운 시청자를 유입시키는 능력",
                "recommendation": "데이터 분석 중 오류가 발생했습니다. 다시 시도해주세요."
            },
            "viewer_retention": {
                "score": 50,
                "title": "시청자 유지율",
                "description": "시청자가 영상을 시청하는 평균 시간",
                "recommendation": "데이터 분석 중 오류가 발생했습니다. 다시 시도해주세요."
            },
            "competition_saturation": {
                "score": 50,
                "title": "경쟁 포화도",
                "description": "유사한 주제의 경쟁 콘텐츠 포화 정도",
                "recommendation": "데이터 분석 중 오류가 발생했습니다. 다시 시도해주세요."
            },
            "thumbnail_ctr": {
                "score": 50,
                "title": "썸네일 클릭률",
                "description": "노출 대비 클릭 비율 추정치",
                "recommendation": "데이터 분석 중 오류가 발생했습니다. 다시 시도해주세요."
            }
        }

def calculate_trend_relevance(video_data, other_videos_data):
    """트렌드 연관성 점수 계산"""
    # 실제로는 YouTube Trending API나 카테고리 인기도를 활용해야 함
    # 여기서는 다른 영상들과 비교한 상대적 성과를 기준으로 추정
    video_views = int(video_data.get("statistics", {}).get("viewCount", 0))
    publish_date = datetime.fromisoformat(video_data.get("snippet", {}).get("publishedAt")[:-1])
    days_since_publish = (datetime.now() - publish_date).days
    
    # 최근 영상일수록 높은 가중치
    recency_factor = max(30 - days_since_publish, 1) / 30
    
    # 일일 평균 조회수
    daily_views = video_views / max(days_since_publish, 1)
    
    # 다른 영상들의 일일 평균 조회수
    other_daily_views = []
    for video in other_videos_data:
        other_views = int(video.get("statistics", {}).get("viewCount", 0))
        other_date = datetime.fromisoformat(video.get("snippet", {}).get("publishedAt")[:-1])
        other_days = max((datetime.now() - other_date).days, 1)
        other_daily_views.append(other_views / other_days)
    
    avg_daily_views = sum(other_daily_views) / max(len(other_daily_views), 1) if other_daily_views else 1
    
    # 상대적 성과와 최신성을 고려한 점수
    relative_performance = daily_views / max(avg_daily_views, 1)
    trend_score = min(relative_performance * recency_factor * 70 + 30, 100)
    
    return round(trend_score)

def calculate_keyword_efficiency(video_data, other_videos_data):
    """키워드 효율성 점수 계산"""
    # 제목, 태그, 설명의 길이와 질을 기반으로 점수 계산
    snippet = video_data.get("snippet", {})
    title = snippet.get("title", "")
    description = snippet.get("description", "")
    tags = snippet.get("tags", [])
    
    # 기본 점수
    base_score = 50
    
    # 제목 길이 점수 (30-60자 사이가 최적)
    title_length = len(title)
    if 30 <= title_length <= 60:
        title_score = 20
    elif 20 <= title_length < 30 or 60 < title_length <= 70:
        title_score = 15
    else:
        title_score = 10
    
    # 태그 수와 다양성 점수
    tag_count = len(tags)
    if tag_count >= 15:
        tag_score = 20
    elif tag_count >= 10:
        tag_score = 15
    elif tag_count >= 5:
        tag_score = 10
    else:
        tag_score = 5
    
    # 설명 길이 점수 (200자 이상이 이상적)
    desc_length = len(description)
    if desc_length >= 300:
        desc_score = 15
    elif desc_length >= 200:
        desc_score = 10
    elif desc_length >= 100:
        desc_score = 5
    else:
        desc_score = 0
    
    # 성과를 고려한 보정
    stats = video_data.get("statistics", {})
    views = int(stats.get("viewCount", 0))
    
    # 다른 영상들의 평균 조회수 계산
    other_views = [int(v.get("statistics", {}).get("viewCount", 0)) for v in other_videos_data]
    avg_views = sum(other_views) / max(len(other_views), 1) if other_views else 1
    
    # 상대적 성과가 좋을수록 키워드 효율성이 높다고 가정
    performance_factor = min(views / max(avg_views, 1), 3)
    
    # 최종 점수 계산
    keyword_score = min(base_score + title_score + tag_score + desc_score, 100)
    adjusted_score = round(keyword_score * math.sqrt(performance_factor))
    
    return min(adjusted_score, 100)

def calculate_target_acquisition(video_data, channel_data):
    """타겟 유입율 점수 계산 (새로운 시청자 획득 용이성)"""
    stats = video_data.get("statistics", {})
    views = int(stats.get("viewCount", 0))
    
    channel_stats = channel_data.get("statistics", {})
    subscribers = int(channel_stats.get("subscriberCount", 0))
    
    # 구독자 대비 조회수 비율 (높을수록 비구독자 유입이 많을 가능성)
    view_sub_ratio = views / max(subscribers, 1)
    
    # 비율에 따른 점수 매핑
    if view_sub_ratio >= 2.0:
        base_score = 90  # 구독자의 2배 이상이면 매우 높은 점수
    elif view_sub_ratio >= 1.5:
        base_score = 80
    elif view_sub_ratio >= 1.0:
        base_score = 70
    elif view_sub_ratio >= 0.7:
        base_score = 60
    elif view_sub_ratio >= 0.5:
        base_score = 50
    elif view_sub_ratio >= 0.3:
        base_score = 40
    else:
        base_score = 30
    
    # 제목의 클릭을 유도하는 요소 보정
    title = video_data.get("snippet", {}).get("title", "")
    
    # 클릭을 유도하는 요소 체크 (숫자, 특정 키워드 등)
    clickbait_patterns = [
        r'\d+',  # 숫자
        r'(?i)how to|tutorial|guide|tips',  # 하우투, 튜토리얼, 가이드
        r'(?i)best|top|ultimate',  # 최고, 탑, 궁극의
        r'(?i)secret|trick|hack',  # 비밀, 트릭, 핵
        r'(?i)review|comparison',  # 리뷰, 비교
    ]
    
    pattern_matches = sum(1 for pattern in clickbait_patterns if re.search(pattern, title))
    clickbait_bonus = min(pattern_matches * 2, 10)  # 최대 10점 보너스
    
    return min(base_score + clickbait_bonus, 100)

def calculate_viewer_retention(video_data, other_videos_data):
    """시청자 유지율 점수 계산 (시청 지속 시간 추정)"""
    # 실제로는 YouTube Analytics API를 사용해야 하나,
    # 여기서는 좋아요 비율, 댓글 비율로 유지율 추정
    stats = video_data.get("statistics", {})
    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0))
    comments = int(stats.get("commentCount", 0))
    
    # 영상 길이 추출 (초 단위)
    duration = video_data.get("contentDetails", {}).get("duration", "PT0S")
    duration_sec = parse_duration_to_seconds(duration)
    
    # 좋아요 비율
    like_ratio = likes / max(views, 1)
    
    # 댓글 비율
    comment_ratio = comments / max(views, 1)
    
    # 영상 길이에 따른 가중치 (너무 짧거나 너무 긴 영상은 불리)
    if duration_sec <= 60:  # 1분 이하
        duration_factor = 0.7
    elif duration_sec <= 300:  # 5분 이하
        duration_factor = 1.0
    elif duration_sec <= 600:  # 10분 이하
        duration_factor = 0.9
    elif duration_sec <= 1200:  # 20분 이하
        duration_factor = 0.8
    else:  # 20분 초과
        duration_factor = 0.7
    
    # 좋아요와 댓글 비율로 유지율 추정
    estimated_retention = (like_ratio * 5000 + comment_ratio * 3000) * duration_factor
    
    # 점수화 (0-100)
    retention_score = min(30 + estimated_retention * 70, 100)
    
    return round(retention_score)

def calculate_competition_saturation(video_data):
    """경쟁 포화도 점수 계산 (유사 콘텐츠 대비 경쟁 상황)"""
    # 실제로는 YouTube Search API로 유사 콘텐츠 검색 결과 수를 활용해야 함
    # 여기서는 카테고리와 태그 기반으로 추정
    
    # 카테고리 ID (주요 카테고리별 포화도 추정)
    snippet = video_data.get("snippet", {})
    category_id = snippet.get("categoryId", "0")
    
    # 인기 카테고리는 경쟁이 더 치열함 (낮은 점수 = 높은 경쟁)
    # 카테고리별 경쟁 점수 (높을수록 경쟁이 덜함)
    category_competition = {
        "1": 40,   # 영화/애니메이션 (중간)
        "2": 30,   # 자동차 (중간-낮음)
        "10": 20,  # 음악 (매우 높음)
        "15": 35,  # 동물 (중간)
        "17": 25,  # 스포츠 (높음)
        "20": 30,  # 게임 (중간-높음)
        "22": 40,  # 블로그 (중간)
        "23": 35,  # 코미디 (중간)
        "24": 35,  # 엔터테인먼트 (중간)
        "25": 40,  # 뉴스/정치 (중간)
        "26": 50,  # 하우투/스타일 (낮음)
        "27": 45,  # 교육 (낮음-중간)
        "28": 45,  # 과학/기술 (낮음-중간)
    }
    
    base_score = category_competition.get(category_id, 35)  # 기본값 35
    
    # 태그 개수 (태그가 많을수록 경쟁이 치열한 키워드를 더 많이 타겟팅)
    tags = snippet.get("tags", [])
    tag_count = len(tags)
    
    if tag_count >= 15:
        tag_bonus = 15  # 태그를 많이 사용하면 경쟁에서 유리
    elif tag_count >= 10:
        tag_bonus = 10
    elif tag_count >= 5:
        tag_bonus = 5
    else:
        tag_bonus = 0
    
    # 틈새시장 보너스 (일반적인 태그가 아닌 특수한 태그가 많을수록 경쟁이 덜함)
    niche_bonus = 0
    common_tags = ["how to", "tutorial", "review", "best", "top", "guide", "tips", "reaction"]
    niche_count = sum(1 for tag in tags if not any(common in tag.lower() for common in common_tags))
    
    niche_bonus = min(niche_count * 2, 20)  # 최대 20점 보너스
    
    # 최종 점수
    competition_score = min(base_score + tag_bonus + niche_bonus, 100)
    
    return round(competition_score)

def calculate_thumbnail_ctr(video_data, other_videos_data):
    """썸네일 클릭률 추정 점수 계산"""
    # 실제로는 YouTube Analytics API로 CTR을 가져와야 함
    # 여기서는 조회수와 영상 게시일을 기반으로 추정
    
    stats = video_data.get("statistics", {})
    views = int(stats.get("viewCount", 0))
    publish_date = datetime.fromisoformat(video_data.get("snippet", {}).get("publishedAt")[:-1])
    days_since_publish = max((datetime.now() - publish_date).days, 1)
    
    # 일일 평균 조회수
    daily_views = views / days_since_publish
    
    # 같은 채널의 다른 영상들의 일일 평균 조회수
    other_daily_views = []
    for video in other_videos_data:
        other_views = int(video.get("statistics", {}).get("viewCount", 0))
        other_date = datetime.fromisoformat(video.get("snippet", {}).get("publishedAt")[:-1])
        other_days = max((datetime.now() - other_date).days, 1)
        other_daily_views.append(other_views / other_days)
    
    avg_daily_views = sum(other_daily_views) / max(len(other_daily_views), 1) if other_daily_views else 1
    
    # 채널 평균 대비 성과로 CTR 추정
    relative_ctr = daily_views / max(avg_daily_views, 1)
    
    # 썸네일 특성 추정 (제목 길이, 시선을 끄는 단어 등)
    title = video_data.get("snippet", {}).get("title", "")
    
    clickbait_words = ["shocking", "amazing", "unbelievable", "secret", "revealed", 
                       "you won't believe", "mind-blowing", "incredible", "surprising",
                       "충격", "놀라운", "믿을 수 없는", "비밀", "공개", "경악"]
    
    has_clickbait = any(word.lower() in title.lower() for word in clickbait_words)
    
    # CTR 점수 계산
    if relative_ctr >= 2.0:
        base_ctr = 85
    elif relative_ctr >= 1.5:
        base_ctr = 75
    elif relative_ctr >= 1.0:
        base_ctr = 65
    elif relative_ctr >= 0.7:
        base_ctr = 55
    else:
        base_ctr = 45
    
    # 제목에 시선을 끄는 단어가 있으면 보너스
    clickbait_bonus = 10 if has_clickbait else 0
    
    return min(base_ctr + clickbait_bonus, 100)

def parse_duration_to_seconds(duration):
    """ISO 8601 기간 형식을 초 단위로 변환"""
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds

# 인사이트 추천 문구
def get_trend_recommendation(score, title, tags):
    if score >= 80:
        return "현재 트렌드와 매우 잘 연관되어 있습니다. 이 주제의 후속 콘텐츠를 빠르게 제작하세요."
    elif score >= 60:
        return "트렌드와 적절히 연관되어 있지만, 관련 키워드를 더 포함시키면 좋을 것 같습니다."
    else:
        return "현재 트렌드와의 연관성이 낮습니다. 시의성 있는 주제나 키워드를 포함해보세요."

def get_keyword_recommendation(score, title, tags, description):
    if score >= 80:
        return "키워드 최적화가 매우 잘 되어있습니다. 이 패턴을 다른 영상에도 적용해보세요."
    elif score >= 60:
        if len(tags) < 10:
            return "태그를 더 추가하여 검색 노출을 높이세요. 최소 10-15개의 관련 태그를 사용하는 것이 좋습니다."
        elif len(description) < 200:
            return "설명을 더 자세하게 작성하여 SEO를 개선하세요. 키워드가 풍부한 300자 이상의 설명이 이상적입니다."
        else:
            return "제목에 주요 키워드를 더 명확하게 포함시켜 검색 노출을 개선하세요."
    else:
        return "SEO 최적화가 부족합니다. 관련 키워드를 제목, 태그, 설명에 더 포함시키세요."

def get_target_recommendation(score):
    if score >= 80:
        return "비구독자 유입이 매우 좋습니다. 이 패턴의 콘텐츠로 채널 성장을 가속화하세요."
    elif score >= 60:
        return "적절한 비구독자 유입이 있습니다. 더 많은 외부 유입을 위해 소셜 미디어 공유와 SEO를 강화하세요."
    else:
        return "주로 구독자들에게만 시청되고 있습니다. 새로운 시청자 유입을 위해 더 넓은 주제나 트렌드를 활용해보세요."

def get_retention_recommendation(score):
    if score >= 80:
        return "시청자 유지율이 매우 높습니다. 영상의 첫 30초 구성과 이야기 전개 방식을 다른 영상에도 적용하세요."
    elif score >= 60:
        return "시청자 유지율이 양호합니다. 영상 도입부를 더 강화하고 콘텐츠 전환을 부드럽게 하면 개선될 수 있습니다."
    else:
        return "시청자 유지율이 낮습니다. 영상의 첫 15초를 더 인상적으로 만들고, 불필요한 내용을 줄여 핵심에 집중하세요."

def get_competition_recommendation(score, title):
    if score >= 80:
        return "경쟁이 적은 틈새 주제를 잘 파고들었습니다. 이 영역에서 시리즈 콘텐츠를 추가로 만들어보세요."
    elif score >= 60:
        return "적정한 경쟁 환경입니다. 해당 주제에 대해 더 깊이 있는 콘텐츠로 차별화하세요."
    else:
        return "경쟁이 매우 치열한 영역입니다. 더 구체적인 틈새 주제를 찾거나 접근 방식을 독특하게 바꿔보세요."

def get_thumbnail_recommendation(score):
    if score >= 80:
        return "썸네일이 매우 효과적입니다. 이 디자인 패턴을 다른 영상에도 적용해보세요."
    elif score >= 60:
        return "썸네일이 적절히 작동하고 있습니다. 더 강한 대비와 표정, 텍스트 강조로 클릭률을 높일 수 있습니다."
    else:
        return "썸네일 효과가 낮습니다. 더 선명한 색상, 감정적인 표정, 호기심을 자극하는 요소를 추가해보세요."

@app.route("/", methods=["GET"])
def index():
    api_key_status = "설정됨" if DEFAULT_API_KEY else "설정되지 않음"
    
    return jsonify({
        "status": "success",
        "message": "YouTube Search API is running",
        "api_key_status": api_key_status,
        "endpoints": {
            "/search": {
                "method": "POST",
                "description": "YouTube 동영상 검색",
                "parameters": {
                    "api_key": "YouTube Data API 키 (선택사항, .env에 설정된 경우)",
                    "query": "검색어 (필수)"
                }
            },
            "/analyze_video": {
                "method": "POST",
                "description": "특정 동영상의 성과 분석 및 점수 계산",
                "parameters": {
                    "api_key": "YouTube Data API 키 (필수)",
                    "video_id": "동영상 ID (필수)",
                    "channel_id": "채널 ID (필수)"
                }
            }
        }
    })

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, port=port)
