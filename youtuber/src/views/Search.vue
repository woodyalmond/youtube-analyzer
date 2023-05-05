<template>
    <div class="container">
      <h1 class="mt-5">Search Videos</h1>
      <p class="lead">Enter your query to find videos and analyze their performance.</p>
      <b-form @submit.prevent="searchVideos">
        <b-form-group
          label="Search Query"
          label-for="query"
        >
          <b-form-input
            id="query"
            v-model="query"
            required
            placeholder="Enter query"
          ></b-form-input>
        </b-form-group>
        <b-button type="submit" variant="primary">Search</b-button>
      </b-form>
      <b-table
        v-if="videos.length"
        :items="videos"
        :fields="fields"
        class="mt-5"
        responsive
        bordered
        hover
        striped
      ></b-table>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  
  export default {
    data() {
      return {
        apiKey: this.$route.params.apiKey,
        query: '',
        videos: [],
        fields: [
          { key: 'thumbnail', label: 'Thumbnail', formatter: 'thumbnailFormatter' },
          { key: 'title', label: 'Title' },
          { key: 'description', label: 'Description' },
        { key: 'publishDate', label: 'Publish Date' },
        { key: 'channelTitle', label: 'Channel Title' },
        { key: 'viewCount', label: 'View Count' },
        { key: 'likeCount', label: 'Like Count' },
        { key: 'duration', label: 'Video Length' },
        { key: 'url', label: 'URL', formatter: 'urlFormatter' },
      ],
    }
  },
  methods: {
    async searchVideos() {
      try {
        const response = await axios.post('http://localhost:5000/search', {
          api_key: this.apiKey,
          query: this.query,
        })
        this.videos = response.data
      } catch (error) {
        console.error(error)
        alert('Error fetching video data. Please check your API key and query.')
      }
    },
    thumbnailFormatter(value) {
      return `<img src="${value}" alt="Thumbnail" width="120" height="90">`
    },
    urlFormatter(value, key, item) {
      return `<a href="https://www.youtube.com/watch?v=${item.id}" target="_blank" rel="noopener noreferrer">${value}</a>`
    },
  },
}
</script>

<style scoped>
table img {
  width: 120px;
  height: 90px;
}
</style>

  