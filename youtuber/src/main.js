import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/reset.css';

// Bootstrap
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.bundle';
import { BootstrapVue3 } from 'bootstrap-vue-3';
import 'bootstrap-vue-3/dist/bootstrap-vue-3.css';

// Vuetify
import { createVuetify } from 'vuetify';
import 'vuetify/styles';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';

const vuetify = createVuetify({
  components,
  directives,
});

const app = createApp(App);

// 플러그인 등록
app.use(router);
app.use(Antd);
app.use(BootstrapVue3);
app.use(vuetify);

// 글로벌 프로퍼티
app.config.globalProperties.$apiBaseUrl = '/api';
app.config.globalProperties.$youtubeApiKey = process.env.VUE_APP_YOUTUBE_API_KEY || '';

// 마운트
app.mount('#app');
