<template>
  <div class="landing-container">
    <div class="landing-card rounded-ios shadow-ios">
      <div class="logo-container">
        <div class="text-logo">
          <span class="brand-text">YT<span class="brand-highlight">Meter</span></span>
        </div>
      </div>
      <p>2025년형 YouTube 콘텐츠 분석 플랫폼</p>
      
      <b-form @submit.prevent="submitApiKey" class="api-form">
        <b-form-group label="YouTube Data API 키" label-for="apiKey">
          <b-form-input
            id="apiKey"
            v-model="apiKey"
            type="password"
            required
            placeholder="YouTube Data API 키를 입력하세요"
            :state="apiKeyValidation"
            class="rounded-ios"
          ></b-form-input>
          <b-form-invalid-feedback :state="apiKeyValidation">
            YouTube Data API 키를 입력해주세요
          </b-form-invalid-feedback>
          <b-form-text>
            <div v-if="defaultApiKey" class="text-success mb-2">
              <i class="fas fa-check-circle"></i> 환경 변수에 설정된 API 키가 있습니다.
            </div>
            <a href="https://console.cloud.google.com/apis/credentials" target="_blank" class="ios-link">Google Cloud Console</a>에서 API 키를 생성할 수 있습니다.
          </b-form-text>
        </b-form-group>
        
        <b-button type="submit" variant="primary" size="lg" :disabled="!apiKeyValidation" class="submit-btn rounded-ios">
          <i class="fas fa-arrow-right mr-2"></i> 시작하기
        </b-button>
      </b-form>
      
      <div class="features">
        <div class="feature rounded-ios shadow-ios">
          <i class="fas fa-search-plus"></i>
          <h3>검색</h3>
          <p>YouTube 동영상을 키워드로 검색합니다.</p>
        </div>
        <div class="feature rounded-ios shadow-ios">
          <i class="fas fa-chart-bar"></i>
          <h3>분석</h3>
          <p>조회수, 좋아요 수 등의 데이터를 분석합니다.</p>
        </div>
        <div class="feature rounded-ios shadow-ios">
          <i class="fas fa-sort-amount-down"></i>
          <h3>정렬</h3>
          <p>다양한 기준으로 검색 결과를 정렬합니다.</p>
        </div>
      </div>
    </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
      apiKey: this.$youtubeApiKey || ''
    }
  },
  computed: {
    defaultApiKey() {
      return !!this.$youtubeApiKey;
    },
    apiKeyValidation() {
      return this.apiKey.length > 0 || !!this.$youtubeApiKey;
      }
    },
    methods: {
      submitApiKey() {
      // 환경 변수에 API 키가 설정되어 있거나 사용자가 입력한 경우 진행
      if (this.apiKeyValidation) {
        // 사용자가 키를 입력했다면 그것을 사용, 아니면 환경 변수의 키 사용
        const keyToUse = this.apiKey || this.$youtubeApiKey;
        
        this.$router.push({ 
          name: 'Search', 
          params: { apiKey: keyToUse } 
        });
      }
    }
  }
}
</script>

<style scoped>
.landing-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
  padding: 20px;
}

.landing-card {
  background: var(--surface-color);
  padding: 40px;
  width: 100%;
  max-width: 700px;
  text-align: center;
}

.logo-container {
  margin-bottom: 20px;
}

.text-logo {
  font-size: 3rem;
  font-weight: 600;
  margin-bottom: 20px;
  letter-spacing: -0.5px;
}

.brand-text {
  letter-spacing: -0.5px;
}

.brand-highlight {
  color: var(--primary-color);
}

p {
  font-size: 1.2rem;
  color: var(--text-secondary);
  margin-bottom: 30px;
}

.api-form {
  margin: 30px 0;
  text-align: left;
}

.submit-btn {
  width: 100%;
  margin-top: 20px;
  transition: all 0.2s;
}

.submit-btn:hover {
  transform: translateY(-2px);
}

.ios-link {
  color: var(--primary-color);
  text-decoration: none;
}

.ios-link:hover {
  text-decoration: underline;
}

.features {
  display: flex;
  justify-content: space-between;
  margin-top: 50px;
  flex-wrap: wrap;
  gap: 20px;
}

.feature {
  flex: 1;
  min-width: 150px;
  padding: 30px 20px;
  background-color: var(--surface-color);
  transition: all 0.3s;
}

.feature:hover {
  transform: translateY(-5px);
}

.feature i {
  font-size: 2rem;
  color: var(--primary-color);
  margin-bottom: 15px;
}

.feature h3 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.feature p {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .features {
    flex-direction: column;
  }
  
  .text-logo {
    font-size: 2.5rem;
  }
}
</style>
  