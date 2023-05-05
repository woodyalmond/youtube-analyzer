import { createRouter, createWebHistory } from 'vue-router'
import Landing from '../views/Landing.vue'
import Search from '../views/Search.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: Landing
  },
  {
    path: '/search',
    name: 'Search',
    component: Search
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
