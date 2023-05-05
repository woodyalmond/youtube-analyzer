
<template>
    <div class="container">
      <h1 class="mt-5">YouTube Analyzer</h1>
      <p class="lead">Enter your YouTube Data API key to start analyzing videos.</p>
      <b-form @submit.prevent="submitApiKey">
        <b-form-group
          label="YouTube Data API Key"
          label-for="apiKey"
        >
          <b-form-input
            id="apiKey"
            v-model="apiKey"
            required
            placeholder="Enter API Key"
          ></b-form-input>
        </b-form-group>
        <b-button type="submit" variant="primary">Submit</b-button>
      </b-form>
    </div>
  </template>
  
  <script>

  export default {
    data() {
      return {
        apiKey: ''
      }
    },
    methods: {
      submitApiKey() {
        this.$router.push({ name: 'Search', params: { apiKey: this.apiKey } })
      }
    }
  }
  
  </script>
  