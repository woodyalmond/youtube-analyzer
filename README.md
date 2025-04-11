# 유튜브 검색 및 분석 플랫폼

유튜브 검색 및 분석 플랫폼은 YouTube 동영상을 검색하고 성과를 분석할 수 있는 웹 애플리케이션입니다. 콘텐츠 제작자가 자신의 영상 성과를 평가하고 개선할 수 있는 인사이트를 제공합니다.

## 주요 기능

### 1. 유튜브 영상 검색
- 키워드 기반 검색으로 관련 YouTube 동영상 찾기
- 검색 결과 정렬 및 필터링
- 상세 메타데이터 표시 (조회수, 좋아요 수, 게시일, 채널명 등)

### 2. 영상 성과 분석
- 채널 성장 기여도 점수 계산
- 독립적 영상 성과도 평가
- 세부 성과 지표 시각화

### 3. 콘텐츠 제작 인사이트
- 트렌드 연관성 분석
- 키워드 효율성 평가
- 타겟 유입률 및 시청자 유지율 측정
- 경쟁 포화도 분석
- 썸네일 클릭률 추정
- 각 영역별 개선 추천 제공

## 설치 및 실행 방법

### 필수 요구사항
- Python 3.8 이상
- Node.js 14 이상
- YouTube Data API 키

### 백엔드 설정 (Flask)

1. 프로젝트 클론 또는 다운로드:
   ```bash
   git clone <repository-url>
   cd you
   ```

2. 필요한 Python 패키지 설치:
   ```bash
   pip install -r requirements.txt
   ```

3. `.env` 파일 생성 및 API 키 설정:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key_here
   FLASK_ENV=development
   PORT=5000
   ```

4. Flask 서버 실행:
   ```bash
   python run.py
   ```
   서버는 기본적으로 http://localhost:5000 에서 실행됩니다.

### 프론트엔드 설정 (Vue.js)

1. 프론트엔드 디렉토리로 이동:
   ```bash
   cd youtuber
   ```

2. 필요한 npm 패키지 설치:
   ```bash
   npm install
   ```

3. `.env` 파일 생성 (필요한 경우):
   ```
   VUE_APP_API_URL=http://localhost:5000
   VUE_APP_YOUTUBE_API_KEY=your_youtube_api_key_here
   ```

4. 개발 서버 실행:
   ```bash
   npm run serve
   ```
   프론트엔드는 기본적으로 http://localhost:8080 에서 실행됩니다.

### 동시에 실행하기

개발 편의를 위해 백엔드와 프론트엔드를 동시에 실행하는 스크립트를 제공합니다:

```bash
cd you
./start_dev.sh
```

## WSL 환경에서 실행

WSL(Windows Subsystem for Linux) 환경에서 애플리케이션을 실행하려면 다음 단계를 따르세요:

1. 코드가 WSL 환경에 클론되어 있는지 확인합니다.

2. 서버가 외부에서 접속 가능하도록 Vue와 Flask 설정이 업데이트되었습니다:
   - Flask는 모든 네트워크 인터페이스(`0.0.0.0`)에서 수신합니다.
   - Vue 개발 서버도 모든 네트워크 인터페이스에서 수신하도록 설정되었습니다.

3. 제공된 스크립트로 서버 실행:
   ```bash
   cd you
   chmod +x start_dev.sh  # 실행 권한 부여 (처음 한 번만)
   ./start_dev.sh
   ```

4. 스크립트는 Windows 호스트 IP 주소를 표시하며, 이 주소를 사용하여 Windows 브라우저에서 Vue 프론트엔드에 접근할 수 있습니다:
   - WSL 내부: http://localhost:8081/
   - Windows 브라우저: http://{Windows_호스트_IP}:8081/

5. 백엔드 API는 다음 주소로 접근할 수 있습니다:
   - WSL 내부: http://localhost:5001/
   - Windows 브라우저: http://{Windows_호스트_IP}:5001/

참고: Windows 방화벽 설정이 WSL의 포트에 대한 접근을 허용하는지 확인하세요.

## 기능 상세 설명

### 1. 유튜브 영상 검색

#### 사용 방법
1. 검색창에 키워드를 입력하고 검색 버튼을 클릭합니다.
2. 검색 결과에서 영상 정보를 확인할 수 있습니다.
3. 컬럼 헤더를 클릭하여 결과를 정렬할 수 있습니다.
4. 좌측 필터 패널에서 다양한 조건으로 결과를 필터링할 수 있습니다.

#### 기술적 구현
- 백엔드에서 YouTube Data API를 통해 검색을 수행합니다.
- 검색 결과는 JSON 형식으로 반환되며 프론트엔드에서 표시됩니다.
- API 요청 경로: `/search` (POST 메서드)

### 2. 영상 성과 분석

#### 사용 방법
1. 검색 결과에서 분석하고자 하는 영상의 "분석" 버튼을 클릭합니다.
2. 분석 결과에서 채널 성장 기여도와 독립적 영상 성과도를 확인할 수 있습니다.
3. 세부 지표를 그래프로 시각화하여 보여줍니다.

#### 기술적 구현
- 영상 ID와 채널 ID를 기반으로 상세 분석을 수행합니다.
- 다양한 지표를 계산하여 종합적인 점수를 산출합니다.
- API 요청 경로: `/analyze_video` (POST 메서드)

### 3. 콘텐츠 제작 인사이트

#### 제공하는 인사이트
- **트렌드 연관성**: 현재 인기 있는 주제와의 연관성을 분석합니다.
- **키워드 효율성**: 제목, 태그, 설명의 검색 최적화 정도를 평가합니다.
- **타겟 유입율**: 새로운 시청자를 유입시키는 능력을 측정합니다.
- **시청자 유지율**: 시청자가 영상을 시청하는 평균 시간을 추정합니다.
- **경쟁 포화도**: 유사한 주제의 경쟁 콘텐츠 포화 정도를 분석합니다.
- **썸네일 클릭률**: 노출 대비 클릭 비율을 추정합니다.

#### 기술적 구현
- 각 인사이트 영역별로 YouTube 데이터를 분석하여 점수를 계산합니다.
- 점수에 따른 맞춤형 추천 문구를 제공합니다.
- 인사이트는 시각적 대시보드로 표시됩니다.

## 문제 해결 가이드

### 1. 포트 충돌 문제 (Address already in use)

Flask 백엔드 실행 시 다음과 같은 오류가 발생할 수 있습니다:
```
OSError: [Errno 98] Address already in use
```

**해결 방법:**
```bash
# 이미 실행 중인 Flask 프로세스 종료
pkill -f "python run.py"
```

### 2. Vue CLI 실행 문제

`vue-cli-service' 명령이 인식되지 않는 경우:

**해결 방법:**
```bash
# 스크립트에서 npx를 사용하여 로컬 설치된 vue-cli-service 실행
npx vue-cli-service serve

# 또는 Vue CLI를 전역으로 설치
npm install -g @vue/cli
```

### 3. CORS 오류

프론트엔드에서 백엔드 API 호출 시 CORS 오류가 발생하는 경우:

**해결 방법:**
- Vue 프로젝트의 프록시 설정(vue.config.js)이 올바르게 구성되어 있는지 확인
- Flask 백엔드의 CORS 설정이 모든 출처를 허용하는지 확인

더 자세한 문제 해결 방법은 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) 파일을 참조하세요.

## 기술 스택

### 백엔드
- Flask (Python 웹 프레임워크)
- YouTube Data API v3
- Flask-CORS (CORS 미들웨어)

### 프론트엔드
- Vue.js 3
- Axios (HTTP 클라이언트)
- Ant Design Vue (UI 컴포넌트)
- Bootstrap Vue (UI 프레임워크)
- Vuetify (UI 컴포넌트)

## 라이센스
이 프로젝트는 MIT 라이센스 하에 배포됩니다.
