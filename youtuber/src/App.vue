<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg">
      <div class="container">
        <router-link class="navbar-brand" to="/">
          <span class="brand-text">YT<span class="brand-highlight">Meter</span></span>
        </router-link>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
      </div>
    </nav>
    <div class="main-container">
      <router-view/>
    </div>
    <footer class="footer">
      <div class="container text-center">
        <span>YTMeter &copy; 2025</span>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
:root {
  /* Cupertino inspired colors */
  --primary-color: #007aff; /* iOS blue */
  --primary-dark: #0062cc;
  --primary-light: #b4d9ff;
  --secondary-color: #34c759; /* iOS green */
  --text-color: #000000;
  --text-secondary: #8e8e93;
  --background-color: #f2f2f7; /* iOS light gray background */
  --surface-color: #ffffff;
  --border-color: #d1d1d6; /* iOS light border */
  --shadow-color: rgba(0, 0, 0, 0.05);
  
  /* Additional iOS-style colors */
  --ios-red: #ff3b30;
  --ios-orange: #ff9500;
  --ios-yellow: #ffcc00;
  --ios-teal: #5ac8fa;
  --ios-purple: #af52de;
}

body {
  background-color: var(--background-color);
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--text-color);
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.navbar {
  background-color: var(--surface-color);
  box-shadow: 0 1px 0 var(--border-color);
  padding: 1rem 0;
}

.navbar-brand {
  font-weight: 600;
  font-size: 1.5rem;
  color: var(--text-color);
}

.brand-text {
  letter-spacing: -0.5px;
}

.brand-highlight {
  color: var(--primary-color);
}

.main-container {
  flex: 1;
  padding: 2rem 0;
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}

.footer {
  background-color: var(--surface-color);
  padding: 1.5rem 0;
  color: var(--text-secondary);
  box-shadow: 0 -1px 0 var(--border-color);
  margin-top: auto;
}

/* Cupertino-style button */
.btn-primary {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  border-radius: 10px;
  font-weight: 500;
}

.btn-primary:hover {
  background-color: var(--primary-dark);
  border-color: var(--primary-dark);
}

.btn-outline-primary {
  color: var(--primary-color);
  border-color: var(--primary-color);
  border-radius: 10px;
  font-weight: 500;
}

.btn-outline-primary:hover {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

/* Cupertino-style card */
.card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 1px 5px var(--shadow-color);
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px var(--shadow-color);
}

/* Utility classes */
.rounded-ios {
  border-radius: 10px !important;
}

.shadow-ios {
  box-shadow: 0 1px 5px var(--shadow-color) !important;
}

/* iOS style form controls */
.form-control, .custom-select {
  border-radius: 10px;
  border: 1px solid var(--border-color);
  padding: 0.5rem 0.75rem;
}

.form-control:focus, .custom-select:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.25);
}
</style>
