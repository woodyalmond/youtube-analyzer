# YouTube 콘텐츠 분석 도구 (YouTube Content Analyzer)

YouTube 영상의 성과를 분석하고 콘텐츠 제작 인사이트를 제공하는 웹 애플리케이션입니다.

## 주요 기능

- YouTube 검색 결과 분석
- 영상별 성과 지표 확인 (조회수, 좋아요, 댓글 등)
- 콘텐츠 인사이트 분석:
  - 트렌드 연관성 (현재 인기 있는 주제와의 연관성)
  - 키워드 효율성 (검색 최적화)
  - 타겟 유입율 (새로운 시청자 유입 가능성)
  - 시청자 유지율 (시청 지속 시간)
  - 경쟁 포화도 (유사 콘텐츠 경쟁 정도)
  - 썸네일 클릭률 추정
- 성과 인사이트에 따른 필터링
- 퍼포먼스 점수 기반 추천 제공

## 기술 스택

- **프론트엔드**: Vue.js, Bootstrap Vue
- **백엔드**: Python Flask API
- **데이터 소스**: YouTube Data API v3

## 설치 및 실행 방법

### 사전 준비사항
- Node.js 및 npm
- Python 3.6 이상
- YouTube Data API v3 API 키

### 프론트엔드 설치
```bash
# 저장소 클론
git clone https://github.com/your-username/youtube-analyzer.git
cd youtube-analyzer/youtuber

# 의존성 설치
npm install

# 개발 서버 실행
npm run serve
```

### 백엔드 설치
```bash
# 백엔드 디렉토리로 이동
cd ../

# 파이썬 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python main.py
```

### API 키 설정
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```
VUE_APP_YOUTUBE_API_KEY=your_youtube_api_key_here
```

## 사용 방법

1. 웹 애플리케이션에 접속합니다 (기본 주소: http://localhost:8080)
2. YouTube API 키를 입력합니다
3. 분석하고 싶은 키워드로 검색합니다
4. 검색 결과에서 영상을 선택하여 상세 분석을 확인합니다
5. 원하는 인사이트에 따라 영상을 필터링합니다

## 라이센스

MIT License

## 기여하기

1. 이 저장소를 포크합니다
2. 새 브랜치를 생성합니다: `git checkout -b feature/amazing-feature`
3. 변경사항을 커밋합니다: `git commit -m 'Add some amazing feature'`
4. 브랜치에 푸시합니다: `git push origin feature/amazing-feature`
5. Pull Request를 생성합니다
