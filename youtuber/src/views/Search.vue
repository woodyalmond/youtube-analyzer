<template>
    <div class="container">
    <!-- 커스텀 툴팁 컴포넌트 -->
    <div class="custom-tooltip" :style="tooltipStyle" v-show="isTooltipVisible">
      {{ tooltipText }}
    </div>
    
    <!-- 헤더 및 검색 섹션 -->
    <div class="search-header">
      <div class="search-container">
        <h1 class="header-title">YT<span class="brand-highlight">Meter</span></h1>
        <p class="header-subtitle">2025년형 콘텐츠 분석 플랫폼으로 영상 성과를 평가하고 개선하세요</p>
        
        <b-form @submit.prevent="searchVideos" class="search-form">
          <div class="search-input-container rounded-ios shadow-ios">
            <div class="search-icon">
              <i class="fas fa-search"></i>
            </div>
          <b-form-input
            id="query"
            v-model="query"
            required
              placeholder="유튜브 영상 또는 키워드 검색"
              class="search-input"
          ></b-form-input>
            <b-button type="submit" variant="primary" class="search-button rounded-ios">
              <span>검색</span>
            </b-button>
      </div>
      </b-form>
      </div>
    </div>

    <!-- 로딩 인디케이터 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner">
      <b-spinner variant="primary" label="검색 중..."></b-spinner>
      </div>
      <p class="loading-text">영상 데이터를 불러오는 중입니다...</p>
    </div>

    <!-- 에러 메시지 -->
    <div v-if="error" class="error-message rounded-ios shadow-ios">
      <div class="error-icon">
        <i class="fas fa-exclamation-circle"></i>
      </div>
      <div class="error-text">{{ error }}</div>
    </div>
    
    <!-- 필터링 및 정렬 옵션 -->
    <div v-if="videos.length" class="results-section">
      <div class="results-header">
        <div class="results-count">
          <span class="count-number">{{ videos.length }}</span>
          <span class="count-label">개의 검색 결과</span>
        </div>
        <div class="sorting-controls">
          <b-form-select v-model="sortBy" :options="sortOptions" class="sort-select rounded-ios"></b-form-select>
          <b-form-select v-model="sortDir" :options="sortDirOptions" class="sort-direction-select rounded-ios"></b-form-select>
        </div>
      </div>
      
      <!-- 고급 필터링 섹션 -->
      <div class="filter-section rounded-ios shadow-ios">
        <div class="filter-header">
          <h5 class="filter-title">필터</h5>
          <span class="filter-badge mr-2">{{ activeFiltersCount }}개 적용 중</span>
          <span v-if="activeInsightFiltersCount > 0" class="filter-badge insight-filter-badge">
            인사이트 {{ activeInsightFiltersCount }}개
          </span>
          <button class="filter-reset btn btn-sm btn-outline-secondary" @click="resetAllFilters">
            <i class="fas fa-undo-alt mr-1"></i> 초기화
          </button>
        </div>
        
        <div class="filter-body">
          <h6 class="filter-title mb-3">인사이트 필터</h6>
          <div class="row mb-2">
            <div class="col-md-3 mb-3">
              <div class="custom-control custom-switch mb-2">
                <input type="checkbox" class="custom-control-input" id="filter-trend-relevance" 
                  v-model="filters.insightFilters.trend_relevance.enabled">
                <label class="custom-control-label" for="filter-trend-relevance">트렌드 연관성</label>
              </div>
              <div class="d-flex" v-if="filters.insightFilters.trend_relevance.enabled">
                <select class="form-control form-control-sm mr-2" 
                  v-model="filters.insightFilters.trend_relevance.operator">
                  <option v-for="op in operatorOptions" :key="op.value" :value="op.value">
                    {{ op.text }}
                  </option>
                </select>
                <input type="number" class="form-control form-control-sm" 
                  v-model.number="filters.insightFilters.trend_relevance.value" min="0" max="100">
              </div>
            </div>
            
            <div class="col-md-3 mb-3">
              <div class="custom-control custom-switch mb-2">
                <input type="checkbox" class="custom-control-input" id="filter-target-acquisition" 
                  v-model="filters.insightFilters.target_acquisition.enabled">
                <label class="custom-control-label" for="filter-target-acquisition">타겟 유입율</label>
              </div>
              <div class="d-flex" v-if="filters.insightFilters.target_acquisition.enabled">
                <select class="form-control form-control-sm mr-2" 
                  v-model="filters.insightFilters.target_acquisition.operator">
                  <option v-for="op in operatorOptions" :key="op.value" :value="op.value">
                    {{ op.text }}
                  </option>
                </select>
                <input type="number" class="form-control form-control-sm" 
                  v-model.number="filters.insightFilters.target_acquisition.value" min="0" max="100">
              </div>
            </div>
            
            <div class="col-md-3 mb-3">
              <div class="custom-control custom-switch mb-2">
                <input type="checkbox" class="custom-control-input" id="filter-viewer-retention" 
                  v-model="filters.insightFilters.viewer_retention.enabled">
                <label class="custom-control-label" for="filter-viewer-retention">시청자 유지율</label>
              </div>
              <div class="d-flex" v-if="filters.insightFilters.viewer_retention.enabled">
                <select class="form-control form-control-sm mr-2" 
                  v-model="filters.insightFilters.viewer_retention.operator">
                  <option v-for="op in operatorOptions" :key="op.value" :value="op.value">
                    {{ op.text }}
                  </option>
                </select>
                <input type="number" class="form-control form-control-sm" 
                  v-model.number="filters.insightFilters.viewer_retention.value" min="0" max="100">
              </div>
            </div>
            
            <div class="col-md-3 mb-3">
              <div class="custom-control custom-switch mb-2">
                <input type="checkbox" class="custom-control-input" id="filter-competition" 
                  v-model="filters.insightFilters.competition.enabled">
                <label class="custom-control-label" for="filter-competition">경쟁 포화도</label>
              </div>
              <div class="d-flex" v-if="filters.insightFilters.competition.enabled">
                <select class="form-control form-control-sm mr-2" 
                  v-model="filters.insightFilters.competition.operator">
                  <option v-for="op in operatorOptions" :key="op.value" :value="op.value">
                    {{ op.text }}
                  </option>
                </select>
                <input type="number" class="form-control form-control-sm" 
                  v-model.number="filters.insightFilters.competition.value" min="0" max="100">
              </div>
            </div>
          </div>
          <hr class="my-3" />
          <b-row>
            <b-col md="4">
              <div class="filter-group">
                <label class="filter-label">제목</label>
        <b-input-group>
                  <b-form-input v-model="filters.title" placeholder="제목에 포함된 키워드" class="rounded-ios"></b-form-input>
                  <b-input-group-append v-if="filters.title">
                    <b-button variant="outline-secondary" @click="filters.title = ''" class="rounded-ios">
                      <i class="fas fa-times"></i>
                    </b-button>
          </b-input-group-append>
        </b-input-group>
              </div>
            </b-col>
            <b-col md="4">
              <div class="filter-group">
                <label class="filter-label">채널명</label>
                <b-input-group>
                  <b-form-input v-model="filters.channel" placeholder="채널명" class="rounded-ios"></b-form-input>
                  <b-input-group-append v-if="filters.channel">
                    <b-button variant="outline-secondary" @click="filters.channel = ''" class="rounded-ios">
                      <i class="fas fa-times"></i>
                    </b-button>
                  </b-input-group-append>
                </b-input-group>
              </div>
            </b-col>
            <b-col md="4">
              <div class="filter-group">
                <label class="filter-label">조회수</label>
                <b-input-group>
                  <b-form-select v-model="filters.viewCount.operator" :options="operatorOptions" class="rounded-ios"></b-form-select>
                  <b-form-input v-model.number="filters.viewCount.value" type="number" min="0" class="rounded-ios"></b-form-input>
                </b-input-group>
              </div>
            </b-col>
          </b-row>
          <b-row class="mt-3">
            <b-col md="4">
              <div class="filter-group">
                <label class="filter-label">좋아요</label>
                <b-input-group>
                  <b-form-select v-model="filters.likeCount.operator" :options="operatorOptions" class="rounded-ios"></b-form-select>
                  <b-form-input v-model.number="filters.likeCount.value" type="number" min="0" class="rounded-ios"></b-form-input>
                </b-input-group>
              </div>
            </b-col>
            <b-col md="4" class="d-flex align-items-center">
              <div class="filter-toggle">
                <b-form-checkbox v-model="showOnlyAnalyzed" switch>
                  분석된 영상만 보기
                </b-form-checkbox>
              </div>
            </b-col>
          </b-row>
          <div class="row mb-3">
            <div class="col-12">
              <div class="insight-score-legend d-flex align-items-center">
                <span class="mr-3">점수 범위:</span>
                <div class="d-flex align-items-center mr-3">
                  <span class="score-indicator score-high mr-1"></span>
                  <span>높음 (80-100)</span>
                </div>
                <div class="d-flex align-items-center mr-3">
                  <span class="score-indicator score-medium mr-1"></span>
                  <span>중간 (60-79)</span>
                </div>
                <div class="d-flex align-items-center">
                  <span class="score-indicator score-low mr-1"></span>
                  <span>낮음 (0-59)</span>
                </div>
              </div>
              <small class="text-muted d-block mt-2">
                * 인사이트 필터는 분석된 영상에만 적용됩니다. 원하는 점수 범위로 영상을 필터링하세요.
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 결과 표시 (테이블 형식) -->
    <div v-if="videos.length" class="results-table-container rounded-ios shadow-ios">
      <div class="table-responsive">
        <table class="video-table">
        <thead>
          <tr>
            <th @click="changeSort('thumbnail')" class="thumbnail-column">미리보기</th>
              <th @click="changeSort('title')" :class="['title-column', getSortClass('title')]">제목</th>
              <th @click="changeSort('channelTitle')" :class="['channel-column', getSortClass('channelTitle')]">채널</th>
              <th @click="changeSort('viewCount')" :class="['metrics-column', getSortClass('viewCount')]">조회수</th>
              <th @click="changeSort('likeCount')" :class="['metrics-column', getSortClass('likeCount')]">좋아요</th>
              <th colspan="4" class="insights-header">성과 인사이트</th>
              <th class="actions-column">분석</th>
            </tr>
            <tr class="sub-header">
              <th colspan="5"></th>
              <th class="insight-sub-header" 
                @mouseenter="showInsightTooltip($event, 'trend_relevance')" 
                @mouseleave="hideTooltip()">트렌드</th>
              <th class="insight-sub-header" 
                @mouseenter="showInsightTooltip($event, 'target_acquisition')" 
                @mouseleave="hideTooltip()">유입률</th>
              <th class="insight-sub-header" 
                @mouseenter="showInsightTooltip($event, 'viewer_retention')" 
                @mouseleave="hideTooltip()">유지율</th>
              <th class="insight-sub-header" 
                @mouseenter="showInsightTooltip($event, 'competition')" 
                @mouseleave="hideTooltip()">경쟁도</th>
              <th></th>
            </tr>
        </thead>
          
        <tbody>
          <tr v-for="video in filteredVideos" :key="video.id" class="video-row">
            <td class="thumbnail-cell" @click="openVideo(video.id)">
                <div class="video-thumbnail rounded-ios overflow-hidden">
                <img :src="video.thumbnail" :alt="video.title">
                <div class="video-duration">{{ formatDuration(video.duration) }}</div>
              </div>
            </td>
              <td class="title-cell" @click="openVideo(video.id)">
                <div class="video-title">{{ video.title }}</div>
                <div class="publish-date">{{ formatDate(video.publishDate) }}</div>
              </td>
              <td class="channel-cell" @click="openVideo(video.id)">
                <div class="channel-name">{{ video.channelTitle }}</div>
              </td>
              <td class="view-count-cell" @click="openVideo(video.id)">
                <div class="metric-value">{{ formatNumber(video.viewCount) }}</div>
              </td>
              <td class="like-count-cell" @click="openVideo(video.id)">
                <div class="metric-value">{{ formatNumber(video.likeCount) }}</div>
              </td>
              
              <!-- 인사이트 점수 표시 (4개 열) -->
              <td class="insight-value-cell">
                <div v-if="video.isAnalyzing" class="analyzing-indicator">
                <b-spinner small variant="primary"></b-spinner>
              </div>
              <div v-else-if="video.analysisError" class="analysis-error">
                  <i class="fas fa-exclamation-circle error-icon"></i>
              </div>
                <div v-else-if="video.insights" class="insight-score-badge">
                  <div class="badge-value" :class="getScoreClass(video.insights.trend_relevance)">
                    {{ video.insights.trend_relevance }}
                  </div>
                  </div>
                <div v-else class="pending-analysis">
                  <div class="placeholder-badge">-</div>
                  </div>
              </td>
              
              <td class="insight-value-cell">
                <div v-if="video.isAnalyzing" class="analyzing-indicator">
                  <b-spinner small variant="primary"></b-spinner>
                  </div>
                <div v-else-if="video.analysisError" class="analysis-error">
                  <i class="fas fa-exclamation-circle error-icon"></i>
                </div>
                <div v-else-if="video.insights" class="insight-score-badge">
                  <div class="badge-value" :class="getScoreClass(video.insights.target_acquisition)">
                    {{ video.insights.target_acquisition }}
              </div>
                </div>
                <div v-else class="pending-analysis">
                  <div class="placeholder-badge">-</div>
              </div>
            </td>
              
              <td class="insight-value-cell">
                <div v-if="video.isAnalyzing" class="analyzing-indicator">
                  <b-spinner small variant="primary"></b-spinner>
                </div>
                <div v-else-if="video.analysisError" class="analysis-error">
                  <i class="fas fa-exclamation-circle error-icon"></i>
                </div>
                <div v-else-if="video.insights" class="insight-score-badge">
                  <div class="badge-value" :class="getScoreClass(video.insights.viewer_retention)">
                    {{ video.insights.viewer_retention }}
                  </div>
                </div>
                <div v-else class="pending-analysis">
                  <div class="placeholder-badge">-</div>
                </div>
              </td>
              
              <td class="insight-value-cell">
                <div v-if="video.isAnalyzing" class="analyzing-indicator">
                  <b-spinner small variant="primary"></b-spinner>
                </div>
                <div v-else-if="video.analysisError" class="analysis-error">
                  <i class="fas fa-exclamation-circle error-icon"></i>
                </div>
                <div v-else-if="video.insights" class="insight-score-badge">
                  <div class="badge-value" :class="getScoreClass(video.insights.competition)">
                    {{ video.insights.competition }}
                  </div>
                </div>
                <div v-else class="pending-analysis">
                  <div class="placeholder-badge">-</div>
                </div>
              </td>
              
              <td class="action-cell">
                <b-button size="sm" variant="primary" @click="analyzeVideo(video)" class="analyze-btn rounded-ios">
                  <i class="fas fa-chart-bar"></i>
                  <span>상세 분석</span>
              </b-button>
            </td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>
    <div v-else-if="!loading && query" class="no-results rounded-ios shadow-ios">
      <div class="no-results-icon">
        <i class="fas fa-search"></i>
      </div>
      <h3 class="no-results-title">검색 결과가 없습니다</h3>
      <p class="no-results-text">다른 키워드로 검색해 보세요</p>
    </div>
    <div v-else-if="!loading && !query" class="empty-state rounded-ios shadow-ios">
      <div class="empty-state-icon">
        <i class="fas fa-video"></i>
      </div>
      <h3 class="empty-state-title">YTMeter로 분석을 시작하세요</h3>
      <p class="empty-state-text">검색어를 입력하여 YouTube 동영상을 검색하고 분석할 수 있습니다</p>
    </div>
    
    <!-- 분석 결과 모달 -->
    <b-modal
      v-model="showAnalysisModal"
      title="영상 성과 분석"
      size="lg"
      centered
      hide-footer
      dialog-class="analysis-modal cupertino-modal"
    >
      <div v-if="analysisLoading" class="text-center p-5">
        <b-spinner variant="primary" label="분석 중..."></b-spinner>
        <p class="mt-3">영상과 채널 데이터를 분석 중입니다...</p>
      </div>
      
      <div v-else-if="analysisError" class="alert alert-danger rounded-ios" role="alert">
        {{ analysisError }}
      </div>
      
      <div v-else-if="analysisData">
        <h5>{{ analysisData.title }}</h5>
        <p class="text-muted">{{ analysisData.channel_title }} • {{ formatDate(analysisData.publish_date) }}</p>
        
        <!-- 인사이트 탭 구성 -->
        <b-tabs content-class="mt-3" fill class="cupertino-tabs">
          <b-tab title="성과 분석" active>
            <div class="row mt-4">
              <div class="col-md-6">
                <div class="score-card channel-growth rounded-ios shadow-ios">
                  <h3>채널 성장 기여도</h3>
                  <div class="score-value">{{ analysisData.channel_growth_score }}</div>
                  <div class="score-description">채널 성장에 기여한 정도</div>
                  
                  <div class="factors mt-3">
                    <div v-for="(factor, key) in analysisData.growth_factors" :key="key" class="factor-item rounded-ios">
                      <div class="factor-label">{{ factor.description }}</div>
                      <div class="factor-value">{{ factor.value }}</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6">
                <div class="score-card independent-performance rounded-ios shadow-ios">
                  <h3>독립적 영상 성과도</h3>
                  <div class="score-value">{{ analysisData.independent_performance_score }}</div>
                  <div class="score-description">구독자 기반과 독립적으로 획득한 성과</div>
                  
                  <div class="factors mt-3">
                    <div v-for="(factor, key) in analysisData.performance_factors" :key="key" class="factor-item rounded-ios">
                      <div class="factor-label">{{ factor.description }}</div>
                      <div class="factor-value">{{ factor.value }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="row mt-4">
              <div class="col-12">
                <div class="analysis-summary rounded-ios shadow-ios">
                  <h4>분석 요약</h4>
                  <p v-if="analysisData.channel_growth_score > 70">
                    이 영상은 <strong>채널 성장에 매우 큰 기여</strong>를 하고 있습니다. 구독자 증가와 채널 인지도 향상에 중요한 역할을 하고 있습니다.
                  </p>
                  <p v-else-if="analysisData.channel_growth_score > 50">
                    이 영상은 <strong>채널 성장에 긍정적인 기여</strong>를 하고 있습니다. 채널의 평균적인 성과보다 우수합니다.
                  </p>
                  <p v-else>
                    이 영상은 채널 성장 측면에서 평균 또는 평균 이하의 성과를 보이고 있습니다.
                  </p>
                  
                  <p v-if="analysisData.independent_performance_score > 70">
                    이 영상은 <strong>구독자 기반과 독립적으로 매우 우수한 성과</strong>를 내고 있습니다. 비구독자들에게 인기가 높고 알고리즘 추천이 잘 되고 있을 가능성이 높습니다.
                  </p>
                  <p v-else-if="analysisData.independent_performance_score > 50">
                    이 영상은 <strong>구독자 외 시청자들에게도 좋은 반응</strong>을 얻고 있습니다. 외부 유입이 적절히 이루어지고 있습니다.
                  </p>
                  <p v-else>
                    이 영상은 주로 구독자들에게 시청되고 있으며, 구독자 외 시청자 유입은 제한적입니다.
                  </p>
                  
                  <div class="recommendation mt-3">
                    <h5>추천 사항</h5>
                    <ul class="recommendation-list">
                      <li v-if="analysisData.channel_growth_score > analysisData.independent_performance_score">
                        이 영상은 채널 성장에 기여하고 있지만, 비구독자 유입을 늘리기 위한 노력이 필요합니다. 
                        SEO 최적화, 썸네일 개선, 영상 공유를 더 활성화하세요.
                      </li>
                      <li v-else-if="analysisData.independent_performance_score > analysisData.channel_growth_score">
                        이 영상은 외부 유입이 좋지만, 구독 전환율을 높일 필요가 있습니다. 
                        시청자들에게 구독을 유도하는 CTA를 강화하고, 관련 콘텐츠로 연결되는 엔드스크린을 추가하세요.
                      </li>
                      <li v-else>
                        이 영상의 성공 요소를 분석하여 향후 콘텐츠 제작에 반영하세요. 
                        유사한 주제나 형식으로 후속 콘텐츠를 만들어 시너지를 얻을 수 있습니다.
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </b-tab>
          
          <!-- 콘텐츠 인사이트 탭 -->
          <b-tab title="콘텐츠 인사이트">
            <div class="insight-container mt-4" v-if="analysisData && analysisData.content_insights">
              <h4 class="mb-4">콘텐츠 제작 인사이트</h4>
              
              <!-- 엑셀형 테이블 UI로 변경 -->
              <div class="table-responsive insight-table-container rounded-ios shadow-ios">
                <table class="table insight-table">
                  <thead class="thead-light">
                    <tr>
                      <th @click="sortInsightBy('title')" class="insight-column">영역</th>
                      <th @click="sortInsightBy('score')" class="score-column">점수</th>
                      <th>설명</th>
                      <th>추천사항</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(insight, key) in sortedInsights" :key="key" :class="getRowClass(insight.score)">
                      <td><strong>{{ insight.title }}</strong></td>
                      <td class="text-center">
                        <div class="insight-score-cell rounded-ios" :class="getScoreClass(insight.score)">
                        {{ insight.score }}
                      </div>
                      </td>
                      <td>{{ insight.description }}</td>
                      <td>{{ insight.recommendation }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <div class="content-strategy mt-4">
                <h4>콘텐츠 전략 제안</h4>
                <div class="strategy-card rounded-ios shadow-ios">
                  <p>
                    <strong>강점 활용:</strong> 
                    {{ getTopStrength() }} 점수가 높습니다. 이 강점을 활용하여 더 많은 콘텐츠를 제작하세요.
                  </p>
                  
                  <p>
                    <strong>개선 필요:</strong>
                    {{ getTopWeakness() }} 점수가 낮습니다. 위 추천사항에 따라 이 부분을 개선하세요.
                  </p>
                  
                  <div class="next-steps">
                    <h6>다음 콘텐츠 제작 시 주의사항:</h6>
                    <ul class="suggestion-list">
                      <li v-if="isStrong('trend_relevance')">현재의 트렌드 연관성을 유지하면서 후속 콘텐츠를 빠르게 제작하세요.</li>
                      <li v-if="isStrong('keyword_efficiency')">현재 키워드 구성을 유지하고 유사한 키워드로 확장하세요.</li>
                      <li v-if="isStrong('target_acquisition')">비구독자 유입이 좋은 콘텐츠 형식을 유지하세요.</li>
                      <li v-if="isStrong('viewer_retention')">현재 영상의 구성과 페이스를 다른 콘텐츠에도 적용하세요.</li>
                      <li v-if="isStrong('competition_saturation')">이 틈새 주제에 집중하여 경쟁이 적은 영역을 선점하세요.</li>
                      <li v-if="isStrong('thumbnail_ctr')">현재 썸네일 디자인 패턴을 유지하고 발전시키세요.</li>
                      
                      <li v-if="isWeak('trend_relevance')">더 트렌디한 주제나 키워드를 포함시켜 시의성을 높이세요.</li>
                      <li v-if="isWeak('keyword_efficiency')">제목, 태그, 설명에 검색 키워드를 더 효과적으로 포함시키세요.</li>
                      <li v-if="isWeak('target_acquisition')">더 넓은 관심사를 가진 잠재 시청자를 타겟팅하세요.</li>
                      <li v-if="isWeak('viewer_retention')">영상 도입부를 강화하고 콘텐츠를 더 역동적으로 구성하세요.</li>
                      <li v-if="isWeak('competition_saturation')">더 구체적인 틈새 주제를 찾아 경쟁을 피하세요.</li>
                      <li v-if="isWeak('thumbnail_ctr')">더 시선을 사로잡는 썸네일 디자인을 적용하세요.</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="alert alert-warning rounded-ios" role="alert">
              인사이트 데이터를 불러오는 중 오류가 발생했습니다. 다시 시도해주세요.
            </div>
          </b-tab>
        </b-tabs>
        
        <div class="text-right mt-4">
          <b-button variant="secondary" @click="showAnalysisModal = false">닫기</b-button>
        </div>
      </div>
    </b-modal>

    <!-- Add quick filter section above the videos table -->
    <div class="quick-insights-filter mb-3">
      <div class="d-flex align-items-center mb-2">
        <h6 class="mb-0 mr-3">빠른 인사이트 필터:</h6>
        <button class="btn btn-sm btn-outline-primary mr-2" @click="applyQuickFilter('trend_relevance', '>=', 80)">
          <i class="fas fa-chart-line mr-1"></i> 인기 트렌드
        </button>
        <button class="btn btn-sm btn-outline-info mr-2" @click="applyQuickFilter('target_acquisition', '>=', 80)">
          <i class="fas fa-bullseye mr-1"></i> 높은 유입률
        </button>
        <button class="btn btn-sm btn-outline-success mr-2" @click="applyQuickFilter('viewer_retention', '>=', 80)">
          <i class="fas fa-hourglass-half mr-1"></i> 높은 시청 유지율
        </button>
        <button class="btn btn-sm btn-outline-warning mr-2" @click="applyQuickFilter('competition', '<=', 50)">
          <i class="fas fa-trophy mr-1"></i> 낮은 경쟁도
        </button>
        <button class="btn btn-sm btn-outline-danger" @click="applyQuickFilter('all', '>=', 70)">
          <i class="fas fa-star mr-1"></i> 종합 점수 높음
        </button>
      </div>
      <small class="text-muted">빠른 필터를 적용하려면 분석이 완료된 영상이 있어야 합니다.</small>
    </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  
  export default {
    data() {
      return {
      apiKey: this.$route.params.apiKey || this.$youtubeApiKey,
        query: '',
        videos: [],
      loading: false,
      error: null,
      sortBy: 'viewCount',
      sortDir: 'desc',
      filter: '',
      sortOptions: [
        { value: 'viewCount', text: '조회수' },
        { value: 'likeCount', text: '좋아요 수' },
        { value: 'publishDate', text: '게시일' },
        { value: 'title', text: '제목' },
        { value: 'channelTitle', text: '채널명' },
        { value: 'duration', text: '영상 길이' }
      ],
      sortDirOptions: [
        { value: 'desc', text: '내림차순' },
        { value: 'asc', text: '오름차순' }
      ],
      // 분석 관련 데이터
      showAnalysisModal: false,
      analysisLoading: false,
      analysisError: null,
      analysisData: null,
      selectedVideo: null,
      // 채널 ID 캐시 (API 호출 최소화)
      channelIdCache: {},
      // 인사이트 정렬 관련
      insightSortBy: 'score',
      insightSortDir: 'desc',
      // 필터링 관련
      filters: {
        title: '',
        channel: '',
        viewCount: {
          operator: '>=',
          value: 0
        },
        likeCount: {
          operator: '>=',
          value: 0
        },
        // 인사이트 필터 추가
        insightFilters: {
          trend_relevance: {
            enabled: false,
            operator: '>=',
            value: 70
          },
          target_acquisition: {
            enabled: false,
            operator: '>=',
            value: 70
          },
          viewer_retention: {
            enabled: false,
            operator: '>=',
            value: 70
          },
          competition: {
            enabled: false,
            operator: '>=',
            value: 70
          }
        }
      },
      showOnlyAnalyzed: false,
      operatorOptions: [
        { value: '>=', text: '이상' },
        { value: '<=', text: '이하' },
        { value: '>', text: '초과' },
        { value: '<', text: '미만' }
      ],
      tooltipStyle: {
        position: 'fixed',
        zIndex: 10000,
        padding: '8px 12px',
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        color: 'white',
        borderRadius: '8px',
        fontSize: '0.85rem',
        lineHeight: '1.4',
        textAlign: 'left',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        maxWidth: '300px',
        top: '0px',
        left: '0px'
      },
      isTooltipVisible: false,
      tooltipText: ''
    }
  },
  mounted() {
    // 검색 결과를 가져온 후 자동으로 모든 영상의 인사이트를 가져옵니다
    this.$watch('videos', async (videos) => {
      if (videos.length > 0) {
        // 인사이트가 없는 영상만 필터링
        const videosToAnalyze = videos.filter(v => !v.insights && !v.isAnalyzing);
        
        // 각 영상의 인사이트를 병렬로 가져옵니다
        if (videosToAnalyze.length > 0) {
          // 배치 크기 설정 (API 부하 방지)
          const batchSize = 3;
          for (let i = 0; i < videosToAnalyze.length; i += batchSize) {
            const batch = videosToAnalyze.slice(i, i + batchSize);
            await Promise.all(batch.map(video => this.quickAnalyzeVideo(video)));
          }
        }
      }
    });
  },
  computed: {
    filteredVideos() {
      if (!this.videos.length) return [];
      
      return this.videos.filter(video => {
        // 제목 필터링
        if (this.filters.title && !video.title.toLowerCase().includes(this.filters.title.toLowerCase())) {
          return false;
        }
        
        // 채널명 필터링
        if (this.filters.channel && !video.channelTitle.toLowerCase().includes(this.filters.channel.toLowerCase())) {
          return false;
        }
        
        // 조회수 필터링
        if (this.filters.viewCount.value) {
          const viewCount = Number(video.viewCount);
          switch (this.filters.viewCount.operator) {
            case '>=':
              if (viewCount < this.filters.viewCount.value) return false;
              break;
            case '<=':
              if (viewCount > this.filters.viewCount.value) return false;
              break;
            case '>':
              if (viewCount <= this.filters.viewCount.value) return false;
              break;
            case '<':
              if (viewCount >= this.filters.viewCount.value) return false;
              break;
          }
        }
        
        // 좋아요 필터링
        if (this.filters.likeCount.value) {
          const likeCount = Number(video.likeCount);
          switch (this.filters.likeCount.operator) {
            case '>=':
              if (likeCount < this.filters.likeCount.value) return false;
              break;
            case '<=':
              if (likeCount > this.filters.likeCount.value) return false;
              break;
            case '>':
              if (likeCount <= this.filters.likeCount.value) return false;
              break;
            case '<':
              if (likeCount >= this.filters.likeCount.value) return false;
              break;
          }
        }
        
        // 인사이트 필터링 - 분석된 영상만 대상으로 함
        if (video.insights) {
          // 트렌드 연관성 필터링
          if (this.filters.insightFilters.trend_relevance.enabled) {
            const score = video.insights.trend_relevance;
            const filter = this.filters.insightFilters.trend_relevance;
            
            if (!this.meetsScoreFilter(score, filter.operator, filter.value)) {
              return false;
            }
          }
          
          // 타겟 유입율 필터링
          if (this.filters.insightFilters.target_acquisition.enabled) {
            const score = video.insights.target_acquisition;
            const filter = this.filters.insightFilters.target_acquisition;
            
            if (!this.meetsScoreFilter(score, filter.operator, filter.value)) {
              return false;
            }
          }
          
          // 시청자 유지율 필터링
          if (this.filters.insightFilters.viewer_retention.enabled) {
            const score = video.insights.viewer_retention;
            const filter = this.filters.insightFilters.viewer_retention;
            
            if (!this.meetsScoreFilter(score, filter.operator, filter.value)) {
              return false;
            }
          }
          
          // 경쟁 포화도 필터링
          if (this.filters.insightFilters.competition.enabled) {
            const score = video.insights.competition;
            const filter = this.filters.insightFilters.competition;
            
            if (!this.meetsScoreFilter(score, filter.operator, filter.value)) {
              return false;
            }
          }
        } else {
          // 인사이트 필터가 하나라도 활성화되어 있다면 인사이트가 없는 영상은 제외
          if (
            this.filters.insightFilters.trend_relevance.enabled ||
            this.filters.insightFilters.target_acquisition.enabled ||
            this.filters.insightFilters.viewer_retention.enabled ||
            this.filters.insightFilters.competition.enabled
          ) {
            return false;
          }
        }
        
        // 분석된 영상만 보기
        if (this.showOnlyAnalyzed && !video.insights) {
          return false;
        }
        
        return true;
      }).sort((a, b) => {
        let aValue = a[this.sortBy];
        let bValue = b[this.sortBy];
        
        // 날짜 처리
        if (this.sortBy === 'publishDate') {
          aValue = new Date(aValue);
          bValue = new Date(bValue);
        }
        
        // 문자열 처리
        if (this.sortBy === 'title' || this.sortBy === 'channelTitle') {
          aValue = String(aValue).toLowerCase();
          bValue = String(bValue).toLowerCase();
        }
        
        // 숫자 처리
        if (this.sortBy === 'viewCount' || this.sortBy === 'likeCount') {
          aValue = Number(aValue);
          bValue = Number(bValue);
        }
        
        if (this.sortDir === 'asc') {
          return aValue > bValue ? 1 : -1;
        } else {
          return aValue < bValue ? 1 : -1;
        }
      });
    },
    sortedInsights() {
      if (!this.analysisData || !this.analysisData.content_insights) return [];
      
      // 점수가 높은 순서대로 정렬
      const insights = Object.entries(this.analysisData.content_insights).map(([key, value]) => ({
        key,
        ...value
      }));
      
      return insights.sort((a, b) => {
        const aValue = a[this.insightSortBy];
        const bValue = b[this.insightSortBy];
        
        if (this.insightSortDir === 'asc') {
          if (this.insightSortBy === 'title') {
            return aValue.localeCompare(bValue);
          }
          return aValue - bValue;
        } else {
          if (this.insightSortBy === 'title') {
            return bValue.localeCompare(aValue);
          }
          return bValue - aValue;
        }
      });
    },
    activeFiltersCount() {
      let count = 0;
      
      // 제목 필터
      if (this.filters.title) count++;
      
      // 채널명 필터
      if (this.filters.channel) count++;
      
      // 조회수 필터
      if (this.filters.viewCount.value > 0) count++;
      
      // 좋아요 필터
      if (this.filters.likeCount.value > 0) count++;
      
      // 인사이트 필터
      if (this.filters.insightFilters.trend_relevance.enabled) count++;
      if (this.filters.insightFilters.target_acquisition.enabled) count++;
      if (this.filters.insightFilters.viewer_retention.enabled) count++;
      if (this.filters.insightFilters.competition.enabled) count++;
      
      // 분석된 영상 필터
      if (this.showOnlyAnalyzed) count++;
      
      return count;
    },
    activeInsightFiltersCount() {
      return Object.values(this.filters.insightFilters)
        .filter(filter => filter.enabled)
        .length;
    }
  },
  methods: {
    async searchVideos() {
      if (!this.query.trim()) return;
      
      this.loading = true;
      this.error = null;
      
      // 검색 시 필터링 초기화
      this.resetAllFilters();
      
      try {
        const apiUrl = `${this.$apiBaseUrl}/search`;
        console.log('검색 API 요청 URL:', apiUrl);
        console.log('검색 API 요청 데이터:', {
          query: this.query,
          api_key: this.apiKey ? '설정됨' : '설정되지 않음'
        });
        
        // JSON 형식으로 요청
        const response = await axios.post(`${this.$apiBaseUrl}/search`, {
          api_key: this.apiKey,
          query: this.query
        });
        
        console.log('검색 API 응답 데이터:', response.data);
        
        // 각 비디오에 인사이트 관련 속성 초기화
        this.videos = response.data.map(video => ({
          ...video,
          isAnalyzing: false,
          analysisError: null,
          insights: null
        }));
        
        // 검색 결과를 화면에 표시한 후, 자동으로 첫 5개 영상의 인사이트를 가져옵니다
        if (this.videos.length > 0) {
          const initialBatch = this.videos.slice(0, 5);
          for (const video of initialBatch) {
            this.quickAnalyzeVideo(video);
            // API 부하 방지를 위한 짧은 지연
            await new Promise(resolve => setTimeout(resolve, 300));
          }
        }
      } catch (error) {
        console.error('Error searching videos:', error);
        if (error.response) {
          // 서버가 응답을 반환한 경우
          console.error('API 응답 오류:', error.response.data);
          console.error('상태 코드:', error.response.status);
          this.error = `검색 API 호출 중 오류 발생 (${error.response.status}): ${JSON.stringify(error.response.data)}`;
        } else if (error.request) {
          // 요청은 보냈지만 응답을 받지 못한 경우
          console.error('응답 없음:', error.request);
          this.error = 'API 서버가 응답하지 않습니다. 서버가 실행 중인지 확인하세요.';
        } else {
          // 요청 설정 중 오류가 발생한 경우
          this.error = `검색 API 호출 중 오류가 발생했습니다: ${error.message}`;
        }
      } finally {
        this.loading = false;
      }
    },
    clearResults() {
      this.videos = [];
      this.filter = '';
    },
    openVideo(videoId) {
      window.open(`https://www.youtube.com/watch?v=${videoId}`, '_blank');
    },
    formatDuration(duration) {
      if (!duration) return '00:00';
      
      // ISO 8601 형식의 기간 문자열을 파싱
      const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
      if (!match) return '00:00';
      
      const hours = parseInt(match[1] || 0);
      const minutes = parseInt(match[2] || 0);
      const seconds = parseInt(match[3] || 0);
      
      if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
      } else {
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
      }
    },
    formatNumber(num) {
      if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
      } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
      } else {
        return num.toString();
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    changeSort(column) {
      if (this.sortBy === column) {
        // 같은 열을 다시 클릭하면 정렬 방향 전환
        this.sortDir = this.sortDir === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortBy = column;
        // 새로운 열 선택 시 기본 정렬은 내림차순(조회수/좋아요), 오름차순(이름/날짜)
        if (['viewCount', 'likeCount'].includes(column)) {
          this.sortDir = 'desc';
        } else {
          this.sortDir = 'asc';
        }
      }
    },
    getSortClass(column) {
      return {
        'sortable': true,
        'sort-asc': this.sortBy === column && this.sortDir === 'asc',
        'sort-desc': this.sortBy === column && this.sortDir === 'desc'
      };
    },
    // 영상 분석 기능
    async analyzeVideo(video) {
      this.showAnalysisModal = true;
      this.analysisLoading = true;
      this.analysisError = null;
      this.analysisData = null;
      this.selectedVideo = video;
      
      try {
        // 이미 분석된 데이터가 있는 경우 재사용
        if (video.insights && video.insights.fullData) {
          this.analysisData = video.insights.fullData;
          this.analysisLoading = false;
          return;
        }
        
        // 채널 ID가 캐시에 있는지 확인
        let channelId = this.channelIdCache[video.id];
        
        // 채널 ID가 없으면 API로 가져오기
        if (!channelId) {
          try {
          const videoInfoResponse = await axios.get(
            `https://www.googleapis.com/youtube/v3/videos?part=snippet&id=${video.id}&key=${this.apiKey}`
          );
          
          channelId = videoInfoResponse.data.items[0].snippet.channelId;
          this.channelIdCache[video.id] = channelId;
          } catch (error) {
            console.error('Error getting channel ID:', error);
            throw new Error('채널 정보를 가져오는 중 오류가 발생했습니다.');
          }
        }
        
        // 분석 API 호출
        try {
          console.log('상세 분석 API 요청 데이터:', {
            video_id: video.id,
            channel_id: channelId
          });
          
          // JSON 형식으로 요청
          const response = await axios.post(`${this.$apiBaseUrl}/analyze_video`, {
            api_key: this.apiKey,
            video_id: video.id,
            channel_id: channelId
          });
          
          console.log('상세 분석 API 응답 데이터:', response.data);
          
          const analysisData = response.data;
          this.analysisData = analysisData;
          
          if (!analysisData) {
            throw new Error('API 응답이 비어있습니다.');
          }
          
          if (!analysisData.content_insights) {
            console.error('인사이트 데이터 구조 오류:', analysisData);
            throw new Error('인사이트 데이터 구조가 유효하지 않습니다.');
          }
        
        // 아직 인사이트가 없다면 결과 저장
        if (!video.insights) {
          video.insights = {
              trend_relevance: analysisData.content_insights.trend_relevance.score,
              target_acquisition: analysisData.content_insights.target_acquisition.score,
              viewer_retention: analysisData.content_insights.viewer_retention.score,
              competition: analysisData.content_insights.competition_saturation.score,
              fullData: analysisData
            };
          }
        } catch (error) {
          console.error('Error calling analysis API:', error);
          if (error.response) {
            // 서버가 응답을 반환한 경우
            console.error('API 응답 오류:', error.response.data);
            console.error('상태 코드:', error.response.status);
            throw new Error(`분석 API 호출 중 오류 발생 (${error.response.status}): ${JSON.stringify(error.response.data)}`);
          } else if (error.request) {
            // 요청은 보냈지만 응답을 받지 못한 경우
            console.error('응답 없음:', error.request);
            throw new Error('API 서버가 응답하지 않습니다. 서버가 실행 중인지 확인하세요.');
          } else {
            // 요청 설정 중 오류가 발생한 경우
            throw new Error(`분석 API 호출 중 오류가 발생했습니다: ${error.message}`);
          }
        }
      } catch (error) {
        console.error('Error analyzing video:', error);
        this.analysisError = error.message || '영상 분석 중 오류가 발생했습니다. API 키를 확인하거나 나중에 다시 시도하세요.';
      } finally {
        this.analysisLoading = false;
      }
    },
    // 점수에 따른 클래스 반환
    getScoreClass(score) {
      if (score >= 80) return 'score-high';
      if (score >= 60) return 'score-medium';
      return 'score-low';
    },
    
    // 점수에 따른 색상 반환
    getScoreColor(score) {
      if (score >= 80) return '#4caf50'; // 높은 점수 - 녹색
      if (score >= 60) return '#2196f3'; // 중간 점수 - 파란색
      return '#ff9800'; // 낮은 점수 - 주황색
    },
    
    // 가장 높은 점수의 인사이트 영역 반환
    getTopStrength() {
      if (!this.sortedInsights.length) return '';
      const top = this.sortedInsights[0];
      return top.title;
    },
    
    // 가장 낮은 점수의 인사이트 영역 반환
    getTopWeakness() {
      if (!this.sortedInsights.length) return '';
      const bottom = [...this.sortedInsights].sort((a, b) => a.score - b.score)[0];
      return bottom.title;
    },
    
    // 특정 영역의 점수가 높은지 확인
    isStrong(key) {
      if (!this.analysisData || !this.analysisData.content_insights) return false;
      const insight = this.analysisData.content_insights[key];
      return insight && insight.score >= 70;
    },
    
    // 특정 영역의 점수가 낮은지 확인
    isWeak(key) {
      if (!this.analysisData || !this.analysisData.content_insights) return false;
      const insight = this.analysisData.content_insights[key];
      return insight && insight.score < 60;
    },
    async quickAnalyzeVideo(video) {
      // 이미 분석 진행 중이면 중복 요청 방지
      if (video.isAnalyzing) return;
      
      // 분석 시작 상태로 설정
      video.isAnalyzing = true;
      video.analysisError = null;
      
      try {
        // 채널 ID가 캐시에 있는지 확인
        let channelId = this.channelIdCache[video.id];
        
        // 채널 ID가 없으면 API로 가져오기
        if (!channelId) {
          try {
          const videoInfoResponse = await axios.get(
            `https://www.googleapis.com/youtube/v3/videos?part=snippet&id=${video.id}&key=${this.apiKey}`
          );
          
          channelId = videoInfoResponse.data.items[0].snippet.channelId;
          this.channelIdCache[video.id] = channelId; // 캐시에 저장
          } catch (error) {
            console.error('Error getting channel ID:', error);
            throw new Error('채널 정보를 가져오는 중 오류가 발생했습니다.');
          }
        }
        
        // 분석 API 호출
        try {
          console.log('빠른 분석 API 요청 데이터:', {
            video_id: video.id,
            channel_id: channelId
          });
          
          // JSON 형식으로 요청
          const response = await axios.post(`${this.$apiBaseUrl}/analyze_video`, {
            api_key: this.apiKey,
            video_id: video.id,
            channel_id: channelId
          });
          
          console.log('빠른 분석 API 응답 데이터:', response.data);
          
        const analysisData = response.data;
          
          if (!analysisData) {
            throw new Error('API 응답이 비어있습니다.');
          }
          
          if (!analysisData.content_insights) {
            console.error('인사이트 데이터 구조 오류:', analysisData);
            throw new Error('인사이트 데이터 구조가 유효하지 않습니다.');
          }
        
        // 테이블에 표시할 핵심 인사이트 데이터 추출
        video.insights = {
          trend_relevance: analysisData.content_insights.trend_relevance.score,
          target_acquisition: analysisData.content_insights.target_acquisition.score,
          viewer_retention: analysisData.content_insights.viewer_retention.score,
          competition: analysisData.content_insights.competition_saturation.score,
          // 전체 데이터 저장 (상세 분석 모달에서 사용)
          fullData: analysisData
        };
        } catch (error) {
          console.error('Error calling analysis API:', error);
          if (error.response) {
            // 서버가 응답을 반환한 경우
            console.error('API 응답 오류:', error.response.data);
            console.error('상태 코드:', error.response.status);
            throw new Error(`분석 API 호출 중 오류 발생 (${error.response.status}): ${JSON.stringify(error.response.data)}`);
          } else if (error.request) {
            // 요청은 보냈지만 응답을 받지 못한 경우
            console.error('응답 없음:', error.request);
            throw new Error('API 서버가 응답하지 않습니다. 서버가 실행 중인지 확인하세요.');
          } else {
            // 요청 설정 중 오류가 발생한 경우
            throw new Error(`분석 API 호출 중 오류가 발생했습니다: ${error.message}`);
          }
        }
      } catch (error) {
        console.error('Error analyzing video:', error);
        video.analysisError = error.message || '분석 오류';
      } finally {
        video.isAnalyzing = false;
      }
    },
    // 점수에 따른 행 클래스 반환
    getRowClass(score) {
      if (score >= 80) return 'table-success';
      if (score >= 60) return 'table-info';
      return 'table-warning';
    },
    // 인사이트 정렬 방식 변경
    sortInsightBy(column) {
      if (this.insightSortBy === column) {
        this.insightSortDir = this.insightSortDir === 'asc' ? 'desc' : 'asc';
      } else {
        this.insightSortBy = column;
        this.insightSortDir = 'desc';
      }
    },
    resetAllFilters() {
      this.filters = {
        title: '',
        channel: '',
        viewCount: {
          operator: '>=',
          value: 0
        },
        likeCount: {
          operator: '>=',
          value: 0
        },
        insightFilters: {
          trend_relevance: {
            enabled: false,
            operator: '>=',
            value: 70
          },
          target_acquisition: {
            enabled: false,
            operator: '>=',
            value: 70
          },
          viewer_retention: {
            enabled: false,
            operator: '>=',
            value: 70
          },
          competition: {
            enabled: false,
            operator: '>=',
            value: 70
          }
        }
      };
      this.showOnlyAnalyzed = false;
    },
    meetsScoreFilter(score, operator, value) {
      switch (operator) {
        case '>=':
          return score >= value;
        case '<=':
          return score <= value;
        case '>':
          return score > value;
        case '<':
          return score < value;
        default:
          return true;
      }
    },
    getBadgeTooltip(key) {
      // 각 인사이트별 툴팁 텍스트 반환
      const tooltips = {
        trend_relevance: '현재 트렌드와의 연관성 및 시의성 점수입니다. 현재 인기 있는 주제와 얼마나 관련이 있는지를 나타냅니다.',
        target_acquisition: '구독자 외 신규 시청자 유입률 점수입니다. 비구독자들에게 얼마나 노출되고 시청되는지를 나타냅니다.',
        viewer_retention: '시청자 유지율 점수입니다. 시청자들이 영상을 얼마나 오래 시청하는지를 나타냅니다.',
        competition: '콘텐츠 경쟁도 점수입니다. 유사한 콘텐츠와 비교하여 얼마나 경쟁력 있는지를 나타냅니다.'
      };
      
      return tooltips[key] || '정보가 없습니다.';
    },
    displayTooltip(text) {
      this.tooltipText = text;
      this.isTooltipVisible = true;
    },
    showInsightTooltip(event, key) {
      const tooltipText = this.getBadgeTooltip(key);
      this.tooltipText = tooltipText;
      
      // 요소 위치 기반으로 툴팁 배치
      const element = event.target;
      const rect = element.getBoundingClientRect();
      
      // 툴팁을 헤더 위에 표시 (상단 중앙)
      this.tooltipStyle = {
        ...this.tooltipStyle,
        top: `${rect.top - 10}px`,
        left: `${rect.left + (rect.width / 2)}px`,
        transform: 'translate(-50%, -100%)'
      };
      
      this.isTooltipVisible = true;
    },
    hideTooltip() {
      this.isTooltipVisible = false;
    },
    applyQuickFilter(insightType, operator, value) {
      // 모든 필터 초기화
      this.resetAllFilters();
      
      // 특정 필터 적용
      if (insightType === 'all') {
        // 모든 인사이트가 기준 점수 이상인 영상 필터링
        Object.keys(this.filters.insightFilters).forEach(key => {
          this.filters.insightFilters[key].enabled = true;
          this.filters.insightFilters[key].operator = operator;
          this.filters.insightFilters[key].value = value;
        });
      } else {
        // 특정 인사이트만 필터링
        this.filters.insightFilters[insightType].enabled = true;
        this.filters.insightFilters[insightType].operator = operator;
        this.filters.insightFilters[insightType].value = value;
      }
      
      // 분석된 영상만 보기 활성화
      this.showOnlyAnalyzed = true;
    }
  }
}
</script>

<style scoped>
/* Cupertino Design System - iOS Style */

.header-title {
  font-weight: 600;
  font-size: 2rem;
  margin-bottom: 0.5rem;
  letter-spacing: -0.5px;
}

.brand-highlight {
  color: var(--primary-color);
}

.header-subtitle {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

.search-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 2rem 0;
}

.search-input-container {
  display: flex;
  align-items: center;
  background-color: var(--surface-color);
  border: 1px solid var(--border-color);
  max-width: 700px;
  margin: 0 auto;
  transition: box-shadow 0.2s, transform 0.2s;
}

.search-input-container:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.15);
}

.search-icon {
  padding: 0 1rem;
  color: var(--text-secondary);
}

.search-input {
  flex: 1;
  border: none;
  padding: 0.75rem 0;
  background: transparent;
}

.search-input:focus {
  box-shadow: none;
}

.search-button {
  padding: 0.75rem 1.25rem;
  font-weight: 500;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}

/* Results section */
.results-section {
  margin-bottom: 1.5rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.results-count {
  display: flex;
  align-items: baseline;
}

.count-number {
  font-size: 1.5rem;
  font-weight: 600;
  margin-right: 0.5rem;
  color: var(--primary-color);
}

.count-label {
  color: var(--text-secondary);
}

.sorting-controls {
  display: flex;
  gap: 0.75rem;
}

.sort-select, .sort-direction-select {
  border: 1px solid var(--border-color);
  background-color: var(--surface-color);
}

/* Filter section */
.filter-section {
  background-color: var(--surface-color);
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}

.filter-header {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.filter-title {
  font-weight: 600;
  margin-bottom: 0;
  margin-right: 0.75rem;
}

.filter-badge {
  background-color: var(--primary-color);
  color: white;
  border-radius: 12px;
  padding: 0.15rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.filter-reset {
  margin-left: auto;
}

.filter-label {
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

/* Video Table */
.results-table-container {
  background-color: var(--surface-color);
  overflow: hidden;
  margin-bottom: 2rem;
}

.video-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.video-table thead {
  background-color: rgba(0, 0, 0, 0.02);
}

.video-table th {
  padding: 1rem;
  font-weight: 600;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  text-align: center;
}

.video-table th.title-column,
.video-table th.channel-column {
  text-align: left;
}

.video-table th:hover {
  color: var(--primary-color);
}

.video-table .sub-header th {
  padding: 0.5rem;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.8rem;
  font-weight: 500;
}

.insight-sub-header {
  color: var(--text-secondary);
  cursor: help;
  position: relative;
  padding-bottom: 2px;
  position: relative;
}

.insight-sub-header::after {
  content: "";
  display: block;
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 12px;
  height: 1px;
  background-color: var(--text-secondary);
  opacity: 0.7;
  transition: width 0.2s;
}

.insight-sub-header:hover {
  color: var(--primary-color);
}

.insight-sub-header:hover::after {
  background-color: var(--primary-color);
  width: 20px;
}

/* 인사이트 헤더에 화살표 추가 */
.insight-sub-header::before {
  content: "?";
  display: inline-block;
  font-size: 10px;
  width: 14px;
  height: 14px;
  line-height: 14px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.1);
  color: var(--text-secondary);
  margin-right: 4px;
  text-align: center;
  opacity: 0.6;
  transition: all 0.2s;
}

.insight-sub-header:hover::before {
  background-color: var(--primary-color);
  color: white;
  opacity: 1;
}

.insights-header {
  text-align: center;
  color: var(--text-color);
}

.video-row {
  transition: background-color 0.2s;
}

.video-row:hover {
  background-color: rgba(0, 122, 255, 0.05);
}

.video-table td {
  padding: 0.75rem 0.5rem;
  border-bottom: 1px solid var(--border-color);
  text-align: center;
  vertical-align: middle;
}

.video-table td.title-cell,
.video-table td.channel-cell {
  text-align: left;
}

.insight-value-cell {
  padding: 0.75rem 0.25rem !important;
  width: 50px;
}

.badge-value {
  display: inline-block;
  font-weight: 600;
  min-width: 36px;
  height: 36px;
  line-height: 36px;
  text-align: center;
  border-radius: 18px;
  margin: 0 auto;
  font-size: 0.9rem;
  cursor: help;
}

.placeholder-badge {
  display: inline-block;
  width: 36px;
  height: 36px;
  line-height: 36px;
  text-align: center;
  border-radius: 18px;
  background-color: var(--background-color);
  color: var(--text-secondary);
  font-size: 0.9rem;
  opacity: 0.5;
}

.analyzing-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 36px;
}

.analysis-error {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 36px;
  color: var(--ios-red);
}

.video-thumbnail {
  position: relative;
  width: 120px;
  height: 68px;
  cursor: pointer;
}

.video-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-duration {
  position: absolute;
  bottom: 5px;
  right: 5px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.video-title {
  font-weight: 500;
  margin-bottom: 0.25rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  cursor: pointer;
}

.publish-date {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.channel-name {
  font-weight: 500;
}

.metric-value {
  font-weight: 500;
}

.score-high {
  background-color: rgba(52, 199, 89, 0.1);
  border: 1px solid var(--secondary-color);
  color: var(--secondary-color);
}

.score-medium {
  background-color: rgba(255, 149, 0, 0.1);
  border: 1px solid var(--ios-orange);
  color: var(--ios-orange);
}

.score-low {
  background-color: rgba(255, 59, 48, 0.1);
  border: 1px solid var(--ios-red);
  color: var(--ios-red);
}

/* Analysis Modal */
.cupertino-modal .modal-content {
  border-radius: 12px;
  border: none;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15);
}

.cupertino-modal .modal-header {
  border-bottom: 1px solid var(--border-color);
  padding: 1.25rem 1.5rem;
}

.cupertino-modal .modal-title {
  font-weight: 600;
  font-size: 1.3rem;
}

.cupertino-modal .close {
  background-color: var(--background-color);
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 1;
}

.cupertino-modal .close span {
  color: var(--text-secondary);
}

.cupertino-modal .modal-body {
  padding: 1.5rem;
}

/* Cupertino-style tabs */
.cupertino-tabs .nav-tabs {
  border-bottom: 1px solid var(--border-color);
}

.cupertino-tabs .nav-link {
  color: var(--text-secondary);
  font-weight: 500;
  padding: 0.75rem 1.25rem;
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
}

.cupertino-tabs .nav-link.active {
  color: var(--primary-color);
  background: transparent;
  border-bottom: 2px solid var(--primary-color);
}

.cupertino-tabs .tab-content {
  padding-top: 1.5rem;
}

/* Score cards */
.score-card {
  background-color: var(--surface-color);
  padding: 1.5rem;
  height: 100%;
}

.score-card h3 {
  font-weight: 600;
  font-size: 1.25rem;
  margin-bottom: 1rem;
}

.score-value {
  font-size: 3rem;
  font-weight: 700;
  color: var(--primary-color);
}

.score-description {
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.channel-growth .score-value {
  color: var(--ios-teal);
}

.independent-performance .score-value {
  color: var(--ios-purple);
}

.factors {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.factor-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background-color: var(--background-color);
}

.factor-label {
  font-weight: 500;
  font-size: 0.9rem;
}

.factor-value {
  font-weight: 600;
}

/* Analysis summary */
.analysis-summary {
  background-color: var(--surface-color);
  padding: 1.5rem;
}

.analysis-summary h4 {
  font-weight: 600;
  margin-bottom: 1rem;
}

.recommendation h5 {
  font-weight: 600;
  margin-top: 1rem;
}

.recommendation-list {
  padding-left: 1.25rem;
}

.recommendation-list li {
  margin-bottom: 0.75rem;
  line-height: 1.5;
}

/* Insight table */
.insight-table-container {
  background-color: var(--surface-color);
  max-height: 400px;
  overflow-y: auto;
}

.insight-table th {
  position: sticky;
  top: 0;
  background-color: var(--background-color);
  z-index: 1;
  padding: 1rem;
  font-weight: 600;
}

.insight-score-cell {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  min-width: 40px;
  text-align: center;
  font-weight: 600;
}

.insight-table td {
  padding: 0.75rem 1rem;
  vertical-align: middle;
}

/* Strategy card */
.strategy-card {
  background-color: var(--surface-color);
  padding: 1.5rem;
}

.next-steps {
  margin-top: 1.25rem;
}

.next-steps h6 {
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.suggestion-list {
  padding-left: 1.25rem;
}

.suggestion-list li {
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

/* No results & empty states */
.no-results, .empty-state {
  text-align: center;
  padding: 3rem 1rem;
  background-color: var(--surface-color);
}

.no-results-icon, .empty-state-icon {
  font-size: 3rem;
  color: var(--text-secondary);
  opacity: 0.5;
  margin-bottom: 1.5rem;
}

.no-results-title, .empty-state-title {
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.no-results-text, .empty-state-text {
  color: var(--text-secondary);
  max-width: 500px;
  margin: 0 auto;
}

/* Responsive adjustments */
@media (max-width: 767px) {
  .search-header {
    padding: 1.5rem 0;
  }
  
  .header-title {
    font-size: 1.75rem;
  }
  
  .results-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .sorting-controls {
    width: 100%;
  }
  
  .sort-select, .sort-direction-select {
    flex: 1;
  }
  
  .score-card {
    margin-bottom: 1.5rem;
  }
}

/* 툴팁 스타일 커스터마이징 */
:deep(.tooltip) {
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display', 'Helvetica Neue', sans-serif;
  z-index: 10000;
}

:deep(.tooltip-inner) {
  max-width: 300px;
  padding: 8px 12px;
  background-color: rgba(0, 0, 0, 0.8);
  border-radius: 8px;
  font-size: 0.85rem;
  line-height: 1.4;
  text-align: left;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

:deep(.tooltip .arrow::before) {
  border-top-color: rgba(0, 0, 0, 0.8);
}

.insight-badge {
  cursor: help;
  position: relative;
}

/* 테이블 내 컬럼 너비 조정 */
.thumbnail-column {
  width: 140px;
}

.title-column {
  width: 30%;
}

.channel-column {
  width: 15%;
}

.metrics-column {
  width: 10%;
}

.insight-value-cell {
  padding: 0.75rem 0.25rem !important;
  width: 50px;
}

.action-cell {
    width: 120px;
  }
  
/* 인사이트 분석 버튼 스타일 */
.analyze-btn {
    width: 100px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
}

@media (max-width: 1200px) {
  .badge-value {
    min-width: 32px;
    height: 32px;
    line-height: 32px;
    font-size: 0.8rem;
  }
  
  .insight-value-cell {
    padding: 0.5rem 0.1rem !important;
  }
}

.custom-tooltip {
  position: fixed;
  z-index: 10000 !important;
  background-color: rgba(0, 0, 0, 0.85);
  color: white;
  padding: 10px 15px;
  border-radius: 10px;
  font-size: 0.85rem;
  line-height: 1.5;
  max-width: 300px;
  pointer-events: none;
  transition: opacity 0.2s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.custom-tooltip::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  border-width: 8px 8px 0;
  border-style: solid;
  border-color: rgba(0, 0, 0, 0.85) transparent transparent;
}

.score-indicator {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

.score-high {
  background-color: #4caf50;
}

.score-medium {
  background-color: #2196f3;
}

.score-low {
  background-color: #ff9800;
}

.insight-score-legend {
  font-size: 0.85rem;
}

.insight-filter-badge {
  background-color: #9c27b0;
}
</style>

  