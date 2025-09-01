import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'
import './index.css'
import axios from 'axios'

export const api = axios.create({
  baseURL: '/api',         // use relative path so browser uses the page's HTTPS
  withCredentials: true,   // keep cookies enabled
})

const app = createApp(App)
app.use(createPinia())
app.mount('#app')