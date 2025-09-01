<template>
  <div class="min-h-screen px-4 py-6 sm:p-6 bg-gray-100 text-gray-900">
    <!-- Logged in banner -->
    <div v-if="user" class="flex justify-end mb-4 text-sm text-gray-700">
      Logged in as <span class="font-semibold ml-1 mr-2">{{ user }}</span> |
      <button @click="handleLogout" class="text-blue-600 hover:underline ml-2">Logout</button>
    </div>

    <!-- Main content -->
    <Login v-if="!user" />
    <Calendar v-else />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { api } from './main.js'
import { storeToRefs } from 'pinia'
import { useUserStore } from './store/useUserStore'
import Login from './components/Login.vue'
import Calendar from './components/Calendar.vue'

const userStore = useUserStore()
const { user } = storeToRefs(userStore)

onMounted(async () => {
  // await the result so you can inspect it
  const sessionUser = await userStore.loadSession()
  console.log('loadSession returned:', sessionUser)
  console.log('user ref value:', user.value)

  // navigate to /calendar if authenticated
  if (sessionUser) {
    if (window.location.pathname !== '/calendar') {
      window.location.replace('/calendar')
    }
  }
})

const handleLogout = async () => {
  try {
    await api.post('/logout', {})
  } catch (err) {
    console.error('Logout error:', err)
  }
  userStore.logout()
}
</script>
