import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../main.js'
import { useEventsStore } from './useEventsStore'


export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const eventsStore = useEventsStore()

  function setUser(username) {
    user.value = username
  }

  function logout() {
    user.value = null
    eventsStore.clearEvents()
  }

  async function loadSession() {
    try {
      const res = await api.get('/session')
      if (res.data.logged_in) {
        setUser(res.data.username)
        return res.data.username
      } else {
        logout()
        return null
      }
    } catch {
      logout()
      return null
    }
  }

  return { user, setUser, logout, loadSession }
})