const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  
  // 개발 서버 프록시 설정 수정
  devServer: {
    host: '0.0.0.0',  // 모든 네트워크 인터페이스에서 수신
    allowedHosts: 'all',  // 모든 호스트에서의 접근 허용
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        pathRewrite: {
          '^/api': ''  // /api 경로를 빈 문자열로 바꿔 정확하게 리다이렉트
        },
        // 디버깅을 위한 로그 추가
        onProxyReq: (proxyReq, req, res) => {
          console.log(`[Proxy] ${req.method} ${req.url} -> ${proxyReq.path}`);
        }
      }
    }
  }
})
